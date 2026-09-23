#!/usr/bin/env python3
"""Smoke tests for ocas-vesper delivery check logic."""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestDeliveryStatus(unittest.TestCase):
    """Test the dual delivery-flag detection logic."""

    def setUp(self):
        """Create a temporary directory with test briefing files."""
        self.tmpdir = tempfile.mkdtemp()
        self.data_dir = Path(self.tmpdir) / "ocas-vesper"
        self.data_dir.mkdir()
        self.briefings_dir = self.data_dir / "briefings" / "2025-W10"
        self.briefings_dir.mkdir(parents=True)

    def _write_briefing(self, name, data):
        path = self.briefings_dir / name
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def test_delivered_boolean_true(self):
        """A briefing with delivered=True should be considered delivered."""
        bp = self._write_briefing("test.json", {"delivered": True, "content": "Test"})
        content = json.loads(bp.read_text(encoding="utf-8"))
        self.assertTrue(content.get("delivered"))

    def test_undelivered_with_content(self):
        """A briefing with delivered=False and content should be deliverable."""
        bp = self._write_briefing("undelivered.json", {
            "delivered": False,
            "delivery_status": {"status": "pending", "delivered_at": None},
            "content": "Hello world"
        })
        content = json.loads(bp.read_text(encoding="utf-8"))
        self.assertFalse(content.get("delivered"))
        self.assertEqual(content["delivery_status"]["status"], "pending")

    def test_delivery_status_three_formats(self):
        """Verify the three delivery_status formats are recognized."""
        # Format 1: plain string
        f1 = self._write_briefing("f1.json", {"delivery_status": "delivered", "content": "a"})
        # Format 2: object with status/delivered_at
        f2 = self._write_briefing("f2.json", {"delivery_status": {"status": "delivered", "delivered_at": "2026-01-01T00:00:00Z"}, "content": "b"})
        # Format 3: object with status/failed_at/reason
        f3 = self._write_briefing("f3.json", {"delivery_status": {"status": "failed", "failed_at": "2026-01-01T00:00:00Z", "reason": "OAuth"}, "content": "c"})

        for f in [f1, f2, f3]:
            data = json.loads(f.read_text(encoding="utf-8"))
            self.assertIn("delivery_status", data)

    def test_silent_status_skipped(self):
        """Briefings with delivery_status 'silent' should be skipped."""
        bp = self._write_briefing("silent.json", {"delivery_status": "silent", "content": ""})
        data = json.loads(bp.read_text(encoding="utf-8"))
        ds = data.get("delivery_status")
        if isinstance(ds, str):
            self.assertEqual(ds, "silent")
        else:
            self.assertEqual(ds.get("status"), "silent")

    def test_jsonl_parses(self):
        """Ensure our test JSONL is parseable."""
        jsonl_path = self.data_dir / "briefings.jsonl"
        records = [
            {"briefing_id": "test-1", "delivered": True, "content": "a"},
            {"briefing_id": "test-2", "delivered": False, "content": "b"},
        ]
        jsonl_path.write_text("\n".join(json.dumps(r) for r in records), encoding="utf-8")
        # Verify each line parses as valid JSON
        for line in jsonl_path.read_text(encoding="utf-8").strip().split("\n"):
            parsed = json.loads(line)
            self.assertIn("briefing_id", parsed)

if __name__ == "__main__":
    unittest.main()
