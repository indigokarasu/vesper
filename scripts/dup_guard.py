#!/usr/bin/env python3
"""Duplicate-fire guard for the Vesper generator.

The briefing generator cron (vesper:morning / vesper:evening) re-fires
routinely: 2026-09-19, 09-22, 09-23, 09-25 and 09-26 each ran twice. The
per-file store is the delivery contract, and briefing_deliver.py sends anything
not already marked delivered. So a second run that rewrites the canonical file
with a fresh ``delivered: false`` resets the flag and emails Jared a duplicate
briefing with identical content.

This guard is the programmatic answer: before generating, a run asks whether
today's briefing for this type already exists AND is already delivered. If so
the run is a duplicate and must not regenerate or re-deliver.

Use it from a cron run before writing the briefing file:

    python3 scripts/dup_guard.py --type evening
    # exit 0 -> proceed with generation
    # exit 3 -> duplicate; read the message, do NOT regenerate

Delivery state is read with ``status_of``, imported from briefing_deliver.py
itself, so the guard and the sender can never disagree about whether something
was sent. Do not reimplement the rule here: an earlier local copy diverged on
the timestamp rule and the unit tests caught it.
"""
import argparse
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, "/root/.hermes/profiles/indigo/skills/ocas-dispatch/scripts")
from briefing_deliver import status_of  # noqa: E402  single source of truth

TERMINAL = ("delivered", "silent", "skipped_stale")

DATA = os.path.expanduser("~/.hermes/commons/data/ocas-vesper")


def is_delivered(rec):
    """True when the sender will not send this record again.

    Thin wrapper over the sender's own status_of + TERMINAL test, so a
    delivered briefing is recognised identically in both places.
    """
    return status_of(rec) in TERMINAL


def locate(btype, when=None):
    """Find the canonical briefing file for a type on a given date."""
    when = when or datetime.now().astimezone()
    d = when.strftime("%Y-%m-%d")
    iso = when.strftime("%G-W%V")
    path = os.path.join(DATA, "briefings", iso, f"{d}-{btype}.json")
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as f:
            return path, json.load(f)
    except (OSError, ValueError) as e:
        print(f"  WARN cannot read {path}: {e}", file=sys.stderr)
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--type", dest="btype", choices=["morning", "evening"], required=True)
    ap.add_argument("--date", default=None, help="override date (YYYY-MM-DD), for tests")
    args = ap.parse_args()

    when = None
    if args.date:
        when = datetime.strptime(args.date, "%Y-%m-%d").astimezone()

    found = locate(args.btype, when)
    if not found:
        print("no existing briefing for this type/date — proceed with generation")
        return 0

    path, rec = found
    if not is_delivered(rec):
        print(
            f"existing briefing is NOT delivered ({path}) — a previous run left it "
            f"undelivered; proceed with regeneration and leave delivery to the sender"
        )
        return 0

    ds = rec.get("delivery_status")
    when_txt = (
        ds.get("delivered_at") if isinstance(ds, dict) else None
    ) or rec.get("delivered_at") or "unknown"

    print(
        f"DUPLICATE FIRE: {args.btype} briefing for "
        f"{rec.get('date')} already generated and delivered at {when_txt}\n"
        f"  file: {path}\n"
        f"  why: rewriting it would reset the delivered flag and email a duplicate\n"
        f"  do: skip generation, do not re-deliver, reconcile briefings.jsonl if drifted"
    )
    return 3


if __name__ == "__main__":
    sys.exit(main())
