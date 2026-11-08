"""Tests for analysis.safety_ir.safety_ir_builder."""

import json
import sys
import textwrap
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from analysis.safety_ir import build_safety_ir_from_source, safety_ir_to_json


def ir_from(code: str, *, include_ea: bool = False):
    return build_safety_ir_from_source(
        textwrap.dedent(code),
        source_name="<test>",
        timestamp="2026-05-18T00:00:00Z",
        analysis_version="2026.05",
        include_ea=include_ea,
    )


class TestRequiredNodeTypes(unittest.TestCase):

    def test_required_node_types_present(self):
        ir = ir_from("""
            import os
            def run(x):
                while True:
                    os.system(x)
            run(input())
        """)
        d = ir.to_dict()

        self.assertEqual(d["node_type"], "ManifestRoot")
        self.assertTrue(any(n["node_type"] == "FunctionNode" for n in d["nodes"]["functions"]))
        self.assertTrue(any(n["node_type"] == "LoopNode" for n in d["nodes"]["loops"]))
        self.assertTrue(any(n["node_type"] == "CapabilityNode" for n in d["nodes"]["capabilities"]))
        self.assertTrue(any(n["node_type"] == "CFGBlockNode" for n in d["nodes"]["cfg_blocks"]))
        self.assertTrue(any(e["node_type"] == "TaintFlowEdge" for e in d["edges"]["taint_flows"]))


class TestSourceReferences(unittest.TestCase):

    def test_function_and_loop_line_refs(self):
        ir = ir_from("""
            def f(n):
                while n > 0:
                    n -= 1
                return n
        """)
        d = ir.to_dict()

        fn = d["nodes"]["functions"][0]
        lp = d["nodes"]["loops"][0]
        self.assertEqual(fn["source"]["line"], 2)
        self.assertEqual(lp["source"]["line"], 3)

    def test_capability_line_refs(self):
        ir = ir_from("""
            import os
            os.system('ls')
        """)
        d = ir.to_dict()
        caps = d["nodes"]["capabilities"]
        self.assertTrue(any(c["source"]["line"] == 3 for c in caps))


class TestGraphRelationships(unittest.TestCase):

    def test_graph_edges_present(self):
        ir = ir_from("""
            import os
            def g(x):
                os.system(x)
            g(input())
        """)
        d = ir.to_dict()
        graph = d["edges"]["graph"]
        self.assertTrue(len(graph) > 0)
        self.assertTrue(any(e["edge_type"] in {"contains", "observes", "cfg_next"} for e in graph))

    def test_taint_flow_edge_links_to_nodes(self):
        ir = ir_from("""
            import os
            def g():
                cmd = input()
                os.system(cmd)
            g()
        """)
        d = ir.to_dict()
        flow = d["edges"]["taint_flows"]
        self.assertTrue(len(flow) >= 1)
        self.assertIn("from", flow[0])
        self.assertIn("to", flow[0])


class TestDeterministicSerialization(unittest.TestCase):

    def test_same_input_same_json(self):
        code = """
            def f(x):
                for i in range(3):
                    x += i
                return x
        """
        ir1 = ir_from(code)
        ir2 = ir_from(code)

        j1 = safety_ir_to_json(ir1, indent=2)
        j2 = safety_ir_to_json(ir2, indent=2)
        self.assertEqual(j1, j2)

    def test_json_is_machine_readable(self):
        ir = ir_from("x = 1")
        raw = safety_ir_to_json(ir)
        obj = json.loads(raw)
        self.assertEqual(obj["node_type"], "ManifestRoot")
        self.assertIn("nodes", obj)
        self.assertIn("edges", obj)


class TestScopeModeling(unittest.TestCase):

    def test_ir_declares_non_semantic_scope(self):
        ir = ir_from("x = 1")
        d = ir.to_dict()
        self.assertFalse(d["metadata"]["full_python_semantics"])
        self.assertEqual(d["metadata"]["modeling_scope"], "safety_relevant_only")


