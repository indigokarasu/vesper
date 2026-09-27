# Briefing delivery channel — EMAIL ONLY

**Rule (Jared, restated 2026-09-25 after ~100 prior statements): all Vesper
briefings go to EMAIL. Never Telegram.**

- `jared.zimmerman@gmail.com` is the briefing recipient.
- Sender: `skills/ocas-dispatch/scripts/briefing_deliver.py` — the single sender.
- Both `morning` and `evening` use the same `send_email()` path. There is no
  Telegram branch and there must not be one.
- The delivery-failure alert also goes by email
  (`briefing_delivery_verify.py`), never `hermes send`.

## Why the code is the risk, not the comment

On 2026-09-25 the module docstring had been updated to "Telegram delivery
removed — all briefings go to email" while the `main()` body still routed
`morning` to `send_telegram()`. The comment was correct and the code was
wrong, and every morning briefing still went to Telegram. A header comment is
not enforcement.

**Before changing this pipeline:** read `briefing_deliver.py` end to end, and
grep it for `telegram` — the only permitted hits are in the "removed, do not
reintroduce" comment. `TG_TARGET` and `send_telegram()` must not exist.

## Verification

- Sender history: `/root/.hermes/commons/data/ocas-vesper/briefings/*/*.json`
  → `delivery_channel` must read `email` on every delivered item.
- `delivery-log.jsonl` in the same directory records each attempt.
- 2026-09-25 evening briefing: `delivered / email` — proves the email path works.
