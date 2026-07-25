# ⚙️ Vesper

  <img src="./assets/readme/hero.jpg" width="100%" alt="Vesper">

Daily briefing generator. Aggregates signals from across the system into

**Skill name:** `ocas-vesper`
**Version:** 2.13.0
**Type:** 
**Layer:** productivity
**Author:** Indigo Karasu

---

## 📖 Overview

Daily briefing generator. Aggregates signals from across the system into

---

## 🔧 Capabilities

- `vesper.briefing.morning` — generate morning briefing
- `vesper.briefing.evening` — generate evening briefing
- `vesper.briefing.manual` — on-demand briefing
- `vesper.briefing.deliver` — deliver undelivered briefings via email using `mcp_google_workspace_send_gmail_message` (NOT `briefing_deliver.py` which is broken). Scan individual briefing files for non-delivered status, convert content to HTML, send via MCP, update both the individual file and `briefings.jsonl` on success. In cron sessions where the email MCP is unavailable, `python3 scripts/delivery_check.py --type <morning|evening|all> --deliver` performs the same scan, delivers via the Telegram fallback, and updates both records — see Direct Telegram delivery gotcha.
- `vesper.briefing.check` — inspect the latest briefing file (`scripts/check_briefing.py`)
- `vesper.decisions.pending` — list unacted decision requests
- `vesper.config.set` — update schedule, sections, delivery
- `vesper.status` — last briefing time, pending decisions, schedule
- `vesper.journal` — write journal for the current run; called at end of every run
- `vesper.update` — pull latest from GitHub source; preserves journals and data
- `entities_observed` — type, name, context
- `relationships_observed` — connections between entities
- `preferences_observed` — user preferences inferred from briefing interactions
- **`briefing_deliver.py` is BROKEN — use MCP tools directly** — The `scripts/briefing_deliver.py` script uses `googleapiclient` directly and will fail with import/auth errors in cron mode. When delivering briefings, always use `mcp_google_workspace_send_gmail_message` via MCP. Build HTML manually from the `content` field — no template file needed. See the delivery check procedure in cron mode for the correct approach.
- **`delivery_status` has THREE formats** — The field can be: (1) a plain string: `"delivered"`, `"pending"`, or `"silent"`; (2) an object with `{status: "delivered", delivered_at: "..."}`; (3) an object with `{status: "failed", failed_at: "...", reason: "..."}`. When scanning for undelivered briefings, check ALL three forms. A briefing is undelivered if: `delivery_status` is `"pending"`, OR `delivery_status.status` is `"failed"` or `"pending"`, OR `delivered` is `false` or `null`/`None`. **Skip `"silent"` status** — these are intentionally suppressed briefings with no content, not failed deliveries. **Also skip `"draft"` status in JSONL** — this is an intermediate state that can get stuck; always cross-reference against the individual file's `delivery_status` before treating a `"draft"` JSONL entry as undelivered.
- **`delivered: null` with `delivery_status: "delivered"` desync** — A specific desync where the individual briefing file has `delivered: null` (JSON null, never set) but `delivery_status: "delivered"` (plain string) with a valid `delivered_at` timestamp. This happens when delivery succeeds but the code path that sets the top-level `delivered` boolean doesn't run. The `delivery_status` field is authoritative — if it says `"delivered"` with a timestamp, the briefing WAS delivered. Fix by setting `delivered: true` in the individual file. Always check both fields independently.
- **`patch` is unreliable after `read_file`** — `read_file` wraps output with `N|` line prefixes that don't exist in the actual file. If you read a file via `read_file` and then try `patch`, the old_string may never match. Use `terminal` + Python (`json.load`/`json.dump` per line) or `write_file` to rewrite. This applies to ALL files, not just JSONL. The `patch` tool operates on raw file content. If you include the `N|` prefix in both old_string and new_string, you can accidentally create duplicate prefixes (e.g., `27|27|`). SAFE alternatives: (1) Use `terminal` + `sed -i 'Ns/^N|N|/|/'` for surgical single-line prefix fixes. (2) Use `terminal` + Python (`json.load` per line, modify, `json.dump` per line) for structured edits. (3) Use `write_file` to rewrite the entire file from a parsed representation. NEVER use `patch` with the `N|` prefix included in both old and new strings — the prefix duplicates and corrupts the line, making it unparseable.
- **`quality_check.py`** — The quality check script lives at `~/.hermes/profiles/indigo/skills/ocas-vesper/scripts/quality_check.py` (the profile skill directory). Run it as an absolute path — relative `scripts/quality_check.py` only works when CWD happens to be that directory. Call: `python3 ~/.hermes/profiles/indigo/skills/ocas-vesper/scripts/quality_check.py <briefing.json>`. It returns `PASS` or `FAIL — Quality check issues found:` with the failing terms.
- **`quality_check.py` field name mismatch** — The `scripts/quality_check.py` `check_sections_have_content` and `check_decisions_trace` functions now accept both field names: `summary` OR `text` for content items, `section_type` OR `id` for sections. The VesperBriefingFile schema uses `summary` and `section_type`. Always verify field names in `references/schemas.md` when modifying the quality script.
- **`content` field is REQUIRED in VesperBriefingFile** — The `references/schemas.md` VesperBriefingFile schema lists `content` as a string field, but it's easy to omit when building the sections array. The `quality_check.py` `check_greeting` function reads `briefing['content']` and will FAIL if the field is missing (it returns `''` and the greeting check fails with "expected 'Good morning ...'"). Always include `content` — it's the rendered plain-text version of the full briefing, with section markers and newlines. Build it as you build the sections array.

---

## 📊 Outputs

See `SKILL.md` for outputs, journals, and persistence rules.

---

## 📄 Files

| File | Purpose |
|---|---|
| `SKILL.md` | Skill definition |
| `references/` | Supporting documentation |
| `scripts/` | Helper scripts |


## Changelog

- [2.10.0] - 2026-04-26
- Added
- [2.9.0] - 2026-04-18
- Changed
- Added
- [2.8.4] - 2026-04-12
- Added
- [2026-04-04] Spec Compliance Update

---

## 📚 Documentation

Read `SKILL.md` for operational details, schemas, and validation rules.

Read `references/` for detailed specifications and examples.


---

## 📄 License

MIT License — see `LICENSE` for details.