"""Seeding, sealing and measures."""
import unittest

from _helpers import ROOT  # noqa: F401
import measures
import seal

SECRET = b"x" * 48


def decision(i, device, outcome, dwell_ms=9000, words=30, interrupted=False):
    return {"decision_id": f"d{i}", "session_id": "s1", "item_id": f"it{i}",
            "agent_action_id": f"act{i}",
            "device": device, "presented_at": "2026-11-03T08:00:00-06:00",
            "decided_at": "2026-11-03T08:00:09-06:00", "dwell_ms": dwell_ms,
            "outcome": outcome, "item_words": words, "interrupted": interrupted}


class SealTests(unittest.TestCase):
    def test_decisions_are_reproducible_from_the_secret(self):
        self.assertEqual(seal.decide(SECRET, "it7"), seal.decide(SECRET, "it7"))

    def test_rate_stays_in_the_announced_range(self):
        for n in range(50):
            r = seal.seed_rate(bytes([n]) * 40)
            self.assertTrue(seal.RATE_LOW <= r < seal.RATE_HIGH)

    def test_commitment_catches_a_swapped_secret(self):
        c = seal.commitment(SECRET)
        self.assertTrue(seal.verify(SECRET, c))
        self.assertFalse(seal.verify(b"y" * 48, c))

    def test_device_assignment_is_roughly_balanced(self):
        phone = sum(seal.decide(SECRET, f"it{i}")["device"] == "phone" for i in range(2000))
        self.assertTrue(900 < phone < 1100, phone)

    def test_seed_status_cannot_be_recomputed_without_the_secret(self):
        ids = [f"it{i}" for i in range(300)]
        mine = {i for i in ids if seal.decide(SECRET, i)["seeded"]}
        guess = {i for i in ids if seal.decide(b"y" * 48, i)["seeded"]}
        self.assertTrue(mine)
        self.assertNotEqual(mine, guess)


class MeasureTests(unittest.TestCase):
    def setUp(self):
        self.key = [
            {"item_id": "it1", "seeded": True, "seed_kind": "unsupported_claim"},
            {"item_id": "it2", "seeded": True, "seed_kind": "unsupported_claim"},
            {"item_id": "it3", "seeded": True, "seed_kind": "wrong_code"},
            {"item_id": "it4", "seeded": True, "seed_kind": "unsupported_claim"},
            {"item_id": "it5", "seeded": False, "seed_kind": None},
            {"item_id": "it6", "seeded": False, "seed_kind": None},
        ]
        self.decisions = [
            decision(1, "phone", "approve", dwell_ms=1200),      # escape, rubber stamp
            decision(2, "phone", "hold"),                         # caught (lenient)
            decision(3, "desktop", "reject"),                     # caught
            decision(4, "desktop", "narrow"),                     # caught
            decision(5, "phone", "approve"),                      # clean accept
            decision(6, "desktop", "stopped"),                    # stop rule
        ]

    def test_rates_by_device(self):
        out = measures.run(self.decisions, self.key, iters=200)
        self.assertEqual(out["phone"]["catch_rate"]["rate"], 0.5)
        self.assertEqual(out["phone"]["catch_rate_strict"]["rate"], 0.0)
        self.assertEqual(out["desktop"]["catch_rate"]["rate"], 1.0)
        self.assertEqual(out["phone"]["escape_rate"]["rate"], 0.5)
        self.assertEqual(out["phone"]["rubber_stamp_rate"]["k"], 1)
        self.assertEqual(out["desktop"]["stops"], 1)
        self.assertIn("ci95", out["overall"]["catch_rate"])

    def test_decision_without_device_is_rejected(self):
        bad = dict(self.decisions[0])
        del bad["device"]
        with self.assertRaises(ValueError):
            measures.run([bad], self.key)

    def test_time_travel_is_rejected(self):
        bad = dict(self.decisions[0], decided_at="2026-11-03T07:00:00-06:00")
        self.assertIn("decided_at is before presented_at", measures.validate_decision(bad))

    def test_phone_float_numbers_are_accepted(self):
        self.assertEqual(measures.validate_decision(dict(self.decisions[0], dwell_ms=12000.0)), [])

    def test_long_dwell_counts_as_interrupted(self):
        slow = [dict(self.decisions[4], dwell_ms=600000)]
        out = measures.run(slow, self.key, iters=10)
        self.assertEqual(out["phone"]["interrupted"], 1)
        self.assertIsNone(out["phone"]["median_dwell_s"])

    def test_wilson_interval_is_wide_for_small_n(self):
        ci = measures.wilson(4, 5)["ci95"]
        self.assertGreater(ci[1] - ci[0], 0.4)


if __name__ == "__main__":
    unittest.main()
