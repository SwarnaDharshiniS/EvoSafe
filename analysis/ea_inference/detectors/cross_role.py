"""Cross-role detectors driven by local function summaries and registered callbacks."""

from __future__ import annotations

import ast

from .._ast_utils import _names
from .._context import (
    EAAnalysisContext,
    EADetector,
    ObservationCollector,
    RoleObservation,
    expand_population_aliases,
    mark_iterated_candidates,
)
from .._data_flow import DispatchKind
from .._model import EAConfidence, EARole


_REGISTERED_ROLE_TAGS = {
    "population": EARole.POPULATION,
    "initialize_population": EARole.POPULATION,
    "fitness": EARole.FITNESS_EVALUATION,
    "evaluate": EARole.FITNESS_EVALUATION,
    "evaluation": EARole.FITNESS_EVALUATION,
    "fitness_evaluation": EARole.FITNESS_EVALUATION,
    "objective": EARole.FITNESS_EVALUATION,
    "select": EARole.SELECTION,
    "selection": EARole.SELECTION,
    "parent_selection": EARole.SELECTION,
    "mutate": EARole.MUTATION,
    "mutation": EARole.MUTATION,
    "mate": EARole.CROSSOVER,
    "crossover": EARole.CROSSOVER,
    "recombine": EARole.CROSSOVER,
    "replace": EARole.REPLACEMENT,
    "replacement": EARole.REPLACEMENT,
    "survivor_selection": EARole.REPLACEMENT,
    "terminate": EARole.TERMINATION,
    "termination": EARole.TERMINATION,
    "stop": EARole.TERMINATION,
}
_BUILTIN_CALLBACK_ROLES = {
    "sorted": EARole.SELECTION,
    "min": EARole.SELECTION,
    "max": EARole.SELECTION,
    "filter": EARole.SELECTION,
}


class HelperSummaryDetector(EADetector):
    """Roles proven by local helper summaries at call sites receiving EA-linked arguments."""

    def detect(self, context: EAAnalysisContext) -> list[RoleObservation]:
        state = context.state
        found = ObservationCollector()
        for call in context.nodes:
            if not isinstance(call, ast.Call):
                continue
            summary = context.summaries.for_call(call)
            if summary is None:
                continue
            actuals = [set(_names(arg)) for arg in call.args]
            if not actuals:
                continue
            for summary_evidence in summary.role_evidence:
                role_name = summary_evidence.role.value
                parameter_indices = set(summary_evidence.parameter_indices)
                if summary_evidence.certainty == EAConfidence.LOW:
                    confidence = EAConfidence.LOW
                else:
                    confidence = EAConfidence.MEDIUM
                argument_names = set().union(*(
                    actuals[index] for index in parameter_indices if index < len(actuals)
                ))

                if role_name == EARole.MUTATION.value:
                    if not (argument_names & state.candidate_names):
                        continue
                    role = EARole.MUTATION
                elif role_name == EARole.FITNESS_EVALUATION.value:
                    if not (argument_names & state.candidate_names):
                        continue
                    role = EARole.FITNESS_EVALUATION
                elif role_name == EARole.SELECTION.value:
                    if not (argument_names & state.population_names):
                        continue
                    role = EARole.SELECTION
                elif role_name == EARole.CROSSOVER.value:
                    candidate_argument_count = sum(
                        bool(actuals[index] & state.candidate_names)
                        for index in parameter_indices if index < len(actuals)
                    )
                    if candidate_argument_count < 2:
                        continue
                    role = EARole.CROSSOVER
                elif role_name == EARole.REPLACEMENT.value:
                    if not (argument_names & state.population_names):
                        continue
                    role = EARole.REPLACEMENT
                else:
                    continue

                found.add(
                    role,
                    context.evidence(
                        f"helper_{role_name}",
                        summary_evidence.description,
                        summary_evidence.node,
                    ),
                    confidence,
                )
                found.add(
                    role,
                    context.evidence(
                        "helper_call_site",
                        f"Local helper {summary.name!r} receives values structurally linked to the EA role inputs.",
                        call,
                    ),
                    confidence,
                )

                assigned = context.assigned_names(call)
                if role == EARole.FITNESS_EVALUATION:
                    state.fitness_names.update(assigned)
                elif role == EARole.SELECTION:
                    state.selection_names.update(assigned)
                elif role == EARole.MUTATION:
                    state.offspring_names.update(assigned)
        return found.observations()


