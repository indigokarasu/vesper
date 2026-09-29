#!/usr/bin/env python3
"""Smoke tests for ocas-vesper delivery check logic (real functions, table-driven)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))

from delivery_check import has_content, is_undelivered
from dup_guard import is_delivered
from quality_check import check_internal_maintenance


def _brief(system_text=None, content="Good morning\nYou have a 10:00 with Sarah."):
    """A minimal well-formed briefing, optionally carrying one System item."""
    sections = []
    if system_text is not None:
        sections.append({
            "section_type": "system",
            "section_marker": "⚙",
            "content_items": [{"summary": system_text}],
        })
    return {"type": "morning", "sections": sections, "content": content}


class TestInternalMaintenanceGate(unittest.TestCase):
    """3f must catch the real defect and must not flag the legitimate neighbour.

    Both directions are pinned: a gate that only ever returns clean is a
    safe-direction false negative, and one that flags everything would stop
    briefings being delivered at all.
    """

    def test_catches_the_two_delivered_offenders(self):
        """The exact strings that reached Jared's inbox on 09-28 and 09-29."""
        offenders = [
            ("Chronicle context engine: 51 init failures across 9 hours (06:42-15:30 PDT), "
             "peak 10/hour. All self-healed via heuristic fallback. Duplicate-core hypothesis "
             "falsified; measured root cause is 5s init busy timeout."),
            ("Custodian proposal insight-20260928-fingerprint-msfield-fix (tier 3, "
             "confidence 0.95, status open). Raw log lines carry 'YYYY-MM-DD HH:MM:SS,mmm' "
             "prefixes, so the millisecond field produced literal 503/402/429 tokens."),
        ]
        for text in offenders:
            with self.subTest(text=text[:40]):
                self.assertTrue(check_internal_maintenance(_brief(text)),
                                "gate missed a delivered offender")

    def test_catches_maintenance_in_rendered_content_only(self):
        """A violation can arrive through `content` with no System section at all."""
        b = {"type": "morning", "sections": [],
             "content": "Good morning\nThe fleet-wide watchdog tripped and self-healed."}
        self.assertTrue(check_internal_maintenance(b))

    def test_allows_owner_relevant_absence(self):
        """A missing data source is the OWNER's information, not our maintenance.

        This is the near-miss boundary: deleting this assertion would let the
        gate quietly expand until briefings cannot say why a section is empty.
        """
        ok = [
            "Calendar sync and email delivery are currently unavailable this cycle, so "
            "today's events and new messages do not appear here.",
            "Email source silent this cycle; no Dispatch summary available. Briefing built "
            "from calendar context and portfolio report.",
            "Some supporting market indicators were unavailable for today's report.",
            "Your portfolio closed yesterday at $412,908 (-0.4%). Tomorrow: gym 10:00, "
            "breast imaging 12:15.",
        ]
        for text in ok:
            with self.subTest(text=text[:40]):
                self.assertEqual(check_internal_maintenance(_brief(text)), [])

    def test_allows_portfolio_performance_language(self):
        """The words the owner is actually reading must never be flagged.

        Regression: the first draft of this gate included `benchmark` and
        `throughput`, which fire on "Portfolio beat the SPY benchmark by 0.60%"
        and "throughput was 62% of baseline". A corpus sweep over 61 delivered
        briefings found 6 such false positives and zero real ones among them.
        The two terms were removed; this pins the removal.
        """
        ok = [
            "The portfolio beat the SPY benchmark by 0.60% today (SPY -0.53%). "
            "Five orders filled. UTHR was the strongest mover at +4.9%.",
            "Your portfolio lagged the benchmark by 0.12% on the day. Throughput was "
            "normal and allocation is unchanged.",
        ]
        for text in ok:
            with self.subTest(text=text[:40]):
                self.assertEqual(check_internal_maintenance(_brief(text)), [])

    def test_clean_briefing_passes(self):
        self.assertEqual(check_internal_maintenance(_brief()), [])

    def test_empty_and_missing_fields_are_not_flagged(self):
        """A malformed briefing must report the malformed thing, not this gate."""
        for b in ({}, {"sections": []}, {"content": ""},
                  {"sections": [{"section_type": "system", "content_items": []}]},
                  {"sections": [{"section_type": "system",
                                 "content_items": [{"summary": ""}]}]}):
            with self.subTest(briefing=b):
                self.assertEqual(check_internal_maintenance(b), [])


