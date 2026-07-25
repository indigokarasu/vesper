# Cron Mode Briefing Generation — End-to-End Workflow

This reference documents the complete workflow for generating a Vesper briefing in cron mode, including pitfalls encountered and their solutions.

## Tool Constraints in Cron Mode

- **`execute_code` is DENIED** — Cannot use `execute_code` in isolated cron sessions. Use `terminal` with Python one-liners or heredocs instead.
- **`write_file` works** — Safe for individual JSON files (briefing files, not JSONL).
- **`patch` is unreliable** — Especially after `read_file` (which adds `N|` line prefixes). Use `terminal` + Python for structured edits.
- **`delegate_task` works** — Subagents can run calendar queries, weather fetches, and Gmail searches in parallel.

## Path Resolution

**Critical**: In cron mode, relative paths in `read_file` may resolve incorrectly (the tool prepends the profile path). Always use absolute paths:

```
<hermes-home>/profiles/indigo/skills/ocas-vesper/references/<file>.md
<hermes-home>/commons/data/ocas-vesper/briefings/YYYY-WXX/<file>.json
<hermes-home>/commons/data/ocas-vesper/<file>.jsonl
```

If `read_file` fails with "File not found" on a path you expect to exist, use `terminal` + `find` to locate the actual file.

## Step-by-Step Workflow

### 1. Read references
Use absolute paths. Load `briefing_templates.md`, `signal_filtering.md`, `weather-codes.md`, `sparse-briefings.md`, `schemas.md` as needed.

### 2. Gather signals in parallel
Use `delegate_task` with up to 3 subagents:
- Weather: `terminal` + `curl` to Open-Meteo API
- Calendar: `mcp_google_workspace_get_events` (direct MCP)
- Gmail: `mcp_google_workspace_search_gmail_messages` (direct MCP)

Subagent Gmail OAuth may fail — always have a direct fallback in the parent session.

### 3. Build the briefing JSON
**Must include `content` field** — The VesperBriefingFile schema requires `content` (rendered plain-text briefing). The quality check's `check_greeting` reads this field. Without it, the check fails.

Build `content` as a plain-text string with:
- Greeting as first line ("Good morning the owner" / "Good evening the owner", no punctuation after)
- Weather paragraph (morning only)
- Section markers (▪ ✉ ⚑ ◈ ⟡ ⚙) followed by content
- Double newline between sections

**Do NOT include `signals_consumed`** — This field is not in the schema and causes the quality check's `check_signals_evaluated` to fail if `signals_evaluated.jsonl` hasn't been written yet.

### 4. Write the briefing file
Use `terminal` + Python `json.dump` for reliability:

```python
import json
with open(path, 'w') as f:
    json.dump(briefing, f, indent=2, ensure_ascii=False)
```

Avoid heredoc JSON — special characters (em dashes, smart quotes, emoji) can corrupt the heredoc.

### 5. Run quality check
```bash
python3 scripts/quality_check.py <briefing-file.json>
```

Do NOT pass the signals_evaluated path unless you've already appended to it (which violates the draft→check→finalize ordering).

### 6. Finalize (after quality check passes)
- Append to `briefings.jsonl` — **must use Python `json.dump`**, NOT heredoc. Emoji section markers (⟡, ▪, �) and smart quotes corrupt in raw heredocs. Pattern:
  ```bash
  python3 -c "
  import json
  record = {
    'briefing_id': '...',
    'type': 'evening',
    ...
    'sections': [...]
  }
  with open('<hermes-home>/commons/data/ocas-vesper/briefings.jsonl', 'a') as f:
      json.dump(record, f, ensure_ascii=False)
      f.write('\n')
  "
  ```
- Append to `signals_evaluated.jsonl` (one evaluation record per line)
- Write journal to `journals/ocas-vesper/YYYY-MM-DD/{run_id}.json`

Each `signals_evaluated.jsonl` entry should include:
- `signal_id` — unique identifier for the signal
- `source` — which skill or system produced it (e.g., `gmail`, `ocas-dispatch`, `ocas-sands`)
- `relevance_score` — 0.0 to 1.0
- `included` — boolean, whether it appeared in the briefing
- `exclusion_reason` — required when `included: false`, explains why (e.g., "routine notification, limit already reset, no longer actionable")

### 7. Handle delivery flags correctly
If the user says "save locally only" or "do NOT deliver":
- Set `delivered: false` in the briefing file
- Set `delivery_status: {"status": "draft"}` in the briefing file
- Set `delivered: false` in the JSONL entry

If you accidentally set `delivered: true` during the JSONL append, fix it immediately with `terminal` + Python (read, modify, rewrite the JSONL).

#### User-specified subdirectory paths
When the user specifies a destination like `evening/` or `morning/`:
- Save a copy to the requested path (e.g., `evening/2026-06-27-evening.json`)
- The canonical file must ALWAYS go to `briefings/YYYY-WXX/YYYY-MM-DD-{type}.json`
- Both files must be byte-identical at write time (use `cp` or read+verify)
- Delivery tracking (briefings.jsonl) applies ONLY to the canonical path
- Do NOT put delivery tracking (delivered/delivery_status) in the copy — treat it as a reference mirror
- Journal should note the divergence: canonical path is the delivery contract, user-path is informational

## Common Pitfalls

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| Missing `content` field | Quality check: "greeting is '', expected 'Good morning ...'" | Add `content` with rendered text |
| `signals_consumed` in briefing | Quality check: "Signals consumed but not in signals_evaluated.jsonl" | Remove `signals_consumed` from briefing JSON |
| Heredoc JSON corruption | `JSONDecodeError` or garbled Unicode | Use `terminal` + Python `json.dump` |
| `read_file` path not found | "File not found" on expected paths | Use absolute paths or `terminal` + `find` |
| `delivered` accidentally set true | Briefing marked as delivered when it wasn't | Fix with Python: read JSONL, modify last entry, rewrite |
| User requests `evening/` or `morning/` path | Briefing saved to wrong location, delivery tracking broken | Always write canonical to `briefings/YYYY-WXX/`, then `cp` a byte-identical copy to the requested path |
| Weather-only briefing (all signals absent) | Added empty section object as placeholder, quality check failed on `check_sections_have_content` | Use `"sections": []` — no section objects when there is no actionable content beyond weather |
| Heredoc emoji corruption | Section markers (⟡, ▪, ✉) become garbled in the JSONL entry (e.g., `"Decisions"` loses its `⟡` marker), making downstream parsing or display fail | Use `terminal` + `python3 -c "import json,sys; data=json.load(open('briefing.json')); ..."` or write a temp Python script — never raw heredoc for JSON containing Unicode |
