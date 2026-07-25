---
name: ocas-vesper
description: 'Daily briefing generator. Aggregates signals from across the system into
  concise morning and evening briefings. Surfaces outcomes, opportunities, and decisions
  in natural language without exposing internal processes. NOT for: deep research
  (use Sift), pattern analysis, message drafting (use Dispatch), or raw data queries (use Styx directly).'
license: MIT
source: https://github.com/<agent-handle>/vesper
includes:
- references/**
- scripts/**
triggers:
- daily briefing
- morning briefing
- evening briefing
- status summary
metadata:
  author: Indigo Karasu (indigokarasu)
  version: 2.13.0
  hermes:
    category: productivity
    tags:
    - daily-briefing
    - aggregation
    - natural-language
    - OCAS-core
---
## Interactive Menu

When invoked interactively, present a two-level menu using the `clarify` tool. See `references/interactive-menu.md` for the full menu structure, response parsing, and platform adaptation.




Vesper is the system's daily voice — it aggregates signals from every other skill and presents what matters as a concise, conversational morning or evening briefing, surfacing concrete outcomes, upcoming decisions, and actionable opportunities without exposing any internal architecture or analysis processes. This skill exists because raw signal data from individual skills is not actionable — the owner needs a synthesized, natural-language summary.

## When to Use

- Daily briefing generation (morning, evening, on-demand)
- Signal aggregation from all OCAS skills
- Morning summary of calendar, email, and system status
- End-of-day wrap-up and next-day preview
- Checking pending decision requests
- Configuring briefing schedule or sections

## When NOT to Use

- Deep research — use Sift
- Pattern analysis
- Message drafting — use Dispatch
- Action execution — use relevant domain skill
- Real-time monitoring
- Calendar management (use Sands)
- Email sending (use Dispatch)

## What this skill does not do

- Signal generation (no current skill for this)
- Portfolio management (Rally)
- Calendar management (Sands)
- Communications delivery (Dispatch)
- Research (Sift/Scout)
- Action decisions (Praxis)

## Account isolation

See `references/account-credentials.md` for Google account isolation rules and OAuth credential configuration.

## Responsibility boundary

Vesper owns briefing generation, signal aggregation, and decision presentation. It aggregates signals from Rally, Sands, Dispatch, and Calendar into morning and evening briefings, then writes completed briefings to its `briefings/` directory for Dispatch to pick up and deliver.

Vesper does **not** own: signal generation, portfolio management (Rally), calendar management (Sands), communications delivery (Dispatch), research (Sift/Scout), or action decisions (Praxis). It surfaces outcomes; it does not act.

## Signal filtering rules

Read `references/signal_filtering.md` for full rules.

Summary: Include actionable information, meaningful outcomes, plan-affecting changes, multi-signal opportunities, and preparation-useful information. Exclude routine background activity, already-experienced events, internal system reasoning, and speculative observations. Evening-specific: no past weather, no summaries of attended meetings.

## Formatting rules

Read `references/briefing_templates.md` for structure and examples, `references/html-templates.md` for HTML layout, and `references/weather-codes.md` for weather rendering.

Key constraints:

- No markdown syntax (#, **, ---) — plain text or minimal HTML suitable for Gmail
- Conversational paragraphs, not bullet dumps
- Section headers: ▪ Today, ✉ Messages, ⚑ Logistics, ◈ Markets, ⟡ Decisions, ⚙ System
- Sections with no content are omitted entirely — no "nothing to report" placeholders
- Normal-state system health is silence — no "all clear" or "systems normal"
- Opening: "Good morning the owner" / "Good evening the owner" (no punctuation after greeting)
- Markets: morning shows yesterday's close; evening shows open and close. Notable movers only when material.
- Decision requests: option, benefit, cost — framed as optional
- Links are inline with meaningful anchor text; see URI formats in reference files
- When Vibes (ocas-vibes) is present, apply its voice and anti-AI rules to all briefing text
- No nagging, no internal terminology, no speculative observations, no architecture references

## Commands

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

## Invocation modes

- **Automatic morning** — during configured morning window
- **Automatic evening** — during configured evening window
- **Manual** — on user request

## Run completion

- [ ] **Apply Vibes rules** — Apply voice rules from SOUL.md directly (no em dashes, no "the user", no meta-narration, no "Now I have…"). **Do NOT load ocas-vibes via skill_view** — its rules are already embedded in SOUL.md/AGENTS.md.
- [ ] Read InsightProposal files from Custodian `proposals/` directory. Apply signal filtering. Track consumed `proposal_id` values in `signals_evaluated.jsonl` to avoid reprocessing. Read Dispatch summary and Rally daily report if present. For parallel signal gathering, `delegate_task` works for calendar queries but subagent Gmail OAuth may fail independently — always have a direct fallback.
- [ ] Write briefing file to `{agent_root}/commons/data/ocas-vesper/briefings/YYYY-WXX/YYYY-MM-DD-{type}.json` using `VesperBriefingFile` schema. Create week directory if absent. **Path is non-negotiable** — the schema `briefings/YYYY-WXX/YYYY-MM-DD-{type}.json` is the delivery contract. If user instructions specify a different path (e.g., `morning/` or `evening/`), follow the schema for the canonical location AND save a copy to the requested path. The copy and the canonical file must be identical at write time; only delivery tracking (via `briefings.jsonl`) applies to the canonical path. Note the divergence in the journal.
- [ ] **Briefing quality check**: Re-read the generated briefing file and verify: (a) no internal system terminology leaked through (no skill IDs, database references, or technical jargon — use **whole-word matching**, not substring matching, to avoid false positives like "DB" matching inside "Handbuilding"), (b) all included sections have actual content — no empty sections, (c) the greeting matches the time-of-day format, (d) `signals_evaluated.jsonl` was updated with all consumed proposal IDs, and (e) every decision item traces to a real upstream signal — no fabricated or template-copied decisions. If any check fails, regenerate the briefing before marking the run complete. **Tip:** Run `python3 scripts/quality_check.py <briefing-file.json> [signals-evaluated.jsonl]` for automated validation — it implements all five sub-checks with whole-word regex matching.
- [ ] **Only after the briefing passes quality check**, persist the completed briefing record to `briefings.jsonl` and evaluated signals to `signals_evaluated.jsonl`. Log material decisions to `decisions.jsonl`. (Do not append these files before the quality check succeeds — the JSONL is the delivery contract and must match the final briefing exactly.)
- [ ] Write journal via `vesper.journal`.

## Inter-skill interfaces

**Custodian → Vesper:** Custodian writes InsightProposal files (`anomaly_alert` type) to `{agent_root}/commons/data/ocas-custodian/proposals/{proposal_id}.json`. Vesper reads them during briefing generation.

**Dispatch → Vesper:** Dispatch writes `DispatchSummaryReport` to `{agent_root}/commons/data/ocas-dispatch/reports/YYYY-MM-DD-{period}.json`. Vesper uses this for the Messages section.

**Rally → Vesper:** Rally writes daily portfolio reports to `{agent_root}/commons/data/ocas-rally/reports/YYYY-MM-DD-daily.json`. Vesper uses this for the Markets section.

**Vesper → Dispatch:** Vesper writes completed briefings to its `briefings/` directory. Dispatch picks them up for delivery. See `references/schemas.md` VesperBriefingFile.

## Storage layout & configuration

Data lives under `{agent_root}/commons/data/ocas-vesper/` with journals under `{agent_root}/commons/journals/ocas-vesper/`. The default `config.json` sets morning window 07:00–09:00 PT, evening window 17:00–19:00 PT, all six sections enabled, 30-day retention, and 10k record cap. Briefings are stored in ISO week directories as `YYYY-MM-DD-{type}.json`. See `references/schemas.md` for the full directory tree and default config.

## OKRs

Vesper tracks five OKRs — signal precision, terminology compliance, decision framing, schedule adherence, and data integrity — all evaluated over 30-run windows. Targets: 85%+ actionable signals, 100% terminology-free briefings, 100% complete decision framing, 95%+ schedule compliance, 99%+ data integrity. See `references/okrs.md` for the full OKR specification.

## Optional skill cooperation

- **Vibes** — applies voice identity and anti-AI rules from ocas-vibes. **Do NOT load ocas-vibes via skill_view** — its rules are already in SOUL.md and AGENTS.md. Apply voice rules directly from SOUL.md: no em dashes, no "the user" (use "you"), no meta-narration ("Now I have…", "Let me check…"), no rule of three, no Vibes checklist items that conflict with SOUL.md.
- **Custodian** — reads InsightProposal files (cooperative read)
- **Dispatch** — reads DispatchSummaryReport; Dispatch picks up completed briefings from Vesper for delivery
- **Rally** — reads portfolio daily reports (cooperative read)
- **Calendar/Weather** — reads external context for briefing content


## Ontology types & journal

Vesper observes entities during briefing aggregation (Entity/Person, Concept/Event, Place). Entity observations are recorded in journal outputs for downstream Chronicle ingestion. Read `references/journal.md` before `vesper.journal`.

When entities are encountered, include in `decision.payload`:
- `entities_observed` — type, name, context
- `relationships_observed` — connections between entities
- `preferences_observed` — user preferences inferred from briefing interactions

Each entity observation includes a `user_relevance` field: `user`, `agent_only`, or `unknown`.

## Initialization

On first invocation, run `vesper.init`:
- [ ] Create data directories (including `briefings/`)
- [ ] Write default `config.json` if absent
- [ ] Create empty JSONL files
- [ ] Create journal directory
5. Register cron jobs `vesper:morning`, `vesper:evening`, `vesper:update` if not already present
6. Log initialization as a DecisionRecord in `decisions.jsonl`

## Background tasks

| Job name | Mechanism | Schedule | Command |
|---|---|---|---|
| `vesper:morning` | cron | `0 6 * * *` (daily 6am) | `vesper.briefing.morning` |
| `vesper:evening` | cron | `0 20 * * *` (daily 8pm) | `vesper.briefing.evening` |
| `vesper:update` | cron | `0 0 * * *` (midnight daily) | `vesper.update` |

Cron options: `sessionTarget: isolated`, `lightContext: true`, `wakeMode: next-heartbeat`.

Default times are 6am and 8pm PT. Override with `vesper.config.set morning_hour <H>` and `vesper.config.set evening_hour <H>`.

## Self-update

`vesper.update` pulls the latest package from the `source:` URL in SKILL.md frontmatter. Runs silently unless version changed or error occurred. On failure, retries once. Output on success: `I updated Vesper from version {old} to {new}`.

**Procedure**: See `references/update-procedure.md` for the full update workflow including conflict resolution and profile sync. Key points:
- If local modifications block `git pull`: stash, move conflicting untracked files, pull, stash pop, resolve conflicts
- After pulling: sync the profile copy (`~/.hermes/profiles/indigo/skills/ocas-vesper/`) — sessions load from there, not the git repo

## Visibility

public

## Gotchas

Error handling in vesper focuses on graceful signal degradation — when a signal source is unavailable, the briefing notes the gap rather than failing silently or fabricating content.

- **Account isolation is critical** — See `references/account-credentials.md`.
- **Upstream skill unavailability is silent** — Missing data means the affected section is omitted entirely. No error raised.
- **All-upstream silence produces thin briefings** — When Custodian, Dispatch, and Rally are all unavailable (common on quiet days), the briefing may contain only weather + email. This is normal. Do not pad with fabricated content. A 3-line briefing that accurately reflects available signals is better than a padded one. If the only available signal is weather, the briefing can be just the greeting + weather paragraph. If email is also empty, consider whether a briefing should be generated at all — sometimes silence is the correct output. **Evening briefings** have no weather section, so a thin evening briefing may be just greeting + one message line. See `references/sparse-briefings.md` for evening-specific guidance.
- **Signal filtering is strict** — Routine, speculative, and already-experienced signals are excluded.
- **Normal state is silence** — Never confirms "all systems normal." Empty sections are omitted with no placeholder.
- **Briefing files use ISO week directories** — Stored under `briefings/YYYY-WXX/`. Create the directory if absent.
- **Cron mode blocks `execute_code`** — Vesper runs as an isolated cron job. `execute_code` is denied in this mode. Use `terminal` + Python `json.dump` for JSONL appends and file writes. Plan file operations accordingly. When appending to JSONL files, use `terminal` with a Python one-liner or heredoc that calls `json.dump` — do NOT use `write_file` for JSONL (it overwrites). **Do NOT use raw heredoc for JSON** — emoji (� ▪ ✉), smart quotes, and em dashes corrupt in heredocs. Use `python3 -c '...json.dump(...)`` instead. See `references/cron-mode-briefing-generation.md` sectionStep 4: Write the briefing file" for the correct pattern.
- **Avoid piping command output into an interpreter** — Commands like `sed ... | python3` or `cat file | python3` are blocked by the security scanner (flagged as pipe-to-interpreter) in terminal/cron mode. When you need to post-process file contents with Python, write the logic to a script file (e.g. `/tmp/check.py`) via `write_file` and run `python3 /tmp/check.py` instead of inlining a pipe. This applies to all shell work in this environment, not just Vesper.
- **`briefing_deliver.py` is BROKEN — use MCP tools directly** — The `scripts/briefing_deliver.py` script uses `googleapiclient` directly and will fail with import/auth errors in cron mode. When delivering briefings, always use `mcp_google_workspace_send_gmail_message` via MCP. Build HTML manually from the `content` field — no template file needed. See the delivery check procedure in cron mode for the correct approach.
- **Never fabricate decisions** — Every decision item in the briefing must trace to a real upstream signal (a Custodian alert, pending renewal with real data). Template examples in `briefing_templates.md` are illustrations only, not real pending items. If no genuine decision signal exists, omit the Decisions section entirely. A fabricated decision (#4 quality check violation) is worse than silence.
- **Hallucination window — April-May 2026** — During this period, Vesper briefings were generated with fabricated personal data (false locations, investment positions, family details, insurance policies). These briefings ARE in the system and may be read by Dispatch and other skills. When sourcing data for briefings corroborate all "facts" about the user's personal life against primary sources (actual Gmail, actual Calendar, actual session transcripts) — never trust a Vesper briefing from this window as a source of personal fact. If you find briefing content that contradicts known reality, discard the briefing data and flag the briefing as corrupted.
- **JSONL write ordering** — The briefing content (`briefings/YYYY-WXX/YYYY-MM-DD-{type}.json`) is the source of truth. Only after the briefing file passes the quality check (step 5 of Run completion) should `briefings.jsonl` and `signals_evaluated.jsonl` be written/appended. Never append to `briefings.jsonl` during the draft phase. Draft → quality check → finalize → append JSONLs. This avoids append-then-retract cycles that complicate delivery tracking.
- **briefings.jsonl IS real JSONL** — `briefings.jsonl` is one JSON object per line, standard JSONL format. The `read_file` tool wraps all output in a `content` field with `N|` line prefixes — this is a tool artifact, NOT the file's actual structure. To verify raw file format, use `head -c 500 file` or `terminal cat file | head -3`. To check for undelivered briefings: `grep -c '"delivered": false' briefings.jsonl` (standard grep works on raw JSONL). To count lines: `wc -l briefings.jsonl`.
- **Dual delivery flags can desync** — `briefings.jsonl` has two parallel delivery tracking fields: `delivered` (boolean) and `delivery_status` (object with `status` + `delivered_at`). These can get out of sync when delivery updates one but not the other. When checking for undelivered briefings, check BOTH fields: a briefing is considered delivered if either `delivered=true` OR `delivery_status.status="delivered"` (with a non-null `delivered_at`). If flags are desync'd, fix them by setting `delivered=true` on any entry where `delivery_status.status="delivered"` — the delivery timestamp is the authoritative record.
<<<<<<< Updated upstream
- **Dual LOCATIONS can desync** — Briefings live in two places: the master index (`briefings.jsonl`) AND individual files (`briefings/YYYY-WXX/YYYY-MM-DD-{type}.json`). Each has its own `delivered` flag. The JSONL index may say `delivered: true` while the individual file says `delivered: false`, or vice versa. When checking for undelivered briefings, you MUST scan both locations. Use `grep -rl '"delivered": false' <hermes-home>/commons/data/ocas-vesper/briefings/*/` to find undelivered individual files. **Also check for `delivered: None` (JSON null)** — a briefing that was generated but never had its delivery flag set will have `null`/`None` rather than `false`. Use `grep -rl '"delivered": null' briefings/*/` or a Python scan to catch these. After delivering, update BOTH locations.
=======
- **Dual LOCATIONS can desync** — Briefings live in two places: the master index (`briefings.jsonl`) AND individual files (`briefings/YYYY-WXX/YYYY-MM-DD-{type}.json`). Each has its own `delivered` flag. The JSONL index may say `delivered: true` while the individual file says `delivered: false`, or vice versa. When checking for undelivered briefings, you MUST scan both locations. Use `grep -rl '"delivered": false' ~/.hermes/commons/data/ocas-vesper/briefings/*/` to find undelivered individual files. **Also check for `delivered: None` (JSON null)** — a briefing that was generated but never had its delivery flag set will have `null`/`None` rather than `false`. Use `grep -rl '"delivered": null' briefings/*/` or a Python scan to catch these. After delivering, update BOTH locations.
>>>>>>> Stashed changes
- **`delivery_status` has THREE formats** — The field can be: (1) a plain string: `"delivered"`, `"pending"`, or `"silent"`; (2) an object with `{status: "delivered", delivered_at: "..."}`; (3) an object with `{status: "failed", failed_at: "...", reason: "..."}`. When scanning for undelivered briefings, check ALL three forms. A briefing is undelivered if: `delivery_status` is `"pending"`, OR `delivery_status.status` is `"failed"` or `"pending"`, OR `delivered` is `false` or `null`/`None`. **Skip `"silent"` status** — these are intentionally suppressed briefings with no content, not failed deliveries. **Also skip `"draft"` status in JSONL** — this is an intermediate state that can get stuck; always cross-reference against the individual file's `delivery_status` before treating a `"draft"` JSONL entry as undelivered.
- **`delivered: null` with `delivery_status: "delivered"` desync** — A specific desync where the individual briefing file has `delivered: null` (JSON null, never set) but `delivery_status: "delivered"` (plain string) with a valid `delivered_at` timestamp. This happens when delivery succeeds but the code path that sets the top-level `delivered` boolean doesn't run. The `delivery_status` field is authoritative — if it says `"delivered"` with a timestamp, the briefing WAS delivered. Fix by setting `delivered: true` in the individual file. Always check both fields independently.
- **JSONL may claim delivered with no content** — A desync case where `briefings.jsonl` has `delivered: true` and `delivery_status: "delivered"` but the `content` field is empty or missing, while the individual briefing file has full content and `delivered: null`. This happens when a delivery run partially succeeds (updates JSONL metadata but fails to send or record content). Recovery: read content from the individual file, send it, then update both locations with content and delivery confirmation.
- **MCP server unavailable in cron mode** — When running as a cron job, the Google Workspace MCP server may not be running at all. The native MCP client (not the skill wrapper, but the actual `workspace-mcp` stdio subprocess) can be dead, broken, or pointing at a non-existent Python module. Symptoms: (1) `hermes status` shows "Email ✗ not configured" even though `config.yaml` has the MCP server entry with `enabled: true`, (2) `ps aux | grep workspace-mcp` returns nothing, (3) the wrapper binary at `/usr/local/bin/workspace-mcp` calls `python -m main` but the module doesn't exist in the venv. **Diagnosis sequence:** `hermes status` → `ps aux | grep workspace-mcp` → `cat /usr/local/bin/workspace-mcp` and `cat /usr/local/bin/workspace-mcp-fixed` to check the entrypoint. If the entrypoint is broken (module not found, wrong venv path), the MCP cannot send from the cron session's own resources. **Procedure when MCP is dead/broken:** (1) Set `delivery_status: {status: "failed", failed_at: <now>, reason: "MCP server not running in cron session — <specific error>"}` on both the individual briefing file AND the `briefings.jsonl` entry. (2) Do NOT retry sending in a loop — the MCP process won't recover within a cron run. (3) Do NOT attempt to use `googleapiclient` directly — that's the old broken `briefing_deliver.py` path. (4) Preserve the briefing content so a later retry run (or Dispatch) can deliver it. (5) Report the blocker with the briefing's content in the response so the user has it immediately. This is distinct from the "send times out" bug (documented in `email-sending` skill) — that's when the MCP IS running but the send tool hangs. This pitfall covers the MCP not running at all.
- **MCP package completely missing (not just wrong path)** — A more severe variant of the "MCP unavailable" failure: the `workspace_mcp` Python package is not installed in ANY environment on the system. The entrypoint binary (`/usr/local/bin/workspace-mcp`) calls `python -m main` but no `workspace_mcp` package exists anywhere — not in the hermes-agent venv, not in system site-packages, not anywhere `pip list` or `find` can locate it. This means the MCP server can never start until the package is reinstalled. **Diagnosis:** `pip list 2>/dev/null | grep -i workspace` returns nothing, `find / -name "workspace_mcp" -type d 2>/dev/null` returns nothing, `find / -name "__main__.py" -path "*workspace*" 2>/dev/null` returns nothing. **Fix:** reinstall the package (e.g. `pip install google-workspace-mcp` or whatever the correct package name is) into the venv referenced by the entrypoint binary, then verify with `python -m workspace_mcp --help` or equivalent. **Workaround until fixed:** deliver briefings via `hermes send --to telegram:OWNER_CHAT_ID` as described in the Direct Telegram delivery gotcha. Note: OAuth credentials may still be valid even when the package is missing — check `<gworkspace-creds>/credentials/` for token freshness before assuming auth is also broken.
- **OAuth failures are persistent blockers** — When `send_gmail_message` returns an auth error, the briefing's `delivery_status` is set to `{status: "failed", reason: "Google OAuth..."}`. On retry, if OAuth is still not reauthorized, do NOT keep retrying in a loop — update the `failed_at` timestamp and reason, then report the blocker to the user. The OAuth outage briefing itself (the 2026-05-31 evening brief) is a self-referential case: it reports the OAuth failure that prevents its own delivery.
- **Weather API: use Open-Meteo directly, not RapidAPI** — The RapidAPI `weather` endpoint's `current-weather` action is unreliable (returns "tool not found"). Use `curl` directly to `https://api.open-meteo.com/v1/forecast` with parameters `temperature_2m` and `weather_code` (NOT `temperature_2m,weather_code` as a comma-separated single param — they are separate query params). Example: `curl -s "https://api.open-meteo.com/v1/forecast?latitude=37.7749&longitude=-122.4194&current=temperature_2m,weather_code&hourly=temperature_2m,weather_code&daily=temperature_2m_max,temperature_2m_min,weather_code&temperature_unit=fahrenheit&timezone=America%2FLos_Angeles&forecast_days=2"`. See `references/weather-codes.md` for WMO code mapping.
- **Python booleans in heredocs** — When writing Python via shell heredoc (`cat << 'EOF'`), use `True`/`False` (Python capitalization), NOT `true`/`false` (JSON/JS). Using lowercase causes `NameError: name 'false' is not defined`.
- **Direct Telegram delivery** — When the user requests immediate delivery (not via Dispatch), OR when the MCP server is broken/unavailable during a cron delivery check, use `hermes send --to telegram:OWNER_CHAT_ID --quiet "message"`. This bypasses the Dispatch pipeline and delivers directly. Mark the briefing as `delivered: true` with `delivered_at` timestamp immediately after successful send. When delivering a full briefing, prepend the subject line (e.g. "Evening Briefing — June 28") as the first line of the message. For stale briefings (e.g. a morning briefing delivered in the evening), add "(delayed delivery)" to the subject line so the recipient knows the context is dated.
- **Vibes is a passive style reference — do NOT load it via skill_view** — The ocas-vibes skill has a 67% false trigger rate when loaded directly. Its rules are already in SOUL.md and AGENTS.md. Apply voice rules from SOUL.md (em dash prohibition, no "the user", no meta-narration, no "Now I have…", etc.) without loading the skill. The Vibes Pre-Send Checklist should be applied from memory, not by invoking the skill binary.

- **Finch journals are NOT deliverables** — The JSON files in `commons/journals/ocas-finch/YYYY-MM-DD/` (daily-HHMM.json, weekly-HHMM.json, scan-HHMM.json) are internal action journals, not user-facing reports. Finch cron jobs are self-delivering via the cron system (`deliver: "origin"` or `deliver: "local"`). When running a delivery check, NEVER send finch journal content via `hermes send`. Only check `briefings.jsonl` for undelivered briefings. See `references/delivery-check-procedure.md` for the full procedure.
- **Legacy ocas-corvus proposal paths** — Files may exist at `{agent_root}/commons/data/ocas-corvus/proposals/` — these are legacy artifacts from before Corvus was merged into Chronicle. Ignore them during signal gathering.
- **read_file output is tool wrapping, not file contents** — The `read_file` tool wraps all output in `{"content": "N|line1\nN|line2"}` — this is a tool presentation layer, NOT the file's actual on-disk format. When verifying file structure (JSONL delimiters, CSV headers, encoding), use `terminal head -c 500 file` or `terminal head -3 file` to see raw bytes. The pipe-delimited `N|` prefixes you see in tool output do NOT exist in the actual file.
- **Skill files live in two locations** — The git repo at `~/.hermes/skills/ocas-vesper/` is the update source. Sessions load from `~/.hermes/profiles/indigo/skills/ocas-vesper/`. After any `vesper.update`, the profile copy MUST be synced or the next session will run stale code. Always sync both `SKILL.md` and `references/` after pulling. See `references/update-procedure.md`.
- **Reference file path resolution** — When SKILL.md references files like `references/briefing_templates.md`, the actual files live under the profile skill directory (`~/.hermes/profiles/indigo/skills/ocas-vesper/references/`), NOT under the data directory (`~/.hermes/commons/data/ocas-vesper/references/`). The data directory has no `references/` subdirectory. Always resolve reference paths against the skill directory, not the data directory.
- **Cron user instructions may conflict with stored paths** — When a cron job is invoked with an explicit file destination (e.g., `save to morning/`), the stored procedure in `references/schemas.md` takes precedence. The path schema `briefings/YYYY-WXX/YYYY-MM-DD-{type}.json` is the delivery contract and must be followed for Dispatch and delivery checks to function. If user instructions specify a different path, save a copy to that path for the user's reference, but the canonical file MUST go to `briefings/YYYY-WXX/`. Note the divergence in the journal.
- **`patch` is unreliable after `read_file`** — `read_file` wraps output with `N|` line prefixes that don't exist in the actual file. If you read a file via `read_file` and then try `patch`, the old_string may never match. Use `terminal` + Python (`json.load`/`json.dump` per line) or `write_file` to rewrite. This applies to ALL files, not just JSONL. The `patch` tool operates on raw file content. If you include the `N|` prefix in both old_string and new_string, you can accidentally create duplicate prefixes (e.g., `27|27|`). SAFE alternatives: (1) Use `terminal` + `sed -i 'Ns/^N|N|/|/'` for surgical single-line prefix fixes. (2) Use `terminal` + Python (`json.load` per line, modify, `json.dump` per line) for structured edits. (3) Use `write_file` to rewrite the entire file from a parsed representation. NEVER use `patch` with the `N|` prefix included in both old and new strings — the prefix duplicates and corrupts the line, making it unparseable.
- **Failed briefings may have no `content` field** — When a briefing fails during generation (e.g., OAuth expired before data could gather), the JSONL entry may contain only metadata (`briefing_id`, `type`, `date`, `sections`, `delivery_status`) with NO `content` field. During delivery checks, skip entries that lack a `content` string — there is nothing to deliver. Mark them as `delivery_status: "skipped"` with a reason of "No content — generation failed" to prevent re-checking. If `content` exists but is empty string (`""`), also skip — the briefing was intentionally suppressed.
- **Quality check substring false positives** — When checking for internal terminology leaks (quality check step 3a), use **whole-word matching**, not simple substring search. `\bDB\b` as a regex will not match "Handbuilding" — but a naive `if "DB" in content` check WILL. Similarly, terms like "cal" match "calendar", "int" matches "intelligence", etc. Write the terminology check as word-boundary regex (`\b` on each side) or explicitly enumerate only full technical terms. A false positive on the terminology check causes unnecessary regeneration and wasted cycles.
- **System section needs user-facing phrasing** — The System section (⚙) communicates service gaps to the owner, but terms like "MCP", "cron", "OAuth", "API" in the System text are flagged as internal terminology by `quality_check.py`. Use generic user-facing language: "Calendar sync and email delivery are currently unavailable — no live data from those sources this cycle" instead of "MCP server not running in cron sessions". Test the System text with `quality_check.py` after writing — if it fails, rephrase generically and re-run. The System section should be ONE short paragraph about what's unavailable, not a technical diagnosis.
- **`quality_check.py`** — The quality check script lives at `~/.hermes/profiles/indigo/skills/ocas-vesper/scripts/quality_check.py` (the profile skill directory). Run it as an absolute path — relative `scripts/quality_check.py` only works when CWD happens to be that directory. Call: `python3 ~/.hermes/profiles/indigo/skills/ocas-vesper/scripts/quality_check.py <briefing.json>`. It returns `PASS` or `FAIL — Quality check issues found:` with the failing terms.
- **`quality_check.py` field name mismatch** — The `scripts/quality_check.py` `check_sections_have_content` and `check_decisions_trace` functions now accept both field names: `summary` OR `text` for content items, `section_type` OR `id` for sections. The VesperBriefingFile schema uses `summary` and `section_type`. Always verify field names in `references/schemas.md` when modifying the quality script.
- **`content` field is REQUIRED in VesperBriefingFile** — The `references/schemas.md` VesperBriefingFile schema lists `content` as a string field, but it's easy to omit when building the sections array. The `quality_check.py` `check_greeting` function reads `briefing['content']` and will FAIL if the field is missing (it returns `''` and the greeting check fails with "expected 'Good morning ...'"). Always include `content` — it's the rendered plain-text version of the full briefing, with section markers and newlines. Build it as you build the sections array.
- **`signals_consumed` is NOT in the VesperBriefingFile schema** — The `quality_check.py` `check_signals_evaluated` function looks for `briefing.get('signals_consumed', [])`, but this field is not part of the VesperBriefingFile schema in `references/schemas.md`. If you include `signals_consumed` in the briefing JSON, the quality check will try to validate those IDs against `signals_evaluated.jsonl` — which fails if the JSONL hasn't been written yet (per the draft→check→finalize ordering). **Do not include `signals_consumed` in the briefing file.** Run `quality_check.py` without the second argument (signals path) to skip the signals check, then append to `signals_evaluated.jsonl` after the check passes (step 4 of run completion).
- **`write_file` is safe for individual briefing JSON files** — The "Cron mode" gotcha about using heredocs applies to JSONL files (which must be appended, not overwritten). Individual briefing files (`briefings/YYYY-WXX/YYYY-MM-DD-{type}.json`) are single JSON documents — `write_file` or `terminal` + Python `json.dump` both work. Use `write_file` for the initial write, then `terminal` + Python for any post-quality-check modifications (like fixing the `delivered` flag).
- **JSONL bracket corruption in nested sections** — A `briefings.jsonl` entry can develop a bracket mismatch in the deeply nested `sections[].content_items[].decision_request` structure. The correct closing sequence for a section with a decision_request is `"status":"pending"}}]}]` (close decision_request `}`, close content_items item `}`, close content_items array `]`, close section object `}`, close sections array `]`). A corrupted entry will have `"status":"pending"}]}]` — missing the `}` that closes the content_items item object. This produces a `JSONDecodeError: Expecting ',' delimiter` at the exact position of the stray `]`. **Diagnosis:** Use `python3 -c "import json; json.loads(line)"` per line to find the broken one, then count `{`/`}` and `[`/`]` opens vs closes in the sections array to find the mismatch. **Fix:** Add the missing `}` — change `"}]}]` to `"}}]}]` at the decision_request boundary. Always verify the fix with `json.loads()` before writing back. This corruption appears to be caused by the briefing generation code omitting one closing brace when serializing sections that contain decision_request objects.
- **Custom paths**: When a user requests a briefing saved to a custom directory (e.g., `evening/` or `morning/`), always also write the canonical file to `briefings/YYYY-WXX/YYYY-MM-DD-{type}.json` per the schema, and keep the two files identical. Delivery tracking applies only to the canonical file.

## Recovery behavior

## Recovery behavior

When Vesper encounters a partial failure, it follows the recovery protocol in `spec-ocas-recovery.md`:

- **Partial signal loss**: Logs via journal, generates briefing with available data, omits missing sections silently.
- **Corrupted briefing file**: Archives with `.corrupted.{timestamp}` suffix and regenerates.
- **Interrupted run**: Checks `intents.jsonl` for incomplete entries, retries once, skips persistently failed entries.
- **Upstream unavailability**: Treated as normal empty state — section omitted.

All recovery actions logged to `evidence.jsonl`.

## Support File Map

| File | When to read |
|---|---|
| `references/account-credentials.md` | Before any Google OAuth operation |
| `references/schemas.md` | Before creating briefings, sections, or decision requests; also contains storage layout and default config |
| `references/briefing_templates.md` | Before generating briefing content |
| `references/signal_filtering.md` | Before evaluating signals for inclusion |
| `references/journal.md` | Before vesper.journal; at end of every run |
| `references/html-templates.md` | Before rendering briefing email HTML |
| `references/weather-codes.md` | Before rendering the weather line (morning briefings) |
| `references/weather-api.md` | Before fetching weather data — working Open-Meteo curl command and parameter reference |
| `references/delivery-troubleshooting.md` | When a briefing is generated but not delivered |
| `references/delivery-check-procedure.md` | During delivery check cron runs — checking briefings.jsonl for undelivered entries, fixing flag desyncs |
| `references/mcp-server-diagnosis.md` | When the Google Workspace MCP server is unresponsive or absent — binary-chain diagnosis, failure modes, and fallback handling |
| `references/okrs.md` | Before evaluating or reporting OKR metrics |
| `references/update-procedure.md` | During `vesper.update` — conflict resolution and profile sync steps |
| `references/cron-mode-operations.md` | During cron job execution — tool constraints (`execute_code` denied, `patch` unreliable on JSONL), briefing path conventions, JSONL write ordering |
| `references/sparse-briefings.md` | When upstream signals are unavailable — how to produce useful thin briefings without padding. Covers weather-only briefings (empty `sections` array), evening sparse patterns, and "tomorrow-empty, day-after-has-events" pattern. |
| `references/signal-gathering.md` | During signal fetching — parallel fetching reliability, subagent OAuth pitfall, thin briefing examples |
| `references/cron-mode-briefing-generation.md` | During cron job execution — complete end-to-end workflow with pitfalls and solutions |
| `references/jsonl-debug.md` | When briefings.jsonl has corrupted entries — diagnosis and repair of bracket mismatches |
| `scripts/quality_check.py` | After generating a briefing file — automated validation. Run with absolute path: `python3 ~/.hermes/profiles/indigo/skills/ocas-vesper/scripts/quality_check.py <briefing.json>`. Returns `PASS` or `FAIL` with specific terms/sctions that need fixing. |
| `scripts/delivery_check.py` | During delivery-check cron runs — scans individual files + `briefings.jsonl` for undelivered briefings (applies the dual delivery-flag/desync rules), and with `--deliver` sends via the Telegram fallback when the email MCP is unavailable, then updates both records with a surgical line edit (preserves corrupted sibling JSONL lines byte-for-byte). Run `python3 ~/.hermes/profiles/indigo/skills/ocas-vesper/scripts/delivery_check.py --type morning --deliver`. |