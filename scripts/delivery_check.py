#!/usr/bin/env python3
"""Vesper delivery-check + Email fallback delivery.

Scans for undelivered Vesper briefings across BOTH storage locations:
  - individual files: {data}/briefings/YYYY-WXX/YYYY-MM-DD-{type}.json
  - master index:     {data}/briefings.jsonl

It applies the dual delivery-flag / desync rules documented in SKILL.md gotchas.

When --deliver is passed and the email MCP is unavailable (cron mode), this
script now delivers via direct Gmail API as an *email* fallback (no Telegram).

Usage:
  python3 delivery_check.py --type morning            # scan only, report
  python3 delivery_check.py --type morning --deliver  # scan + Email deliver
  python3 delivery_check.py --all --deliver           # all types
"""

import argparse
import json
import os
import sys

# Third-party imports are deferred to function scope so --help works even when
# google-auth / google-api-python-client are not installed (D9 compliance).

DATA = os.path.expanduser("~/.hermes/commons/data/ocas-vesper")
BRIEF_DIR = os.path.join(DATA, "briefings")
JSONL = os.path.join(DATA, "briefings.jsonl")

# Default: only deliver briefings within this many days of today
MAX_AGE_DAYS = 2


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
    return isinstance(c, str) and c.strip() != ""


def scan_individual(btype, max_days=MAX_AGE_DAYS):
    from datetime import datetime, timedelta
    out = []
    if not os.path.isdir(BRIEF_DIR):
        return out

    cutoff = datetime.now().astimezone() - timedelta(days=max_days)

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

            # Skip briefings older than max_days
            bdate = rec.get("date", "")
            if bdate:
                try:
                    bdt = datetime.strptime(bdate, "%Y-%m-%d").replace(
                        tzinfo=cutoff.tzinfo
                    )
                    if bdt < cutoff:
                        continue
                except ValueError:
                    pass  # unparseable date — let it through

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
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


def mark_delivered_individual(path, ts):
    rec = json.load(open(path, encoding="utf-8"))
    rec["delivered"] = True
    rec["delivered_at"] = ts
    rec["delivery_status"] = {
        "status": "delivered",
        "delivered_at": ts,
        "channel": "email",
        "note": "Delivered via Email fallback - email MCP unavailable in cron session",
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
                "channel": "email",
                "note": "Delivered via Email fallback - email MCP unavailable in cron session",
            }
            lines[i] = json.dumps(o, ensure_ascii=False)
            updated += 1

    out = "\n".join(lines)
    if trailing:
        out += "\n"

    with open(JSONL, "w", encoding="utf-8") as f:
        f.write(out)

    return updated


def deliver_email(rec):
    """Send a briefing via Gmail API. Returns (ok, id_or_error)."""
    from email.mime.text import MIMEText
    from email.header import Header
    import base64
    # Lazy import so --help works without google libs
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    # Local template module (lazy so --help works without it)
    sys.path.insert(0, "~/.hermes/profiles/indigo/commons/email-templates")
    from send_email import render_vesper_template

    date = rec.get("date")
    bt = rec.get("type", "briefing")
    label = bt.capitalize() if bt in ("morning", "evening") else "Briefing"
    subject = f"{label} Briefing — {date}"

    # Use the proper vesper template to render styled HTML
    data = {
        "type": bt,
        "date": date,
        "content": rec.get("content", ""),
    }
    html_body = render_vesper_template(data)

    sender = os.environ.get("VESPER_SENDER_EMAIL", "mx.indigo.karasu@gmail.com")
    recipient = os.environ.get("VESPER_OWNER_EMAIL", "<operator-email>")

    creds_dir = "~/.google_workspace_mcp/credentials"
    credentials_path = os.path.join(creds_dir, f"{sender}.json")
    if not os.path.exists(credentials_path):
        return False, f"Missing Gmail credentials file: {credentials_path}"

    with open(credentials_path, "r", encoding="utf-8") as f:
        token_data = json.load(f)

    creds = Credentials.from_authorized_user_info(token_data)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    service = build("gmail", "v1", credentials=creds, cache_discovery=False)

    msg = MIMEText(html_body, "html", "utf-8")
    msg["To"] = recipient
    msg["From"] = sender
    msg["Subject"] = str(Header(subject, "utf-8"))

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
    res = service.users().messages().send(userId="me", body={"raw": raw}).execute()

    return True, res.get("id")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--type", choices=["morning", "evening", "all"], default="all")
    ap.add_argument("--days", type=int, default=1,
                    help="Max age in days for briefings to deliver (default: 1)")
    ap.add_argument(
        "--deliver",
        action="store_true",
        help="Deliver undelivered briefings via Email fallback (cron mode)",
    )
    args = ap.parse_args()

    indiv = scan_individual(args.type, max_days=args.days)
    jsonl = scan_jsonl(args.type)

    print(f"Undelivered ({args.type}) - individual files: {len(indiv)}, jsonl index: {len(jsonl)}")
    for path, rec in indiv:
        print(f"  FILE {rec.get('date')} {rec.get('type')}: {path}")

    if not args.deliver:
        return

    ts = stamp()
    delivered = 0

    for path, rec in indiv:
        ok, code_or_err = deliver_email(rec)
        if ok:
            mark_delivered_individual(path, ts)
            n = mark_delivered_jsonl(rec.get("date"), rec.get("type"), ts)
            print(f"  DELIVERED {rec.get('date')} {rec.get('type')} (jsonl lines updated: {n})")
            delivered += 1
        else:
            print(
                f"  FAILED {rec.get('date')} {rec.get('type')} (email error: {code_or_err})",
                file=sys.stderr,
            )

    print(f"Delivered via Email fallback: {delivered}")


if __name__ == "__main__":
    main()