class TestEAEnrichment(unittest.TestCase):

    EA_SOURCE = """
        population = initialize()
        for generation in range(4):
            for individual in population:
                score = objective(individual)
            selected = sorted(population, key=objective)[-3:]
            offspring = []
            for parent1, parent2 in zip(selected, selected[1:]):
                child = parent1[:2] + parent2[2:]
                child[0] += random_change()
                offspring.append(child)
            population = selected + offspring
    """

    def test_ea_program_contains_all_roles_and_evidence(self):
        data = ir_from(self.EA_SOURCE, include_ea=True).to_dict()
        roles = data["ea_roles"]["roles"]

        self.assertEqual(set(roles), {
            "population", "fitness_evaluation", "selection", "mutation",
            "crossover", "replacement", "termination",
        })
        for role, finding in roles.items():
            with self.subTest(role=role):
                self.assertTrue(finding["detected"])
                self.assertIn(finding["confidence"], {"HIGH", "MEDIUM"})
                self.assertTrue(finding["evidence"])
        ea_evidence = [item for item in data["evidence"] if item["analysis"] == "ea_inference"]
        self.assertTrue(ea_evidence)
        self.assertTrue(all(item["location"].get("line") for item in ea_evidence))
        self.assertTrue(all(item["explanation"] for item in ea_evidence))
        self.assertTrue(any(item["details"].get("cfg_blocks") for item in ea_evidence))
        self.assertEqual(data["metadata"]["ea_confidence_semantics"], "structural_evidence_strength_not_probability")

    def test_non_ea_program_is_representable_with_no_detected_roles(self):
        data = ir_from("value = 3", include_ea=True).to_dict()
        self.assertIsNotNone(data["ea_roles"])
        self.assertFalse(any(role["detected"] for role in data["ea_roles"]["roles"].values()))
        self.assertEqual(data["verdict_hint"], "SAFE")

    def test_partial_ea_structure_preserves_unknown_roles(self):
        data = ir_from("""
            candidates = create()
            for candidate in candidates:
                value = objective(candidate)
        """, include_ea=True).to_dict()
        roles = data["ea_roles"]["roles"]
        self.assertTrue(roles["population"]["detected"])
        self.assertTrue(roles["fitness_evaluation"]["detected"])
        self.assertFalse(roles["crossover"]["detected"])
        self.assertEqual(roles["crossover"]["confidence"], "LOW")
        self.assertEqual(roles["crossover"]["evidence"], [])

    def test_low_or_unknown_ea_evidence_does_not_block_ir(self):
        ir = ir_from("population = [1, 2, 3]", include_ea=True)
        data = json.loads(safety_ir_to_json(ir))
        self.assertEqual(data["ea_roles"]["roles"]["population"]["confidence"], "LOW")
        self.assertEqual(data["verdict_hint"], "SAFE")

    def test_safe_and_unsafe_ea_verdicts_are_independent_of_inference(self):
        safe_ea = self.EA_SOURCE
        unsafe_ea = """
            population = initialize()
            for individual in population:
                score = objective(individual)
                os.system(input())
        """
        for source, expected in ((safe_ea, "SAFE"), (unsafe_ea, "UNSAFE")):
            with self.subTest(expected=expected):
                without_ea = ir_from(source, include_ea=False).to_dict()
                with_ea = ir_from(source, include_ea=True).to_dict()
                self.assertEqual(without_ea["verdict_hint"], expected)
                self.assertEqual(with_ea["verdict_hint"], expected)
                self.assertEqual(with_ea["decision"]["verdict"], expected)

    def test_safe_and_unsafe_non_ea_programs_keep_verdicts(self):
        for source, expected in (("answer = 42", "SAFE"), ("eval(input())", "UNSAFE")):
            with self.subTest(expected=expected):
                data = ir_from(source, include_ea=True).to_dict()
                self.assertEqual(data["verdict_hint"], expected)
                self.assertFalse(any(role["detected"] for role in data["ea_roles"]["roles"].values()))

    def test_full_safety_facts_and_decision_are_serialized(self):
        data = ir_from("eval(input())").to_dict()
        self.assertIn("taint", data["safety_facts"])
        self.assertIn("capability", data["safety_facts"])
        self.assertIn("resource", data["safety_facts"])
        self.assertEqual(data["decision"]["verdict"], data["verdict_hint"])
        self.assertTrue(any(item["analysis"] == "taint" for item in data["evidence"]))

    def test_legacy_graph_fields_and_new_fields_serialize_deterministically(self):
        first = ir_from(self.EA_SOURCE, include_ea=True)
        second = ir_from(self.EA_SOURCE, include_ea=True)
        self.assertEqual(first.to_json(), second.to_json())
        data = json.loads(safety_ir_to_json(first))
        self.assertEqual(data["ir_version"], "1.1")
        self.assertIn("nodes", data)
        self.assertIn("edges", data)
        self.assertIn("safety_facts", data)
        self.assertIn("ea_roles", data)
        self.assertIn("evidence", data)


if __name__ == "__main__":
    unittest.main()
