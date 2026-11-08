"""Conservative collection and candidate lineage facts for EA inference."""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, TypeAlias

from ._data_flow import FlowLocation, IntraProceduralDataFlow, ScopedName
from ._model import EAConfidence, EARole


CFGBlockLookup: TypeAlias = Callable[[ast.AST], tuple[str, ...]]

_CANDIDATE_TRANSFORM_ROLES = frozenset({EARole.FITNESS_EVALUATION, EARole.MUTATION, EARole.CROSSOVER})


class CollectionOperation(str, Enum):
    CONSTRUCT = "construct"
    ALIAS = "alias"
    COPY = "copy"
    ITERATE = "iterate"
    INDEX = "index"
    SLICE = "slice"
    COMPREHENSION = "comprehension"
    APPEND = "append"
    EXTEND = "extend"
    INSERT = "insert"
    MUTATE = "mutate"
    REASSIGN = "reassign"
    REPLACE = "replace"
    HELPER_RETURN = "helper_return"


class CandidateRelation(str, Enum):
    ELEMENT_OF_COLLECTION = "element_of_collection"
    ALIAS_OF_CANDIDATE = "alias_of_candidate"
    COPY_OF_CANDIDATE = "copy_of_candidate"
    DERIVED_FROM_CANDIDATE = "derived_from_candidate"
    DERIVED_FROM_TWO_CANDIDATES = "derived_from_two_candidates"
    MUTATED_CANDIDATE = "mutated_candidate"
    RETURNED_CANDIDATE = "returned_candidate"
    INSERTED_INTO_COLLECTION = "inserted_into_collection"
    REPLACED_IN_COLLECTION = "replaced_in_collection"
    SELECTED_FROM_COLLECTION = "selected_from_collection"
    COMPUTED_FROM_CANDIDATE = "computed_from_candidate"


@dataclass(frozen=True)
class CollectionFact:
    collection: str
    operation: CollectionOperation
    location: FlowLocation
    source: str | None = None
    destination: str | None = None
    evidence: str = ""
    confidence: EAConfidence = EAConfidence.MEDIUM
    cfg_blocks: tuple[str, ...] = ()
    node: ast.AST = field(default_factory=ast.AST, compare=False, repr=False)


@dataclass(frozen=True)
class CandidateFact:
    candidate: str
    source_collection: str | None
    relation: CandidateRelation
    location: FlowLocation
    source_candidates: tuple[str, ...] = ()
    evidence: str = ""
    confidence: EAConfidence = EAConfidence.MEDIUM
    cfg_blocks: tuple[str, ...] = ()
    node: ast.AST = field(default_factory=ast.AST, compare=False, repr=False)


@dataclass(frozen=True)
class CandidateLineageFact:
    source_candidates: tuple[str, ...]
    destination: str
    relation: CandidateRelation
    location: FlowLocation
    source_collection: str | None = None
    evidence: str = ""
    confidence: EAConfidence = EAConfidence.MEDIUM
    cfg_blocks: tuple[str, ...] = ()
    node: ast.AST = field(default_factory=ast.AST, compare=False, repr=False)


@dataclass(frozen=True)
class CandidateCollectionFacts:
    collections: tuple[CollectionFact, ...] = ()
    candidates: tuple[CandidateFact, ...] = ()
    lineage: tuple[CandidateLineageFact, ...] = ()

    @property
    def collection_names(self) -> set[str]:
        return {fact.collection.rsplit(":", 1)[-1] for fact in self.collections}

    @property
    def candidate_names(self) -> set[str]:
        return {fact.candidate.rsplit(":", 1)[-1].split("@", 1)[0] for fact in self.candidates}


def _names(node: ast.AST | None) -> set[str]:
    return {item.id for item in ast.walk(node) if isinstance(item, ast.Name)} if node else set()


