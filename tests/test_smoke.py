#!/usr/bin/env python3
"""Smoke tests for ocas-vesper delivery check logic (real functions, table-driven)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))

from delivery_check import has_content, is_undelivered
from dup_guard import is_delivered


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
