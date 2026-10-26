"""Preserve step on the mobile path: the inbox -> raw door."""
import hashlib
import tempfile
import unittest
from pathlib import Path

from _helpers import envelope, tree_hash, write_envelope
import ingest


class IngestTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.inbox, self.raw = base / "inbox", base / "raw"
        self.raw.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def run_one(self, env, watchlist=()):
        path = write_envelope(self.inbox, env)
        return ingest.preserve(path, self.raw, self.inbox, list(watchlist))

    def test_valid_capture_is_preserved_with_manifest_line(self):
        decision, _ = self.run_one(envelope())
        self.assertEqual(decision, "PRESERVED")
        stored = (self.raw / "m-20261027T081512Z-a1b2.json").read_bytes()
        manifest = (self.raw / "MANIFEST.sha256").read_text()
        self.assertIn(hashlib.sha256(stored).hexdigest(), manifest)

    def test_marker_with_no_words_is_a_complete_entry(self):
        decision, _ = self.run_one(envelope(capture_type="marker", text="", text_method="none"))
        self.assertEqual(decision, "PRESERVED")

    def test_handoff_is_a_first_class_type(self):
        decision, _ = self.run_one(envelope(capture_type="handoff"))
        self.assertEqual(decision, "PRESERVED")

    def test_offline_replay_of_same_bytes_is_harmless(self):
        env = envelope()
        self.run_one(env)
        decision, _ = self.run_one(env)
        self.assertEqual(decision, "DUPLICATE")
        self.assertEqual((self.raw / "MANIFEST.sha256").read_text().count("\n"), 1)

    def test_raw_is_immutable(self):
        self.run_one(envelope())
        before = tree_hash(self.raw)
        decision, _ = self.run_one(envelope(text="A different account of the same moment."))
        self.assertEqual(decision, "REFUSE")
        self.assertEqual(tree_hash(self.raw), before)

    def test_hash_mismatch_holds(self):
        decision, reason = self.run_one(envelope(text_sha256="0" * 64))
        self.assertEqual(decision, "HOLD")
        self.assertIn("text_sha256", reason)

    def test_missing_attachment_holds(self):
        env = envelope(capture_type="moment", fidelity="direct", attachment_file="shot.png")
        decision, reason = self.run_one(env)
        self.assertEqual(decision, "HOLD")
        self.assertIn("missing source", reason)

    def test_attachment_path_traversal_is_refused(self):
        env = envelope(capture_type="moment", fidelity="direct", attachment_file="../raw/x.json")
        self.assertEqual(self.run_one(env)[0], "REFUSE")

    def test_direct_label_needs_a_source_file(self):
        self.assertEqual(self.run_one(envelope(capture_type="moment", fidelity="direct"))[0], "HOLD")

    def test_lost_context_cannot_be_labelled_direct(self):
        self.assertEqual(self.run_one(envelope(fidelity="direct", attachment_file="x"))[0], "HOLD")

    def test_study_fields_never_enter_raw(self):
        for key in ("seeded", "study_item", "sealed_ref"):
            with self.subTest(key=key):
                env = envelope(capture_id=f"m-20261027T081512Z-{key[:4]}x")
                env[key] = True
                self.assertEqual(self.run_one(env)[0], "REFUSE")
        self.assertEqual(list(self.raw.glob("m-*.json")), [])

    def test_watchlist_name_holds_and_is_not_written(self):
        env = envelope(text="Asked Jordan Avery about the quiz.")
        decision, _ = self.run_one(env, watchlist=["Jordan Avery"])
        self.assertEqual(decision, "HOLD")
        self.assertEqual(list(self.raw.glob("m-*.json")), [])

    def test_unknown_field_needs_a_schema_proposal(self):
        self.assertEqual(self.run_one(envelope(mood="low"))[0], "HOLD")


if __name__ == "__main__":
    unittest.main()
