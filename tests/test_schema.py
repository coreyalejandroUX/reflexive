"""The shared schema is the single source of truth: same verdicts, no drift."""
import json
import unittest

from _helpers import ROOT
import ingest
import reflexive_schema as rs
from policy_gate import FIDELITY_RANK

FIXTURES = json.loads((ROOT / "schema" / "fixtures.json").read_text(encoding="utf-8"))


class SchemaTests(unittest.TestCase):
    def test_python_matches_every_shared_fixture(self):
        # schema/typescript/conformance.test.ts runs the same file through Ajv.
        for f in FIXTURES:
            with self.subTest(f["name"]):
                self.assertEqual(rs.validate(f["doc"], f["def"]) == [], f["valid"])

    def test_fidelity_labels_are_the_four_grant_labels(self):
        self.assertEqual(rs.enum("fidelity"),
                         ["direct", "user-supplied", "transcription", "reconstruction"])

    def test_support_strength_is_only_proposed(self):
        self.assertEqual(rs.definition("support_strength")["x-status"], "proposed")
        envelope_fields = rs.definition("mobile_envelope")["properties"]
        self.assertNotIn("support", envelope_fields)

    def test_policy_gate_ranks_exactly_the_schema_labels(self):
        self.assertEqual(set(FIDELITY_RANK), set(rs.enum("fidelity")))

    def test_allowed_fidelity_covers_every_capture_type_with_real_labels(self):
        self.assertEqual(set(ingest.ALLOWED_FIDELITY), set(rs.enum("capture_type")))
        for labels in ingest.ALLOWED_FIDELITY.values():
            self.assertTrue(labels <= set(rs.enum("fidelity")))

    def test_reader_refuses_keywords_it_does_not_implement(self):
        with self.assertRaises(ValueError):
            rs._check("x", {"format": "email"}, "", [])


if __name__ == "__main__":
    unittest.main()
