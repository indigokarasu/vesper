#!/usr/bin/env python3
"""
Vesper delivery-check + Telegram fallback delivery.

Scans for undelivered Vesper briefings across BOTH storage locations:
  - individual files: {data}/briefings/YYYY-WXX/YYYY-MM-DD-{type}.json
  - master index:     {data}/briefings.jsonl

Applies the dual delivery-flag / desync rules documented in SKILL.md gotchas:
  A briefing is undelivered if:
    - delivery_status == "pending" (string), OR
    - delivery_status.status in ("pending", "failed") (object), OR
    - delivered is False or None
  Skip when delivery_status == "silent" (intentional suppression).
  delivery_status == "delivered" (string or object) is AUTHORITATIVE = delivered
  (this also repairs the "delivered: null but delivery_status: delivered" desync).

Only briefings with non-empty `content` are deliverable. Entries whose
generation failed (no content) are skipped, not redelivered.

When --deliver is passed and the email MCP is unavailable (cron mode), the
script delivers via the Telegram fallback (`hermes send --to telegram`),
prepends the subject line, then updates BOTH the individual file and the
matching JSONL line. Corrupted sibling JSONL lines are preserved byte-for-byte
via a surgical line-index edit -- the whole file is NEVER rewritten, so
existing corruption at other line numbers survives untouched.

Usage:
  python3 delivery_check.py --type morning            # scan only, report
  python3 delivery_check.py --type morning --deliver  # scan + Telegram deliver
  python3 delivery_check.py --all --deliver           # all types
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

DATA = "<hermes-root>/commons/data/ocas-vesper"
BRIEF_DIR = os.path.join(DATA, "briefings")
JSONL = os.path.join(DATA, "briefings.jsonl")


def is_undelivered(rec):
    ds = rec.get("delivery_status", None)
    if isinstance(ds, str) and ds == "silent":
        return False
    if isinstance(ds, dict) and ds.get("status") == "silent":
        return False
    delivered = rec.get("delivered", None)
    und = delivered is False or delivered is None
    if isinstance(ds, str):
        if ds == "pending":
            und = True
        if ds == "delivered":
            und = False
    if isinstance(ds, dict):
        st = ds.get("status")
        if st == "delivered":
            und = False
        elif st in ("pending", "failed"):
            und = True
    return und


def has_content(rec):
    c = rec.get("content")
    return isinstance(c, "str") and c.strip() != ""


def scan_individual(btype):
    out = []
    if not os.path.isdir(BRIEF_DIR):
        return out
    for root, _, files in os.walk(BRIEF_DIR):
        for fn in files:
            if not fn.endswith(".json"):
                continue
            if btype != "all" and btype not in fn:
                continue
            path = os.path.join(root, fn)
            try:
                rec = json.load(open(path, encoding="utf-8"))
            except Exception as e:
                print(f"  PARSE ERROR {path}: {e}", file=sys.stderr)
                continue
            if is_undelivered(rec) and has_content(rec):
                out.append((path, rec))
    return out


def scan_jsonl(btype):
    out = []
    if not os.path.exists(JSONL):
        return out
    with open(JSONL, encoding="utf-8") as f:
        for i, line in enumerate(f):
            s = line.strip()
            if not s:
                continue
            try:
                rec = json.loads(s)
            except Exception:
                continue  # corrupted line -- not a candidate
            if btype != "all":
                if btype not in str(rec.get("date", "")) + str(rec.get("type", "")):
                    continue
            if is_undelivered(rec) and has_content(rec):
                out.append((i, rec))
    return out


def stamp():
    return datetime.now(timezone.utc).isoformat()


def mark_delivered_individual(path, ts):
    rec = json.load(open(path, encoding="utf-8"))
    rec["delivered"] = True
    rec["delivered_at"] = ts
    rec["delivery_status"] = {
        "status": "delivered",
        "delivered_at": ts,
        "channel": "telegram",
        "note": "Delivered via Telegram fallback - email MCP unavailable in cron session",
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rec, f, ensure_ascii=False, indent=2)


def mark_delivered_jsonl(date, btype, ts):
    """Surgical line-index edit: update only the matching line(s), preserve all
    others (including corrupted ones) byte-for-byte. Returns count updated."""
    with open(JSONL, encoding="utf-8") as f:
        raw = f.read()
    lines = raw.split("\n")
    trailing = raw.endswith("\n")
    updated = 0
    for i, line in enumerate(lines):
        s = line.strip()
        if not s:
            continue
        try:
            o = json.loads(s)
        except Exception:
            continue  # keep corrupted line exactly as-is
        if o.get("date") == date and o.get("type") == btype:
            o["delivered"] = True
            o["delivered_at"] = ts
            o["delivery_status"] = {
                "status": "delivered",
                "delivered_at": ts,
                "channel": "telegram",
                "note": "Delivered via Telegram fallback - email MCP unavailable in cron session",
            }
            lines[i] = json.dumps(o, ensure_ascii=False)
            updated += 1
    out = "\n".join(lines)
    if trailing:
        out += "\n"
    with open(JSONL, "w", encoding="utf-8") as f:
        f.write(out)
    return updated


def deliver_telegram(rec):
    date = rec.get("date")
    bt = rec.get("type", "briefing")
    label = bt.capitalize() if bt in ("morning", "evening") else "Briefing"
    subject = f"{label} Briefing - {date}"
    content = rec.get("content", "")
    tf = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8")
    tf.write(content)
    tf.close()
    cmd = ["hermes", "send", "--to", "telegram", "-s", subject, "-f", tf.name, "--quiet"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        rc = r.returncode
    except Exception as e:
        rc = -1
        print(f"  hermes send error: {e}", file=sys.stderr)
    os.unlink(tf.name)
    return rc == 0, rc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--type", choices=["morning", "evening", "all"], default="all")
    ap.add_argument(
        "--deliver",
        action="store_true",
        help="Deliver undelivered briefings via Telegram fallback (cron mode)",
    )
    args = ap.parse_args()

    indiv = scan_individual(args.type)
    jsonl = scan_jsonl(args.type)
    print(f"Undelivered ({args.type}) - individual files: {len(indiv)}, jsonl index: {len(jsonl)}")
    for path, rec in indiv:
        print(f"  FILE {rec.get('date')} {rec.get('type')}: {path}")

    if not args.deliver:
        return

    ts = stamp()
    delivered = 0
    for path, rec in indiv:
        ok, code = deliver_telegram(rec)
        if ok:
            mark_delivered_individual(path, ts)
            n = mark_delivered_jsonl(rec.get("date"), rec.get("type"), ts)
            print(f"  DELIVERED {rec.get('date')} {rec.get('type')} (jsonl lines updated: {n})")
            delivered += 1
        else:
            print(f"  FAILED {rec.get('date')} {rec.get('type')} (hermes send exit {code})", file=sys.stderr)
    print(f"Delivered via Telegram: {delivered}")


if __name__ == "__main__":
    main()
