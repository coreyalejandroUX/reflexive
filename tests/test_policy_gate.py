"""Refusal rules that must hold on the mobile path without a model."""
import unittest

from _helpers import ROOT  # noqa: F401  (sets sys.path)
from policy_gate import decide


def req(**kw):
    base = {"action": "code", "device": "phone", "evidence_ids": ["e1"],
            "evidence_present": ["e1"], "boundary": "deidentified_study_record",
            "human_confirmed": True}
    base.update(kw)
    return base


class PolicyGateTests(unittest.TestCase):
    def test_phone_can_never_release(self):
        for action in ("export", "share"):
            with self.subTest(action=action):
                self.assertEqual(decide(req(action=action))[0], "ESCALATE")

    def test_desktop_release_needs_interactive_human(self):
        self.assertEqual(decide(req(action="export", device="desktop", human_confirmed=False))[0],
                         "ESCALATE")

    def test_identity_in_release_payload_escalates(self):
        r = req(action="export", device="desktop", text="Met with Jordan Avery")
        self.assertEqual(decide(r, ["Jordan Avery"])[1], "publish-identity")

    def test_nothing_from_an_open_study_block_is_released(self):
        r = req(action="export", device="desktop", includes_open_study_block=True)
        self.assertEqual(decide(r)[1], "study-block-open")

    def test_missing_source_asks_then_holds(self):
        self.assertEqual(decide(req(evidence_ids=[]))[0], "ASK")
        self.assertEqual(decide(req(evidence_present=[]))[0], "HOLD")

    def test_promoting_without_a_source_holds(self):
        self.assertEqual(decide(req(action="promote", evidence_ids=[]))[0], "HOLD")

    def test_release_respects_the_use_boundary(self):
        for boundary in ("private_research_only", "unclear", None):
            with self.subTest(boundary=boundary):
                r = req(action="export", device="desktop", boundary=boundary)
                self.assertEqual(decide(r)[1], "boundary")

    def test_widening_the_boundary_is_a_desk_decision(self):
        self.assertEqual(decide(req(action="widen_boundary", to_boundary="deidentified_study_record"))[0],
                         "ESCALATE")
        self.assertEqual(decide(req(action="widen_boundary", device="desktop",
                                    to_boundary="public_release_requested"))[0], "ESCALATE")
        self.assertEqual(decide(req(action="widen_boundary", device="desktop",
                                    to_boundary="deidentified_study_record"))[0], "SAVE")

    def test_fidelity_upgrade_is_refused_downgrade_allowed(self):
        self.assertEqual(decide(req(action="relabel", from_fidelity="reconstruction",
                                    to_fidelity="direct"))[0], "REFUSE")
        self.assertEqual(decide(req(action="relabel", from_fidelity="direct",
                                    to_fidelity="reconstruction"))[0], "SAVE")

    def test_automated_review_is_held(self):
        self.assertEqual(decide(req(action="review", human_confirmed=False))[0], "HOLD")

    def test_unknown_device_holds(self):
        self.assertEqual(decide(req(device="watch"))[0], "HOLD")


if __name__ == "__main__":
    unittest.main()
