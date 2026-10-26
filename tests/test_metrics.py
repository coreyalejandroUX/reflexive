"""Capture metrics from raw, and inter-reviewer agreement."""
import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from _helpers import envelope, tree_hash, write_envelope
import agreement
import capture_metrics


class CaptureMetricsTests(unittest.TestCase):
    def test_rates_and_timing(self):
        with tempfile.TemporaryDirectory() as d:
            raw = Path(d)
            write_envelope(raw, envelope(capture_id="m-20261027T081512Z-aaaa", capture_seconds=7))
            write_envelope(raw, envelope(capture_id="m-20261027T081512Z-bbbb", capture_type="handoff",
                                         capture_seconds=14))
            old = envelope(capture_id="m-20261027T081512Z-cccc", envelope_version="0.1",
                           capture_type="marker", text="", text_method="none")
            del old["boundary"], old["capture_seconds"]
            write_envelope(raw, old)
            before = tree_hash(raw)
            m = capture_metrics.metrics(capture_metrics.load(raw))
            self.assertEqual(tree_hash(raw), before)
        self.assertEqual(m["timed_captures"], 2)
        self.assertEqual(m["median_capture_seconds"], 10.5)
        self.assertEqual(m["share_within_target"], 0.5)
        self.assertEqual(m["context_loss_rate"], 0.333)
        self.assertEqual(m["marker_rate"], 0.333)
        self.assertIn("not recorded (envelope 0.1)", m["boundary_mix"])

    def test_empty_raw_gives_no_rates(self):
        with tempfile.TemporaryDirectory() as d:
            m = capture_metrics.metrics(capture_metrics.load(Path(d)))
        self.assertIsNone(m["context_loss_rate"])
        self.assertIsNone(m["median_capture_seconds"])


def rows(outcomes):
    return [{"item_id": f"it{i}", "outcome": o} for i, o in enumerate(outcomes)]


class AgreementTests(unittest.TestCase):
    def test_perfect_agreement(self):
        a, b = agreement.paired(rows(["approve", "reject", "hold"]), rows(["approve", "reject", "hold"]))
        s = agreement.summary(a, b)
        self.assertEqual(s["four_outcomes"]["kappa"], 1.0)

    def test_kappa_matches_a_worked_example(self):
        # 10 items: A approves 5, B approves 6, they agree on 7. kappa = (0.7 - 0.5) / 0.5 = 0.4
        a = ["approve"] * 5 + ["reject"] * 5
        b = ["approve"] * 4 + ["reject"] + ["approve"] * 2 + ["reject"] * 3
        self.assertAlmostEqual(agreement.cohen_kappa(a, b), 0.4)

    def test_stopped_and_unshared_items_are_not_compared(self):
        a, b = agreement.paired(rows(["approve", "stopped", "hold"]), rows(["approve", "reject"]))
        self.assertEqual(len(a), 1)

    def test_cli_prints_item_counts(self):
        with tempfile.TemporaryDirectory() as d:
            pa, pb = Path(d) / "a.jsonl", Path(d) / "b.jsonl"
            pa.write_text('{"item_id": "x", "outcome": "approve"}\n')
            pb.write_text('{"item_id": "x", "outcome": "narrow"}\n')
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                agreement.main([str(pa), str(pb)])
        self.assertIn('"items": 1', buf.getvalue())


if __name__ == "__main__":
    unittest.main()
