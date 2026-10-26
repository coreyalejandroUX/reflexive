"""Preserve step on the mobile path: the inbox -> raw door."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from _helpers import envelope, tree_hash, write_envelope
import ingest
import withdraw


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

    def test_phone_cannot_widen_the_use_boundary(self):
        for boundary in ("deidentified_study_record", "public_release_requested"):
            with self.subTest(boundary=boundary):
                decision, reason = self.run_one(envelope(boundary=boundary))
                self.assertEqual(decision, "HOLD")
                self.assertIn("at the desk", reason)

    def test_unclear_boundary_is_allowed_from_the_phone(self):
        self.assertEqual(self.run_one(envelope(boundary="unclear"))[0], "PRESERVED")

    def test_envelope_0_1_is_still_preserved(self):
        env = envelope(envelope_version="0.1")
        del env["boundary"], env["capture_seconds"]
        self.assertEqual(self.run_one(env)[0], "PRESERVED")

    def test_unknown_envelope_version_holds(self):
        self.assertEqual(self.run_one(envelope(envelope_version="9.9"))[0], "HOLD")

    def test_unknown_field_needs_a_schema_proposal(self):
        self.assertEqual(self.run_one(envelope(mood="low"))[0], "HOLD")


class WithdrawTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.inbox, self.raw = base / "inbox", base / "raw"
        self.raw.mkdir()
        self.env = envelope()
        self.path = write_envelope(self.inbox, self.env)
        ingest.preserve(self.path, self.raw, self.inbox, [])
        self.cid = self.env["capture_id"]

    def tearDown(self):
        self.tmp.cleanup()

    def test_withdraw_removes_file_and_keeps_only_the_hash(self):
        stored = (self.raw / f"{self.cid}.json").read_bytes()
        ok, message = withdraw.withdraw(self.raw, self.cid, "participant_choice", self.inbox)
        self.assertTrue(ok)
        self.assertIn("Git history", message)
        self.assertFalse((self.raw / f"{self.cid}.json").exists())
        self.assertFalse(self.path.exists())
        row = json.loads((self.raw / "WITHDRAWN.jsonl").read_text())
        self.assertEqual(row["sha256"], hashlib.sha256(stored).hexdigest())
        self.assertNotIn(self.env["text"], (self.raw / "WITHDRAWN.jsonl").read_text())

    def test_offline_replay_cannot_bring_a_withdrawn_capture_back(self):
        withdraw.withdraw(self.raw, self.cid, "consent_change")
        decision, _ = ingest.preserve(self.path, self.raw, self.inbox, [])
        self.assertEqual(decision, "REFUSE")
        self.assertFalse((self.raw / f"{self.cid}.json").exists())

    def test_free_text_reason_is_rejected(self):
        ok, _ = withdraw.withdraw(self.raw, self.cid, "the tutor transcript embarrassed me")
        self.assertFalse(ok)
        self.assertTrue((self.raw / f"{self.cid}.json").exists())


if __name__ == "__main__":
    unittest.main()