def _targets(node: ast.AST) -> set[str]:
    if isinstance(node, ast.Name):
        return {node.id}
    if isinstance(node, (ast.Tuple, ast.List)):
        return set().union(*(_targets(item) for item in node.elts)) if node.elts else set()
    return set()


def _root(node: ast.AST) -> str | None:
    while isinstance(node, (ast.Attribute, ast.Subscript)):
        node = node.value
    return node.id if isinstance(node, ast.Name) else None


def _copy_source(node: ast.AST) -> ast.AST | None:
    if isinstance(node, ast.Call):
        func = node.func
        if isinstance(func, ast.Attribute) and func.attr in {"copy", "clone", "deepcopy"} and not node.args:
            return func.value
        if isinstance(func, ast.Name) and func.id in {"copy", "deepcopy", "list", "tuple"} and len(node.args) == 1:
            return node.args[0]
    return None


class CandidateCollectionAnalyzer:
    """Build local, source-located lineage without assigning EA semantics to collections."""

    def __init__(
        self,
        tree: ast.AST,
        data_flow: IntraProceduralDataFlow,
        cfg_refs: CFGBlockLookup | None = None,
    ) -> None:
        self.tree = tree
        self.data_flow = data_flow
        self.cfg_refs: CFGBlockLookup = cfg_refs or (lambda _node: ())
        self.facts = CandidateCollectionFacts()
        self._collection_facts: list[CollectionFact] = []
        self._candidate_facts: list[CandidateFact] = []
        self._lineage_facts: list[CandidateLineageFact] = []
        self.parent = {
            child: node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)
        }
        self._collections: dict[ScopedName, str] = {}
        self._candidates: dict[ScopedName, set[str]] = {}
        self._candidate_collections: dict[str, str] = {}
        self._ambiguous_bindings = self._find_ambiguous_bindings()
        self._cleared_collections: set[ScopedName] = set()
        self._build()
        self.facts = CandidateCollectionFacts(
            tuple(self._collection_facts), tuple(self._candidate_facts), tuple(self._lineage_facts),
        )

    def _find_ambiguous_bindings(self) -> set[ScopedName]:
        ambiguous: set[ScopedName] = set()
        for node in ast.walk(self.tree):
            if not isinstance(node, ast.If):
                continue
            left = set().union(*(
                _targets(target)
                for item in ast.walk(ast.Module(body=node.body, type_ignores=[]))
                if isinstance(item, (ast.Assign, ast.AnnAssign, ast.AugAssign))
                for target in (item.targets if isinstance(item, ast.Assign) else [item.target])
            )) if node.body else set()
            right = set().union(*(
                _targets(target)
                for item in ast.walk(ast.Module(body=node.orelse, type_ignores=[]))
                if isinstance(item, (ast.Assign, ast.AnnAssign, ast.AugAssign))
                for target in (item.targets if isinstance(item, ast.Assign) else [item.target])
            )) if node.orelse else set()
            ambiguous.update(ScopedName(self._scope(node), name) for name in left & right)
        return ambiguous

    def _scope(self, node: ast.AST) -> str:
        return self.data_flow.scope_for(node)

    def _id(self, name: str, scope: str) -> str:
        return f"{scope}:{name}"

    def _emit_collection(
        self, node: ast.AST, name: str, operation: CollectionOperation,
        source: str | None = None, destination: str | None = None,
        evidence: str = "",
    ) -> None:
        scope = self._scope(node)
        identity = self._id(name, scope)
        fact = CollectionFact(
            collection=identity, operation=operation, source=source,
            destination=destination, location=self._location(node), evidence=evidence,
            confidence=EAConfidence.MEDIUM, cfg_blocks=self.cfg_refs(node), node=node,
        )
        if fact not in self._collection_facts:
            self._collection_facts.append(fact)
        self._collections[ScopedName(scope, name)] = identity

    def _emit_candidate(
        self, node: ast.AST, candidate: str, collection: str | None,
        relation: CandidateRelation, sources: tuple[str, ...], evidence: str,
    ) -> None:
        fact = CandidateFact(
            candidate=candidate, source_collection=collection, relation=relation,
            source_candidates=sources, location=self._location(node), evidence=evidence,
            confidence=EAConfidence.MEDIUM, cfg_blocks=self.cfg_refs(node), node=node,
        )
        if fact not in self._candidate_facts:
            self._candidate_facts.append(fact)
        for source in sources:
            if collection:
                self._candidate_collections.setdefault(source, collection)

    def _emit_lineage(
        self, node: ast.AST, destination: str, relation: CandidateRelation,
        sources: set[str], collection: str | None, evidence: str,
    ) -> None:
        ordered = tuple(sorted(sources))
        fact = CandidateLineageFact(
            source_candidates=ordered, destination=destination, relation=relation,
            source_collection=collection, location=self._location(node), evidence=evidence,
            confidence=EAConfidence.MEDIUM, cfg_blocks=self.cfg_refs(node), node=node,
        )
        if ordered and fact not in self._lineage_facts:
            self._lineage_facts.append(fact)

    def _expr_candidates(self, node: ast.AST | None, scope: str) -> set[str]:
        if node is None:
            return set()
        if isinstance(node, ast.Name):
            return set(self._candidates.get(ScopedName(scope, node.id), set()))
        if isinstance(node, ast.Subscript):
            root = _root(node.value)
            if root is None:
                return self._expr_candidates(node.value, scope)
            collection = self._collections.get(ScopedName(scope, root))
            if collection is None:
                return self._expr_candidates(node.value, scope)
            if isinstance(node.slice, ast.Slice):
                self._emit_collection(node, root, CollectionOperation.SLICE, collection,
                                      evidence="A slice is derived from a known collection.")
                return self._expr_candidates(node.value, scope)
            index = node.slice.value if isinstance(node.slice, ast.Index) else node.slice
            if isinstance(index, ast.Constant) and isinstance(index.value, (int, str)):
                candidate = f"{collection}[{index.value!r}]"
            else:
                candidate = f"{collection}[?]"
            self._emit_collection(node, root, CollectionOperation.INDEX, collection,
                                  evidence="An indexed value is read from a known collection.")
            self._emit_candidate(
                node, candidate, collection, CandidateRelation.ELEMENT_OF_COLLECTION, (),
                "Indexed value is structurally derived from a collection element.",
            )
            self._candidate_collections[candidate] = collection
            return {candidate}
        if isinstance(node, ast.Call):
            copied = _copy_source(node)
            if copied is not None:
                return self._expr_candidates(copied, scope)
            summary = self.data_flow.summary_for_call(node, scope)
            if summary is None or summary.dynamic_behavior or summary.unresolved_calls or not summary.return_resolved:
                return set()
            dependent_indices = set(summary.return_dependent_parameters | summary.return_alias_parameters)
            dependent_indices.update(
                index
                for evidence in summary.role_evidence
                if evidence.certainty != EAConfidence.LOW
                and evidence.role in _CANDIDATE_TRANSFORM_ROLES
                for index in evidence.parameter_indices
            )
            actuals = [node.args[index] if index < len(node.args) else next(
                (item.value for item in node.keywords if item.arg == parameter), None
            ) for index, parameter in enumerate(summary.parameters)]
            return set().union(*(
                self._expr_candidates(actuals[index], scope)
                for index in dependent_indices
                if index < len(actuals) and actuals[index] is not None
            )) if dependent_indices else set()
        if isinstance(node, ast.IfExp):
            left = self._expr_candidates(node.body, scope)
            right = self._expr_candidates(node.orelse, scope)
            return left if left == right else set()
        if isinstance(node, (ast.ListComp, ast.SetComp, ast.Tuple)):
            return self._expr_candidates(node.elt, scope) if isinstance(node, (ast.ListComp, ast.SetComp)) else set().union(*(
                self._expr_candidates(item, scope) for item in node.elts
            ))
        if isinstance(node, ast.Lambda):
            return set()
        return set().union(*(self._expr_candidates(child, scope) for child in ast.iter_child_nodes(node) if isinstance(child, ast.expr)))

    def _location(self, node: ast.AST) -> FlowLocation:
        return FlowLocation(
            getattr(node, "lineno", None), getattr(node, "col_offset", None),
            getattr(node, "end_lineno", None), getattr(node, "end_col_offset", None),
        )

    def _build(self) -> None:
        for node in ast.walk(self.tree):
            scope = self._scope(node)
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                value = node.value
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                for name in sorted(set().union(*(_targets(target) for target in targets))):
                    if isinstance(value, (ast.List, ast.Tuple, ast.Set, ast.Dict, ast.ListComp, ast.SetComp, ast.DictComp)):
                        operation = CollectionOperation.COMPREHENSION if isinstance(value, (ast.ListComp, ast.SetComp, ast.DictComp)) else CollectionOperation.CONSTRUCT
                        self._emit_collection(node, name, operation, evidence="A collection value is constructed in source.")
                    elif isinstance(value, ast.Call) and isinstance(value.func, ast.Name) and value.func.id in {"list", "tuple", "set", "dict"}:
                        self._emit_collection(node, name, CollectionOperation.CONSTRUCT, evidence="A built-in collection constructor is called.")
            elif isinstance(node, (ast.For, ast.AsyncFor)) and isinstance(node.iter, ast.Name):
                self._emit_collection(node, node.iter.id, CollectionOperation.ITERATE,
                                      evidence="A collection binding is iterated.")
            elif isinstance(node, ast.Subscript) and _root(node):
                root = _root(node)
                self._emit_collection(node, root, CollectionOperation.SLICE if isinstance(node.slice, ast.Slice) else CollectionOperation.INDEX,
                                      evidence="A collection is accessed by slice or index.")

        for node in ast.walk(self.tree):
            if isinstance(node, (ast.For, ast.AsyncFor)) and isinstance(node.iter, ast.Name):
                scope = self._scope(node)
                coll = self._collections.get(ScopedName(scope, node.iter.id))
                if coll is None:
                    self._emit_collection(node, node.iter.id, CollectionOperation.ITERATE,
                                          evidence="A collection binding is iterated.")
                    coll = self._collections[ScopedName(scope, node.iter.id)]
                for name in sorted(_targets(node.target)):
                    candidate = f"{scope}:{name}@{getattr(node, 'lineno', 0)}"
                    self._candidates[ScopedName(scope, name)] = {candidate}
                    self._candidate_collections[candidate] = coll
                    self._emit_candidate(node, candidate, coll, CandidateRelation.ELEMENT_OF_COLLECTION, (),
                                         "Loop target represents an element of the iterated collection.")

        for node in sorted(ast.walk(self.tree), key=lambda item: (getattr(item, "lineno", 0), getattr(item, "col_offset", 0))):
            scope = self._scope(node)
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                value = node.value
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                names = set().union(*(_targets(target) for target in targets))
                for name in sorted(names):
                    if ScopedName(scope, name) in self._ambiguous_bindings:
                        continue
                    previous_collection = self._collections.get(ScopedName(scope, name))
                    if isinstance(value, (ast.List, ast.Tuple, ast.Set, ast.Dict, ast.ListComp, ast.SetComp, ast.DictComp)):
                        op = CollectionOperation.COMPREHENSION if isinstance(value, (ast.ListComp, ast.SetComp, ast.DictComp)) else CollectionOperation.CONSTRUCT
                        self._emit_collection(node, name, op, evidence="A collection value is constructed in source.")
                    elif isinstance(value, ast.Name) and ScopedName(scope, value.id) in self._collections:
                        source = self._collections[ScopedName(scope, value.id)]
                        self._emit_collection(node, name, CollectionOperation.ALIAS, source,
                                              evidence="Assignment preserves a known collection binding.")
                    elif isinstance(value, ast.Call) and _copy_source(value) is not None:
                        source_root = _root(_copy_source(value))
                        source = self._collections.get(ScopedName(scope, source_root)) if source_root else None
                        if source:
                            self._emit_collection(node, name, CollectionOperation.COPY, source,
                                                  evidence="A known collection is copied using an explicit copy operation.")
                    current_collection = self._collections.get(ScopedName(scope, name))
                    assigned_collection = (
                        self._collections.get(ScopedName(scope, value.id)) if isinstance(value, ast.Name) else current_collection
                    )
                    if previous_collection and assigned_collection and assigned_collection != previous_collection:
                        self._emit_collection(node, name, CollectionOperation.REASSIGN,
                                              source=previous_collection, destination=assigned_collection,
                                              evidence="A collection binding is rebound to a different known collection.")

                    sources = self._expr_candidates(value, scope)
                    if previous_collection and sources and not isinstance(value, (ast.List, ast.Tuple, ast.Set, ast.Dict, ast.ListComp, ast.SetComp, ast.DictComp)):
                        self._emit_collection(node, name, CollectionOperation.REPLACE,
                                              source=previous_collection, destination=previous_collection,
                                              evidence="An existing collection binding is rebuilt from candidate-derived values.")
                        self._emit_lineage(node, previous_collection, CandidateRelation.REPLACED_IN_COLLECTION,
                                           sources, previous_collection,
                                           "An existing collection is rebound to candidate-derived contents.")
                    if isinstance(value, ast.Subscript) and isinstance(value.slice, ast.Slice):
                        source_root = _root(value.value)
                        source_collection = self._collections.get(ScopedName(scope, source_root)) if source_root else None
                        if source_collection:
                            self._emit_candidate(node, self._id(name, scope), source_collection,
                                                 CandidateRelation.SELECTED_FROM_COLLECTION, (),
                                                 "A slice result is a subset view of a known collection.")
                            self._emit_lineage(node, self._id(name, scope), CandidateRelation.SELECTED_FROM_COLLECTION,
                                               {source_collection}, source_collection,
                                               "A slice result remains linked to its source collection.")
                    if isinstance(value, ast.Call):
                        summary = self.data_flow.summary_for_call(value, scope)
                        if summary and summary.return_resolved:
                            function = self.data_flow.functions.get(summary.scope)
                            if function and any(
                                isinstance(item, ast.Return)
                                and isinstance(item.value, (ast.List, ast.Tuple, ast.Set, ast.Dict, ast.ListComp, ast.SetComp, ast.DictComp))
                                for item in ast.walk(function)
                            ):
                                self._emit_collection(node, name, CollectionOperation.HELPER_RETURN,
                                                      evidence="A locally resolved helper returns a collection expression.")
                    if isinstance(value, (ast.ListComp, ast.SetComp)) and (
                        any(generator.ifs for generator in value.generators)
                        or isinstance(value.elt, ast.Subscript)
                    ):
                        indexed_root = next((
                            root for root in (
                                _root(item.value) for item in ast.walk(value.elt) if isinstance(item, ast.Subscript)
                            )
                            if root is not None and ScopedName(scope, root) in self._collections
                        ), None)
                        source_collection = self._collections.get(ScopedName(scope, indexed_root)) if indexed_root else None
                        if source_collection is None:
                            source_collection = next((
                                self._collections.get(ScopedName(scope, generator.iter.id))
                                for generator in value.generators
                                if isinstance(generator.iter, ast.Name)
                                and ScopedName(scope, generator.iter.id) in self._collections
                            ), None)
                        if source_collection:
                            self._emit_candidate(node, self._id(name, scope), source_collection,
                                                 CandidateRelation.SELECTED_FROM_COLLECTION, tuple(sorted(sources)),
                                                 "Comprehension output is derived from elements of a known collection.")
                            self._emit_lineage(node, self._id(name, scope), CandidateRelation.SELECTED_FROM_COLLECTION,
                                               sources or {source_collection}, source_collection,
                                               "Comprehension derives a collection from a known source collection.")
                    if isinstance(value, ast.Call):
                        called = value.func.id if isinstance(value.func, ast.Name) else value.func.attr if isinstance(value.func, ast.Attribute) else ""
                        if called in {"sorted", "filter", "sample", "choices", "choice", "nlargest", "nsmallest", "argmin", "argmax"}:
                            source_name = next((
                                ref for ref in sorted(_names(value)) if ScopedName(scope, ref) in self._collections
                            ), None)
                            if source_name:
                                source_collection = self._collections[ScopedName(scope, source_name)]
                                self._emit_candidate(node, self._id(name, scope), source_collection,
                                                     CandidateRelation.SELECTED_FROM_COLLECTION, tuple(sorted(sources)),
                                                     "Selection operation returns values from a known collection.")
                                self._emit_lineage(node, self._id(name, scope), CandidateRelation.SELECTED_FROM_COLLECTION,
                                                   sources or {source_collection}, source_collection,
                                                   "Selection operation derives output from a known collection.")
                    if not sources:
                        continue
                    dest = self._id(name, scope)
                    target_is_copy = isinstance(value, ast.Call) and _copy_source(value) is not None
                    relation = CandidateRelation.COPY_OF_CANDIDATE if target_is_copy else CandidateRelation.ALIAS_OF_CANDIDATE if isinstance(value, ast.Name) else CandidateRelation.DERIVED_FROM_CANDIDATE
                    collection = next((self._candidate_collections.get(item) for item in sorted(sources) if item in self._candidate_collections), None)
                    self._candidates[ScopedName(scope, name)] = set(sources)
                    self._emit_candidate(node, dest, collection, relation, tuple(sorted(sources)),
                                         "Assignment preserves or derives candidate lineage from its value.")
                    self._emit_lineage(node, dest, relation, sources, collection,
                                       "Candidate value is linked to its statically tracked source.")
                    if isinstance(value, ast.Call):
                        self._emit_lineage(node, dest, CandidateRelation.COMPUTED_FROM_CANDIDATE, sources, collection,
                                           "A locally resolved call result depends on candidate-derived input.")
                    if len(sources) >= 2:
                        self._emit_lineage(node, dest, CandidateRelation.DERIVED_FROM_TWO_CANDIDATES, sources, collection,
                                           "One output expression depends on two distinct candidate-derived inputs.")

            elif isinstance(node, (ast.AugAssign, ast.Expr)):
                pass

            if isinstance(node, ast.Subscript):
                root = _root(node.value)
                if root and isinstance(node.slice, ast.Slice) and ScopedName(scope, root) in self._collections:
                    self._emit_collection(node, root, CollectionOperation.SLICE,
                                          self._collections[ScopedName(scope, root)], evidence="A slice is derived from a known collection.")

            if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                for target in targets:
                    if not isinstance(target, (ast.Subscript, ast.Attribute)):
                        continue
                    root = _root(target)
                    if root is None:
                        continue
                    source_candidates = self._candidates.get(ScopedName(scope, root), set())
                    if source_candidates:
                        candidate = self._id(root, scope)
                        self._emit_candidate(node, candidate, next((self._candidate_collections.get(c) for c in sorted(source_candidates)), None),
                                             CandidateRelation.MUTATED_CANDIDATE, tuple(sorted(source_candidates)),
                                             "A write targets an object with candidate lineage.")
                        self._emit_lineage(node, candidate, CandidateRelation.MUTATED_CANDIDATE, source_candidates,
                                           self._candidate_collections.get(next(iter(sorted(source_candidates)))),
                                           "A candidate-derived object is modified at this write.")
                    elif isinstance(target, ast.Subscript) and isinstance(target.slice, ast.Slice) and ScopedName(scope, root) in self._collections:
                        self._emit_collection(node, root, CollectionOperation.REPLACE,
                                              evidence="A slice assignment replaces collection contents.")
                        value_sources = self._expr_candidates(getattr(node, "value", None), scope)
                        if value_sources:
                            self._emit_lineage(node, self._id(root, scope), CandidateRelation.REPLACED_IN_COLLECTION,
                                               value_sources, self._collections[ScopedName(scope, root)],
                                               "Collection contents are replaced with candidate-derived values.")

                    if isinstance(target, ast.Subscript) and ScopedName(scope, root) in self._collections:
                        source_candidates = self._expr_candidates(getattr(node, "value", None), scope)
                        if source_candidates:
                            self._emit_lineage(node, self._id(root, scope), CandidateRelation.REPLACED_IN_COLLECTION,
                                               source_candidates, self._collections[ScopedName(scope, root)],
                                               "An indexed collection element is replaced by a candidate-derived value.")

            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                receiver = _root(node.func.value)
                if receiver is None:
                    continue
                candidate_sources = self._candidates.get(ScopedName(scope, receiver), set())
                if candidate_sources and node.func.attr in {"append", "extend", "insert", "pop", "remove", "clear", "reverse", "sort"}:
                    candidate_id = self._id(receiver, scope)
                    self._emit_lineage(node, candidate_id, CandidateRelation.MUTATED_CANDIDATE,
                                       candidate_sources, self._candidate_collections.get(next(iter(sorted(candidate_sources)))),
                                       "A candidate-derived object is modified by an in-place container operation.")
                if ScopedName(scope, receiver) not in self._collections:
                    continue
                operation = {
                    "append": CollectionOperation.APPEND,
                    "extend": CollectionOperation.EXTEND,
                    "insert": CollectionOperation.INSERT,
                    "clear": CollectionOperation.MUTATE,
                    "remove": CollectionOperation.MUTATE,
                    "pop": CollectionOperation.MUTATE,
                }.get(node.func.attr)
                if operation:
                    self._emit_collection(node, receiver, operation,
                                          evidence=f"Collection method {node.func.attr} changes the collection.")
                    if node.func.attr == "clear":
                        self._cleared_collections.add(ScopedName(scope, receiver))
                    sources = set().union(*(self._expr_candidates(arg, scope) for arg in node.args)) if node.args else set()
                    if sources:
                        self._emit_lineage(node, self._id(receiver, scope), CandidateRelation.INSERTED_INTO_COLLECTION,
                                           sources, self._collections[ScopedName(scope, receiver)],
                                           "Candidate-derived value is inserted into a known collection.")
                        if ScopedName(scope, receiver) in self._cleared_collections:
                            self._emit_collection(node, receiver, CollectionOperation.REPLACE,
                                                  evidence="A cleared collection is repopulated with candidate-derived values.")
                            self._emit_lineage(node, self._id(receiver, scope), CandidateRelation.REPLACED_IN_COLLECTION,
                                               sources, self._collections[ScopedName(scope, receiver)],
                                               "A cleared collection is replaced by candidate-derived values.")

            if isinstance(node, ast.Return) and node.value is not None:
                sources = self._expr_candidates(node.value, scope)
                if sources:
                    self._emit_lineage(node, f"{scope}:return", CandidateRelation.RETURNED_CANDIDATE,
                                       sources, next((self._candidate_collections.get(c) for c in sorted(sources)), None),
                                       "A candidate-derived value is returned by a local function.")

        self._collection_facts.sort(key=lambda item: (item.location.line or 0, item.location.col or 0, item.operation.value, item.collection))
        self._candidate_facts.sort(key=lambda item: (item.location.line or 0, item.location.col or 0, item.relation.value, item.candidate))
        self._lineage_facts.sort(key=lambda item: (item.location.line or 0, item.location.col or 0, item.relation.value, item.destination))