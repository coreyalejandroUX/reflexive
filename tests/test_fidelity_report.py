"""The corpus fidelity report reads, counts, and never relabels."""
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from _helpers import tree_hash
import fidelity_report


class FidelityReportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        c = Path(self.tmp.name)
        (c / "record").mkdir()
        (c / "record" / "a.json").write_text(json.dumps(
            [{"id": "r1", "fidelity": "user-supplied"}, {"id": "r2", "fidelity": "direct"},
             {"id": "r3", "fidelity": "Corroborated: transcript + screenshot"},
             {"id": "r4"}]))
        (c / "record" / "b.jsonl").write_text(
            json.dumps({"id": "r5", "fidelity": "User-supplied"}) + "\n")
        (c / "notes.md").write_text("---\nfidelity: reconstruction\n---\nbody\n")
        (c / "broken.json").write_text("{not json")
        self.corpus = c

    def tearDown(self):
        self.tmp.cleanup()

    def test_counts_exact_values_without_normalizing(self):
        r = fidelity_report.scan(self.corpus)
        self.assertEqual(r["labelled_values"], 5)
        self.assertEqual(r["counts"]["user-supplied"], 1)
        self.assertEqual(r["counts"]["User-supplied"], 1)
        self.assertEqual(r["by_family"], {"grant": 3, "checkpoint": 1, "other": 1})
        self.assertEqual(r["other_values"], ["User-supplied"])

    def test_reports_unlabeled_and_unreadable(self):
        r = fidelity_report.scan(self.corpus)
        self.assertEqual(r["records_without_field"], 1)
        self.assertEqual(r["unreadable_files"], ["broken.json"])

    def test_never_modifies_the_corpus(self):
        before = tree_hash(self.corpus)
        with contextlib.redirect_stdout(io.StringIO()):
            fidelity_report.main([str(self.corpus), "--expect", "68"])
        self.assertEqual(tree_hash(self.corpus), before)


if __name__ == "__main__":
    unittest.main()
