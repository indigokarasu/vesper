# Delivery Check Procedure

## When to Use

Run during any session that checks for undelivered briefings or finch reports — typically a scheduled delivery cron job or manual request.

## Checking Briefings

Two locations must be scanned — briefings live in both:

1. **Individual files**: `briefings/YYYY-WXX/YYYY-MM-DD-{type}.json`
2. **Master index**: `briefings.jsonl`

### Scanning for Undelivered Briefings

**IMPORTANT:** `delivery_status` has three forms (string `"pending"`, object `{"status":"pending",...}`, or boolean `delivered: false/null`). A single grep will miss some forms. Use a Python scan for reliability:

```python
import json, glob

# Scan individual files
for path in glob.glob('<hermes-home>/commons/data/ocas-vesper/briefings/*/*.json'):
    d = json.load(open(path))
    delivered = d.get('delivered')
    ds = d.get('delivery_status', {})
    if isinstance(ds, str):
        is_delivered = ds == 'delivered'
    elif isinstance(ds, dict):
        is_delivered = ds.get('status') == 'delivered' and ds.get('delivered_at')
    else:
        is_delivered = delivered is True
    if not is_delivered and d.get('content'):
        print(f"UNDELIVERED: {path}")
```

Quick grep checks (catch common forms but may miss object-form pending):
```bash
# Individual files — boolean false
grep -rl '"delivered": false' <hermes-home>/commons/data/ocas-vesper/briefings/*/
# Individual files — string pending
grep -rl '"delivery_status": *"pending"' <hermes-home>/commons/data/ocas-vesper/briefings/*/
# Individual files — JSON null delivered
grep -rl '"delivered": *null' <hermes-home>/commons/data/ocas-vesper/briefings/*/
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

### Known Desync Patterns

1. **`delivered: null` + `delivery_status: "delivered"` (individual file)** — The top-level boolean was never set but delivery succeeded. Fix: set `delivered: true`. Check both fields independently.

2. **JSONL `delivery_status: "draft"` + individual file says delivered** — The JSONL entry got stuck in an intermediate "draft" state while the individual file was properly marked delivered. Fix: update JSONL to match the individual file's delivery_status. Always cross-reference JSONL against individual files before treating "draft" as undelivered.

3. **`delivered_at: null` at top level + `delivery_status.delivered_at` has timestamp** — The nested field was set but the top-level mirror wasn't. Fix: copy the timestamp to the top-level `delivered_at` field.

### Silent Entries

Entries with `delivery_status == "silent"` and empty `sections`/`content` were intentionally suppressed. Mark `delivered = true` to prevent re-checking.

### Entries With No Content

Entries with `delivered: false` but **no `content` field** (or `content: ""`) failed during generation — there is nothing to deliver. Mark as `delivery_status: "skipped"` with reason `"No content — generation failed"` to prevent re-checking. Do NOT attempt to send empty content.

## Delivery Methods

### Email (Primary)

Use `mcp_google_workspace_send_gmail_message` via MCP. Build HTML manually from the `content` field — no template file needed.

```python
# Convert plain-text content to simple HTML
# Handle section headers (lines starting with ▪ ✉ ⚑ ◈ ⟡ ⚙)
import re
lines = content.split('\n')
html_parts = []
for line in lines:
    stripped = line.strip()
    if not stripped:
        html_parts.append('')
        continue
    if stripped and stripped[0] in '▪✉⚑◈⟡⚙':
        header_text = stripped[2:].strip() if len(stripped) > 2 else stripped
        html_parts.append(f'<p><strong>{stripped[0]} {header_text}</strong></p>')
    else:
        html_parts.append(stripped)

# Wrap non-header lines in <p> tags, join paragraphs
result = []
in_para = False
for part in html_parts:
    if not part:
        if in_para:
            result.append('</p>')
            in_para = False
        continue
    if not part.startswith('<p><strong>'):
        if not in_para:
            result.append('<p>')
            in_para = True
        result.append(part)
    else:
        if in_para:
            result.append('</p>')
            in_para = False
        result.append(part)
if in_para:
    result.append('</p>')

html = '\n'.join(result)
```

**OAuth failures:** If `send_gmail_message` returns an auth error, update `delivery_status` with `{status: "failed", failed_at: <now>, reason: "Google OAuth..."}`. Do NOT retry in a loop — report the blocker and stop. OAuth reauthorization requires a browser login and cannot be completed in cron mode.

### MCP Package Completely Missing

A more severe variant of "MCP unavailable": the `workspace_mcp` Python package is not installed in ANY environment. The entrypoint binary calls `python -m main` but the module doesn't exist anywhere.

**Diagnosis:**
```bash
pip list 2>/dev/null | grep -i workspace          # returns nothing
find / -name "workspace_mcp" -type d 2>/dev/null  # returns nothing
find / -name "__main__.py" -path "*workspace*" 2>/dev/null  # returns nothing
```

**Fix:** Reinstall the package into the venv referenced by the entrypoint binary, then verify.

**Workaround:** Deliver via Telegram (see above). Note: OAuth credentials may still be valid even when the package is missing — check `<gworkspace-creds>/credentials/` for token freshness before assuming auth is also broken.

### Telegram (Fallback / Direct)

Use when: (1) user requests immediate delivery, OR (2) MCP server is broken/unavailable during a cron delivery check.

```bash
hermes send --to telegram:OWNER_CHAT_ID --quiet "[content field from briefing]"
```

For full briefings, prepend the subject line as the first line of the message:
```
Evening Briefing — June 28

Good evening the owner
...
```

For stale briefings (e.g. a morning briefing delivered in the evening), add "(delayed delivery)" to the subject line:
```
Morning Briefing — June 28 (delayed delivery)

Good morning the owner
...
```

After sending, update the entry:
- `delivered: true`
- `delivery_status.status: "delivered"`
- `delivery_status.delivered_at: <ISO timestamp>`
- `delivery_status.method: "telegram"` (optional, for tracking fallback usage)

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
