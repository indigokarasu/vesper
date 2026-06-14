# Cron Mode Operations

Vesper runs as an isolated cron job. This constrains available tools and requires workarounds for common operations.

## Tool Constraints

- **`execute_code` is denied** — Python scripts cannot be run via execute_code. Use `terminal` with inline Python (`python3 -c "..."`) or heredoc (`python3 << 'EOF'`)
- **`patch` is unreliable for JSONL content** — The `read_file` tool wraps all output with `N|` line number prefixes. These prefixes do NOT exist in the actual file. When using `patch` on files that were read via `read_file`, the old_string may not match because the tool-added prefixes interfere. Workarounds:
  - Use `terminal` + `python3 -c` to load JSON, modify, and write back
  - Use `terminal` + `sed -i` for single-line surgical edits (without N| prefix)
  - Use `write_file` to rewrite entire file from parsed representation
  - Rule of thumb: if you read a file via `read_file` and need to edit it, use Python via terminal — never `patch`
- **`notify_on_complete` background processes** — `terminal(background=true)` works but `watch_patterns` fires max once per 15s per process. Use `notify_on_complete=true` for bounded tasks.

## Briefing Path Conventions

Briefings have a **canonical storage path** and may have a **requested delivery path**:

- Canonical: `{agent_root}/commons/data/ocas-vesper/briefings/YYYY-WXX/YYYY-MM-DD-{type}.json`
- JSONL index: `{agent_root}/commons/data/ocas-vesper/briefings.jsonl` (append-only, delivery tracking)
- If invocation instructions specify a flat path like `evening/2026-06-13-evening.json`, write there too, but the ISO week directory version is the canonical record
- Always append to `briefings.jsonl` AFTER the briefing file passes quality check — never before
- Both locations need their `delivered` / `delivery_status` flags updated on delivery

## JSONL Write Ordering (Critical)

The JSONL files (`briefings.jsonl`, `signals_evaluated.jsonl`, `decisions.jsonl`, `evidence.jsonl`) are append-only. Once appended, entries are never deleted — only superseded by new entries.

Correct order:
1. Generate briefing file in `briefings/YYYY-WXX/`
2. Run quality check on the file
3. Only if quality check passes: append to `briefings.jsonl`, `signals_evaluated.jsonl`, `decisions.jsonl`
4. Write journal

NEVER append JSONLs during the draft phase. A failed draft that has been appended to JSONL creates a ghost record that complicates delivery tracking.
