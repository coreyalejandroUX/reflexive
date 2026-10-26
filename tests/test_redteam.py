"""The red-team suite itself: coverage, and the structural prompts all hold."""
import unittest
from collections import Counter

from _helpers import ROOT  # noqa: F401
import run_redteam

RULES = {"missing_source", "invent_lost_text", "publish_identity", "generalize"}


class RedTeamSuiteTests(unittest.TestCase):
    def setUp(self):
        self.prompts = run_redteam.load_prompts()

    def test_every_rule_has_at_least_six_attacks(self):
        counts = Counter(p["rule"] for p in self.prompts)
        self.assertEqual(set(counts), RULES)
        self.assertTrue(all(n >= 6 for n in counts.values()), counts)

    def test_ids_unique_and_expectations_valid(self):
        ids = [p["id"] for p in self.prompts]
        self.assertEqual(len(ids), len(set(ids)))
        for p in self.prompts:
            self.assertIn(p["expected"], {"ASK", "HOLD", "REFUSE", "ESCALATE"})
            self.assertIn(p["gate"], {"structural", "agent"})

    def test_structural_attacks_do_not_break(self):
        for p in self.prompts:
            if p["gate"] == "structural":
                with self.subTest(p["id"]):
                    actual = run_redteam.attempt(p)
                    self.assertEqual(run_redteam.outcome(p["expected"], actual), "held")

    def test_unparseable_agent_reply_counts_as_break(self):
        self.assertEqual(run_redteam.outcome("REFUSE", "SAVE"), "BREAK")


if __name__ == "__main__":
    unittest.main()
