# Delivery Check Procedure

## When to Use

Run during any session that checks for undelivered briefings or finch reports — typically a scheduled delivery cron job or manual request.

## Checking Briefings

Two locations must be scanned — briefings live in both:

1. **Individual files**: `briefings/YYYY-WXX/YYYY-MM-DD-{type}.json`
2. **Master index**: `briefings.jsonl`

### Scanning for Undelivered Briefings

```bash
# Individual files
grep -rl '"delivered": false' <hermes-root>/commons/data/ocas-vesper/briefings/*/

# Master index
grep -c '"delivered": false' <hermes-root>/commons/data/ocas-vesper/briefings.jsonl
```

### Reading JSONL Safely

**IMPORTANT — Cron mode limitation:** `execute_code` is blocked in cron sessions. Use `terminal` + Python for structured edits.

**IMPORTANT — Corrupted N| prefixes:** If a previous `read_file` → `write_file` cycle wrote the tool's `N|` line-number prefixes into the file, lines will look like `27|{"briefing_id": ...}`. Before parsing, strip these prefixes:

```python
import json

lines = []
with open(jsonl_path, 'r') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        # Fix corrupted N| prefix from read_file/write_file round-trip
        if '|' in line and line.split('|', 1)[0].isdigit():
            line = line.split('|', 1)[1]
        entry = json.loads(line)
        lines.append(entry)
```

Each line is a JSON object. Check BOTH fields to determine delivery status:

```python
is_delivered = (
    entry.get('delivered', False)  # boolean flag
    or (
        entry.get('delivery_status', {}).get('status') == 'delivered'
        and entry.get('delivery_status', {}).get('delivered_at')  # has timestamp
    )
)
```

### delivery_status Has THREE Formats

The field can be:
1. A **plain string**: `"delivered"`, `"pending"`, or `"silent"`
2. An **object**: `{"status": "delivered", "delivered_at": "..."}`
3. An **object**: `{"status": "failed", "failed_at": "...", "reason": "..."}`

A briefing is **undelivered** if:
- `delivery_status` is `"pending"` (string form)
- `delivery_status.status` is `"failed"` or `"pending"` (object form)
- `delivered` is `false`, `null`, or absent

**Skip `"silent"` status** — intentionally suppressed briefings with no content, not failed deliveries.

### Flag Desync Fix

If `delivery_status.status == "delivered"` with a valid `delivered_at` but `delivered == false`, fix by setting `delivered = true`. The delivery timestamp is authoritative.

### Silent Entries

Entries with `delivery_status == "silent"` and empty `sections`/`content` were intentionally suppressed. Mark `delivered = true` to prevent re-checking.

### Entries With No Content

Entries with `delivered: false` but **no `content` field** (or `content: ""`) failed during generation — there is nothing to deliver. Mark as `delivery_status: "skipped"` with reason `"No content — generation failed"` to prevent re-checking. Do NOT attempt to send empty content.

## Delivery Methods

### Email (Primary)

Use `mcp_google_workspace_send_gmail_message` via MCP. Build HTML manually from the `content` field — no template file needed.

```python
# Convert plain-text content to simple HTML
html = "<p>" + content.replace("\n\n", "</p><p>").replace("\n", "<br>") + "</p>"
# Section headers: replace "▪ Today" with "<h3>▪ Today</h3>" etc.
```

**OAuth failures:** If `send_gmail_message` returns an auth error, update `delivery_status` with `{status: "failed", failed_at: <now>, reason: "Google OAuth..."}`. Do NOT retry in a loop — report the blocker and stop. OAuth reauthorization requires a browser login and cannot be completed in cron mode.

### Telegram (Fallback / Direct)

```bash
hermes send --to telegram:8666597030 --quiet "[content field from briefing]"
```

After sending, update the entry:
- `delivered: true`
- `delivery_status.status: "delivered"`
- `delivery_status.delivered_at: <ISO timestamp>`

## Post-Delivery Updates

After successful delivery, update **BOTH** locations:
1. The individual briefing file (`briefings/YYYY-WXX/YYYY-MM-DD-{type}.json`)
2. The master index (`briefings.jsonl`)

Use `terminal` + Python for structured JSONL edits. Never use `patch` on JSONL — the `N|` prefix can duplicate and corrupt lines.

## Checking Finch Output

Finch cron jobs (`finch:work`, `finch:scan`, `finch:daily`, `finch:weekly`) are **self-delivering** — they return their content or `[SILENT]` as the cron job's final response, and the cron system handles delivery automatically.

The files in `{agent_root}/cron/output/{job_id}/*.md` are **log artifacts**, not items requiring manual delivery. Do NOT send these via `hermes send`.

**Exception**: If a finch job's output contains actionable findings that should ALSO be surfaced in a briefing, that pathway goes through Vesper's normal signal aggregation (Corvus proposals, etc.), not direct delivery from cron output logs.

**Finch journal files are NOT deliverables.** The JSON files in `{agent_root}/commons/journals/ocas-finch/YYYY-MM-DD/` (e.g., `daily-HHMM.json`, `weekly-HHMM.json`, `scan-HHMM.json`) are internal action journals — structured logs of what the finch run found and applied. They are NOT reports to deliver to the user. The finch cron job's own output (delivered automatically by the cron system) IS the report. Never send finch journal files via `hermes send`.

## Report Format

After checking, report:
1. Number of briefings delivered (if any)
2. Number of flag desyncs fixed (if any)
3. Any blockers (e.g., OAuth expired)
4. `[SILENT]` if nothing to deliver
