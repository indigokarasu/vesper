#!/usr/bin/env python3
"""Smoke tests for ocas-vesper delivery check logic (real functions, table-driven)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))

from delivery_check import has_content, is_undelivered


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

    def test_has_content(self):
        self.check(has_content, [({"content": "Hello world"}, True), ({"content": ""}, False),
                                 ({"content": "   \n"}, False), ({"content": None}, False), ({}, False)])

    def test_deliverable_candidate_requires_content(self):
        rec = {"delivered": False, "delivery_status": "pending", "content": "Hello world"}
        self.assertTrue(is_undelivered(rec) and has_content(rec))
        blank = dict(rec, content="   ")
        self.assertFalse(is_undelivered(blank) and has_content(blank))


if __name__ == "__main__":
    unittest.main()