class RegisteredDispatchDetector(EADetector):
    """Roles from statically paired callback registrations and their dispatch sites."""

    def detect(self, context: EAAnalysisContext) -> list[RoleObservation]:
        state = context.state
        found = ObservationCollector()
        for dispatch in context.data_flow.dispatches:
            registration = dispatch.registration
            if dispatch.ambiguous or registration.ambiguous:
                continue
            role = _REGISTERED_ROLE_TAGS.get(registration.key.strip().lower().replace("-", "_").replace(" ", "_"))
            explicit_role_tag = role is not None
            summary = (
                context.summaries.for_scope(registration.callable_scope)
                if registration.callable_scope is not None
                else None
            )
            builtin_role = None
            if (
                summary is None
                and isinstance(registration.callable_node, ast.Name)
                and registration.callable_scope is None
            ):
                builtin_role = _BUILTIN_CALLBACK_ROLES.get(registration.callable_node.id)
                if builtin_role is None or role not in (None, builtin_role):
                    continue
                role = builtin_role
            summary_roles = {
                item.role: item for item in summary.role_evidence
            } if summary is not None else {}
            if role is None:
                role = next(iter(summary_roles), None)
            if role is None:
                continue
            if summary is not None and role not in summary_roles and role != EARole.POPULATION:
                # A local callback whose visible body contradicts the registry
                # role is not classified based on its registration key alone.
                continue

            argument_names = [set(_names(argument)) for argument in dispatch.arguments]
            flat_names = set().union(*argument_names) if argument_names else set()
            assigned = context.assigned_names(dispatch.call)
            confidence = EAConfidence.MEDIUM
            evidence_item = summary_roles.get(role)
            if evidence_item is not None and evidence_item.certainty == EAConfidence.LOW:
                confidence = EAConfidence.LOW

            loop = context.in_loop(dispatch.call)
            if (
                role in {EARole.FITNESS_EVALUATION, EARole.MUTATION, EARole.CROSSOVER}
                and loop is not None
                and isinstance(loop.node, (ast.For, ast.AsyncFor))
                and any(set(loop.target_names) & names for names in argument_names)
            ):
                state.candidate_names.update(loop.target_names)
                iterable_names = _names(loop.node.iter)
                for name in iterable_names:
                    state.population_names.update(context.data_flow.alias_group(
                        name,
                        scope=dispatch.scope,
                        line=getattr(loop.node, "lineno", None),
                    ))
                found.add(
                    EARole.POPULATION,
                    context.evidence(
                        "registered_candidate_iteration",
                        "A registered EA operation consumes a loop element drawn from a collection.",
                        loop.node,
                    ),
                    EAConfidence.MEDIUM,
                )

            if role == EARole.POPULATION:
                if not assigned:
                    continue
                state.population_names.update(assigned)
                for name in assigned:
                    state.population_names.update(context.data_flow.alias_group(
                        name,
                        scope=dispatch.scope,
                        line=getattr(dispatch.call, "lineno", None),
                    ))
                found.add(
                    role,
                    context.evidence("registered_role", "A statically paired registration and invocation declares a population-producing role.", registration.node),
                    confidence,
                )
                found.add(
                    role,
                    context.evidence("registered_dispatch", "The registered callable is invoked and its result is assigned to a collection variable.", dispatch.call),
                    confidence,
                )
                expand_population_aliases(context)
                mark_iterated_candidates(context)
                continue

            if role == EARole.FITNESS_EVALUATION:
                candidate_input = bool(flat_names & state.candidate_names)
                mapped_population = dispatch.kind == DispatchKind.HIGHER_ORDER_MAP and bool(flat_names & state.population_names)
                if not (candidate_input or mapped_population):
                    continue
            elif role == EARole.SELECTION:
                if not (flat_names & state.population_names):
                    continue
            elif role == EARole.MUTATION:
                if not (flat_names & state.candidate_names):
                    continue
            elif role == EARole.CROSSOVER:
                candidate_arguments = sum(bool(names & state.candidate_names) for names in argument_names)
                if candidate_arguments < 2:
                    continue
            elif role == EARole.REPLACEMENT:
                if not (flat_names & state.population_names):
                    continue
            elif role == EARole.TERMINATION:
                loop = context.in_loop(dispatch.call)
                if loop is None or not isinstance(loop.node, ast.While):
                    continue

            found.add(
                role,
                context.evidence(
                    "registered_role",
                    (
                        f"Registered callable {registration.callable_name!r} is a builtin ranking/filtering function applied to the population."
                        if builtin_role is not None
                        else f"Registration key {registration.key!r} explicitly labels the callback as {role.value}."
                        if explicit_role_tag
                        else f"The registered callback body provides structural evidence for {role.value}."
                    ),
                    registration.node,
                ),
                confidence,
            )
            found.add(
                role,
                context.evidence(
                    "registered_dispatch",
                    f"The registered callable is dispatched with arguments linked to the {role.value} role.",
                    dispatch.call,
                ),
                confidence,
            )
            found.add(
                role,
                context.evidence(
                    "registered_callable_reference",
                    f"This reference resolves to the callable registered under {registration.key!r}.",
                    dispatch.callable_reference,
                ),
                confidence,
            )
            if evidence_item is not None:
                found.add(
                    role,
                    context.evidence(
                        "registered_callback_summary",
                        evidence_item.description,
                        evidence_item.node,
                    ),
                    confidence,
                )

            if role == EARole.FITNESS_EVALUATION:
                state.fitness_names.update(assigned)
            elif role == EARole.SELECTION:
                state.selection_names.update(assigned)
                state.population_names.update(assigned)
                expand_population_aliases(context)
                mark_iterated_candidates(context)
            elif role in {EARole.MUTATION, EARole.CROSSOVER}:
                state.offspring_names.update(assigned)
        return found.observations()