class TestDeliveryStatus(unittest.TestCase):
    """Coverage of the dual delivery-flag / desync rules."""

    def check(self, fn, cases):
        for rec, expected in cases:
            with self.subTest(rec=rec):
                self.assertIs(fn(rec), expected)

    def test_delivered_boolean(self):
        self.check(is_undelivered, [({"delivered": True}, False), ({"delivered": False}, True), ({}, True)])

    def test_delivery_status_string(self):
        self.check(is_undelivered, [({"delivery_status": "delivered", "delivered": False}, False),
                                    ({"delivery_status": "pending"}, True)])

    def test_delivery_status_dict(self):
        self.check(is_undelivered, [
            ({"delivery_status": {"status": "delivered", "delivered_at": "2026-01-01T00:00:00Z"}}, False),
            ({"delivered": False, "delivery_status": {"status": "pending", "delivered_at": None}}, True),
            ({"delivery_status": {"status": "failed", "failed_at": "2026-01-01T00:00:00Z", "reason": "OAuth"}}, True)])

    def test_silent_never_undelivered(self):
        self.check(is_undelivered, [({"delivery_status": "silent"}, False),
                                    ({"delivered": False, "delivery_status": {"status": "silent"}}, False)])

    def test_skipped_stale_never_undelivered(self):
        """skipped_stale is terminal in BOTH storage shapes.

        Regression: only the string form was handled, so a record shaped
        {"delivery_status": {"status": "skipped_stale"}} read as undelivered
        and the sender would have re-emitted a briefing it had already swept.
        """
        self.check(is_undelivered, [({"delivery_status": "skipped_stale"}, False),
                                    ({"delivery_status": {"status": "skipped_stale"}}, False),
                                    ({"delivered": False,
                                      "delivery_status": {"status": "skipped_stale"}}, False)])

    def test_has_content(self):
        self.check(has_content, [({"content": "Hello world"}, True), ({"content": ""}, False),
                                 ({"content": "   \n"}, False), ({"content": None}, False), ({}, False)])

    def test_deliverable_candidate_requires_content(self):
        rec = {"delivered": False, "delivery_status": "pending", "content": "Hello world"}
        self.assertTrue(is_undelivered(rec) and has_content(rec))
        blank = dict(rec, content="   ")
        self.assertFalse(is_undelivered(blank) and has_content(blank))


class TestDupGuard(unittest.TestCase):
    """The guard must never suppress a send, and must always catch a real one.

    A false 'delivered' here means Jared silently stops getting a briefing, so
    the half-written-flag case is pinned explicitly.
    """

    def check(self, cases):
        for rec, expected in cases:
            with self.subTest(rec=rec):
                self.assertIs(is_delivered(rec), expected)

    def test_terminal_statuses_count_as_delivered(self):
        self.check([
            ({"delivery_status": "delivered"}, True),
            ({"delivery_status": {"status": "delivered", "delivered_at": "2026-09-26T20:17:10-07:00"}}, True),
            ({"delivery_status": "silent"}, True),
            ({"delivery_status": "skipped_stale"}, True),
            ({"delivery_status": {"status": "silent"}}, True),
            ({"delivery_status": {"status": "skipped_stale"}}, True),
        ])

    def test_pending_and_failed_are_not_delivered(self):
        self.check([
            ({"delivery_status": "pending"}, False),
            ({"delivery_status": {"status": "pending", "delivered_at": None}}, False),
            ({"delivery_status": {"status": "failed", "failed_at": "x", "reason": "OAuth"}}, False),
            ({"delivered": False}, False),
            ({"delivered": None}, False),
            ({}, False),
        ])

    def test_delivered_without_timestamp_is_still_delivered(self):
        """The sender treats any 'delivered' status as terminal, timestamp or not.

        The guard must match that exactly. Being stricter here would regenerate
        a briefing the sender already considers sent, which is the duplicate
        email this guard exists to prevent.
        """
        self.check([({"delivery_status": {"status": "delivered", "delivered_at": None}}, True)])

    def test_boolean_true_fallback(self):
        self.check([({"delivered": True}, True)])

    def test_guard_agrees_with_sender(self):
        """The guard must never disagree with the sender about a real record.

        The sender ships outside this repo, so the cross-check only runs where
        it is actually installed. CI must not fail on a missing host path --
        the in-repo table tests above are the portable coverage.
        """
        try:
            sys.path.insert(0, "/root/.hermes/profiles/indigo/skills/ocas-dispatch/scripts")
            from briefing_deliver import TERMINAL as SENDER_TERMINAL, status_of
        except ImportError:
            self.skipTest("sender module not installed on this host")

        recs = [
            {"delivered": True},
            {"delivered": False, "delivery_status": "pending"},
            {"delivery_status": {"status": "delivered", "delivered_at": "t"}},
            {"delivery_status": {"status": "delivered", "delivered_at": None}},
            {"delivery_status": "silent"},
            {"delivery_status": "skipped_stale"},
            {"delivery_status": {"status": "failed", "failed_at": "t", "reason": "r"}},
            {"delivery_status": {"status": "pending", "delivered_at": None}},
            {},
        ]
        for rec in recs:
            with self.subTest(rec=rec):
                self.assertEqual(is_delivered(rec), status_of(rec) in SENDER_TERMINAL)


if __name__ == "__main__":
    unittest.main()
