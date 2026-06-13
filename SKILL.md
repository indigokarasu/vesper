---
name: ocas-vesper
description: 'Daily briefing generator. Aggregates signals from across the system into concise morning and evening briefings. Surfaces outcomes, opportunities, and decisions in natural language without exposing internal processes. Do not use for deep research (use Sift), pattern analysis (use Corvus), or message drafting (use Dispatch).'
license: MIT
source: https://github.com/indigokarasu/vesper
includes:
- references/**
- scripts/**
metadata:
  author: Indigo Karasu (indigokarasu)
  version: 2.13.0
tags:
- briefing
- daily
- signals
- aggregation
- OCAS-core
triggers:
- daily briefing
- morning briefing
- evening briefing
- signal aggregation
- generate briefing
---
## Interactive Menu

When invoked interactively, present a two-level menu using the `clarify` tool. See `references/interactive-menu.md` for the full menu structure, response parsing, and platform adaptation.




Vesper is the system's daily voice — it aggregates signals from every other skill and presents what matters as a concise, conversational morning or evening briefing, surfacing concrete outcomes, upcoming decisions, and actionable opportunities without exposing any internal architecture or analysis processes.

## When to Use

- Daily briefing generation (morning, evening, on-demand)
- Signal aggregation from all OCAS skills
- Morning summary of calendar, email, and system status
- End-of-day wrap-up and next-day preview
- Checking pending decision requests
- Configuring briefing schedule or sections

## When NOT to Use

- Deep research — use Sift
- Pattern analysis — use Corvus
- Message drafting — use Dispatch
- Action execution — use relevant domain skill
- Real-time monitoring
- Calendar management (use Sands)
- Email sending (use Dispatch)

## What this skill does not do

- Signal generation (Corvus owns this)
- Portfolio management (Rally)
- Calendar management (Sands)
- Communications delivery (Dispatch)
- Research (Sift/Scout)
- Action decisions (Praxis)

## Account isolation

See `references/account-credentials.md` for Google account isolation rules and OAuth credential configuration.

## Responsibility boundary

Vesper owns briefing generation, signal aggregation, and decision presentation. It aggregates signals from Corvus, Rally, Sands, Dispatch, and Calendar into morning and evening briefings, then writes completed briefings to its `briefings/` directory for Dispatch to pick up and deliver.

Vesper does **not** own: signal generation (Corvus), portfolio management (Rally), calendar management (Sands), communications delivery (Dispatch), research (Sift/Scout), or action decisions (Praxis). It surfaces outcomes; it does not act.

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
- Opening: "Good morning owner" / "Good evening owner" (no punctuation after greeting)
- Markets: morning shows yesterday's close; evening shows open and close. Notable movers only when material.
- Decision requests: option, benefit, cost — framed as optional
- Links are inline with meaningful anchor text; see URI formats in reference files
- When Vibes (ocas-vibes) is present, apply its voice and anti-AI rules to all briefing text
- No nagging, no internal terminology, no speculative observations, no architecture references

## Commands

- `vesper.briefing.morning` — generate morning briefing
- `vesper.briefing.evening` — generate evening briefing
- `vesper.briefing.manual` — on-demand briefing
- `vesper.briefing.deliver` — deliver undelivered briefings via email using `mcp_google_workspace_send_gmail_message` (NOT `briefing_deliver.py` which is broken). Scan individual briefing files for non-delivered status, convert content to HTML, send via MCP, update both the individual file and `briefings.jsonl` on success.
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

0. **Load Vibes** — Before writing briefing text, load `ocas-vibes` via `skill_view(name='ocas-vibes')` to get voice and anti-AI rules. Apply these rules to all briefing prose.
1. Read InsightProposal files from Corvus and Custodian `proposals/` directories. Apply signal filtering. Track consumed `proposal_id` values in `signals_evaluated.jsonl` to avoid reprocessing. Read Dispatch summary and Rally daily report if present.
2. Write briefing file to `{agent_root}/commons/data/ocas-vesper/briefings/YYYY-WXX/YYYY-MM-DD-{type}.json` using `VesperBriefingFile` schema. Create week directory if absent.
3. **Briefing quality check**: Re-read the generated briefing file and verify: (a) no internal system terminology leaked through (no skill IDs, DB names, or technical jargon), (b) all included sections have actual content — no empty sections, (c) the greeting matches the time-of-day format, (d) `signals_evaluated.jsonl` was updated with all consumed proposal IDs, and (e) every decision item traces to a real upstream signal — no fabricated or template-copied decisions. If any check fails, regenerate the briefing before marking the run complete.
4. **Only after the briefing passes quality check**, persist the completed briefing record to `briefings.jsonl` and evaluated signals to `signals_evaluated.jsonl`. Log material decisions to `decisions.jsonl`. (Do not append these files before the quality check succeeds — the JSONL is the delivery contract and must match the final briefing exactly.)
5. Write journal via `vesper.journal`.

## Inter-skill interfaces

**Corvus → Vesper:** Corvus writes InsightProposal files to `{agent_root}/commons/data/ocas-coralus/proposals/{proposal_id}.json`. Vesper reads and filters them. See `spec-ocas-interfaces.md` for the InsightProposal schema.

**Custodian → Vesper:** Custodian writes InsightProposal files (`anomaly_alert` type) to `{agent_root}/commons/data/ocas-custodian/proposals/{proposal_id}.json`. Vesper reads them during briefing generation.

**Dispatch → Vesper:** Dispatch writes `DispatchSummaryReport` to `{agent_root}/commons/data/ocas-dispatch/reports/YYYY-MM-DD-{period}.json`. Vesper uses this for the Messages section.

**Rally → Vesper:** Rally writes daily portfolio reports to `{agent_root}/commons/data/ocas-rally/reports/YYYY-MM-DD-daily.json`. Vesper uses this for the Markets section.

**Vesper → Dispatch:** Vesper writes completed briefings to its `briefings/` directory. Dispatch picks them up for delivery. See `references/schemas.md` VesperBriefingFile.

## Storage layout & configuration

Data lives under `{agent_root}/commons/data/ocas-vesper/` with journals under `{agent_root}/commons/journals/ocas-vesper/`. The default `config.json` sets morning window 07:00–09:00 PT, evening window 17:00–19:00 PT, all six sections enabled, 30-day retention, and 10k record cap. Briefings are stored in ISO week directories as `YYYY-MM-DD-{type}.json`. See `references/schemas.md` for the full directory tree and default config.

## OKRs

Vesper tracks five OKRs — signal precision, terminology compliance, decision framing, schedule adherence, and data integrity — all evaluated over 30-run windows. Targets: 85%+ actionable signals, 100% terminology-free briefings, 100% complete decision framing, 95%+ schedule compliance, 99%+ data integrity. See `references/okrs.md` for the full OKR specification.

## Optional skill cooperation

- **Vibes** — applies voice identity and anti-AI rules from ocas-vibes. **Load ocas-vibes via `skill_view(name='ocas-vibes')` before writing briefing text** and apply its Pre-Send Checklist to the rendered briefing. Vibes rules apply to all user-facing prose.
- **Corvus** — reads InsightProposal files (cooperative read)
- **Custodian** — reads InsightProposal files (cooperative read)
- **Dispatch** — reads DispatchSummaryReport; Dispatch picks up completed briefings from Vesper for delivery
- **Rally** — reads portfolio daily reports (cooperative read)
- **Calendar/Weather** — reads external context for briefing content
- **Elephas** — journal entity observations consumed during Chronicle ingestion

## Ontology types & journal

Vesper observes entities during briefing aggregation (Entity/Person, Concept/Event, Place). Entity observations are recorded in journal outputs for downstream Chronicle ingestion. Read `references/journal.md` before `vesper.journal`.

When entities are encountered, include in `decision.payload`:
- `entities_observed` — type, name, context
- `relationships_observed` — connections between entities
- `preferences_observed` — user preferences inferred from briefing interactions

Each entity observation includes a `user_relevance` field: `user`, `agent_only`, or `unknown`.

## Initialization

On first invocation, run `vesper.init`:
1. Create data directories (including `briefings/`)
2. Write default `config.json` if absent
3. Create empty JSONL files
4. Create journal directory
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

- **Account isolation is critical** — See `references/account-credentials.md`.
- **Upstream skill unavailability is silent** — Missing data means the affected section is omitted entirely. No error raised.
- **Signal filtering is strict** — Routine, speculative, and already-experienced signals are excluded.
- **Normal state is silence** — Never confirms "all systems normal." Empty sections are omitted with no placeholder.
- **Briefing files use ISO week directories** — Stored under `briefings/YYYY-WXX/`. Create the directory if absent.
- **Cron mode blocks `execute_code`** — Vesper runs as an isolated cron job. `execute_code` is denied in this mode. Use `terminal` with heredoc (`cat >> file << 'EOF'`) for JSONL appends and file writes. Plan file operations accordingly.
- **`briefing_deliver.py` is BROKEN — use MCP tools directly** — The `scripts/briefing_deliver.py` script uses `googleapiclient` directly and will fail with import/auth errors in cron mode. When delivering briefings, always use `mcp_google_workspace_send_gmail_message` via MCP. Build HTML manually from the `content` field — no template file needed. See the delivery check procedure in cron mode for the correct approach.
- **Never fabricate decisions** — Every decision item in the briefing must trace to a real upstream signal (a Corvus proposal, Custodian alert, pending renewal with real data). Template examples in `briefing_templates.md` are illustrations only, not real pending items. If no genuine decision signal exists, omit the Decisions section entirely. A fabricated decision (#4 quality check violation) is worse than silence.
- **Hallucination window — April-May 2026** — During this period, Vesper briefings were generated with fabricated personal data (false locations, investment positions, family details, insurance policies). These briefings ARE in the system and may be read by Corvus, Dispatch, and other skills. When sourcing data for briefings corroborate all "facts" about the user's personal life against primary sources (actual Gmail, actual Calendar, actual session transcripts) — never trust a Vesper briefing from this window as a source of personal fact. If you find briefing content that contradicts known reality, discard the briefing data and flag the briefing as corrupted.
- **JSONL write ordering** — The briefing content (`briefings/YYYY-WXX/YYYY-MM-DD-{type}.json`) is the source of truth. Only after the briefing file passes the quality check (step 5 of Run completion) should `briefings.jsonl` and `signals_evaluated.jsonl` be written/appended. Never append to `briefings.jsonl` during the draft phase. Draft → quality check → finalize → append JSONLs. This avoids append-then-retract cycles that complicate delivery tracking.
- **briefings.jsonl IS real JSONL** — `briefings.jsonl` is one JSON object per line, standard JSONL format. The `read_file` tool wraps all output in a `content` field with `N|` line prefixes — this is a tool artifact, NOT the file's actual structure. To verify raw file format, use `head -c 500 file` or `terminal cat file | head -3`. To check for undelivered briefings: `grep -c '"delivered": false' briefings.jsonl` (standard grep works on raw JSONL). To count lines: `wc -l briefings.jsonl`.
- **Dual delivery flags can desync** — `briefings.jsonl` has two parallel delivery tracking fields: `delivered` (boolean) and `delivery_status` (object with `status` + `delivered_at`). These can get out of sync when delivery updates one but not the other. When checking for undelivered briefings, check BOTH fields: a briefing is considered delivered if either `delivered=true` OR `delivery_status.status="delivered"` (with a non-null `delivered_at`). If flags are desync'd, fix them by setting `delivered=true` on any entry where `delivery_status.status="delivered"` — the delivery timestamp is the authoritative record.
- **Dual LOCATIONS can desync** — Briefings live in two places: the master index (`briefings.jsonl`) AND individual files (`briefings/YYYY-WXX/YYYY-MM-DD-{type}.json`). Each has its own `delivered` flag. The JSONL index may say `delivered: true` while the individual file says `delivered: false`, or vice versa. When checking for undelivered briefings, you MUST scan both locations. Use `grep -rl '"delivered": false' <hermes-root>/commons/data/ocas-vesper/briefings/*/` to find undelivered individual files. After delivering, update BOTH locations.
- **`delivery_status` has THREE formats** — The field can be: (1) a plain string: `"delivered"`, `"pending"`, or `"silent"`; (2) an object with `{status: "delivered", delivered_at: "..."}`; (3) an object with `{status: "failed", failed_at: "...", reason: "..."}`. When scanning for undelivered briefings, check ALL three forms. A briefing is undelivered if: `delivery_status` is `"pending"`, OR `delivery_status.status` is `"failed"` or `"pending"`, OR `delivered` is `false` or `null`/`None`. **Skip `"silent"` status** — these are intentionally suppressed briefings with no content, not failed deliveries.
- **OAuth failures are persistent blockers** — When `send_gmail_message` returns an auth error, the briefing's `delivery_status` is set to `{status: "failed", reason: "Google OAuth..."}`. On retry, if OAuth is still not reauthorized, do NOT keep retrying in a loop — update the `failed_at` timestamp and reason, then report the blocker to the user. The OAuth outage briefing itself (the 2026-05-31 evening brief) is a self-referential case: it reports the OAuth failure that prevents its own delivery.
- **Weather API: use Open-Meteo directly, not RapidAPI** — The RapidAPI `weather` endpoint's `current-weather` action is unreliable (returns "tool not found"). Use `curl` directly to `https://api.open-meteo.com/v1/forecast` with parameters `temperature_2m` and `weather_code` (NOT `temperature_2m,weather_code` as a comma-separated single param — they are separate query params). Example: `curl -s "https://api.open-meteo.com/v1/forecast?latitude=37.7749&longitude=-122.4194&current=temperature_2m,weather_code&hourly=temperature_2m,weather_code&daily=temperature_2m_max,temperature_2m_min,weather_code&temperature_unit=fahrenheit&timezone=America%2FLos_Angeles&forecast_days=2"`. See `references/weather-codes.md` for WMO code mapping.
- **Python booleans in heredocs** — When writing Python via shell heredoc (`cat << 'EOF'`), use `True`/`False` (Python capitalization), NOT `true`/`false` (JSON/JS). Using lowercase causes `NameError: name 'false' is not defined`.
- **Direct Telegram delivery** — When the user requests immediate delivery (not via Dispatch), use `hermes send --to telegram:8666597030 --quiet "message"`. This bypasses the Dispatch pipeline and delivers directly. Mark the briefing as `delivered: true` with `delivered_at` timestamp immediately after successful send.
- **Finch journals are NOT deliverables** — The JSON files in `commons/journals/ocas-finch/YYYY-MM-DD/` (daily-HHMM.json, weekly-HHMM.json, scan-HHMM.json) are internal action journals, not user-facing reports. Finch cron jobs are self-delivering via the cron system (`deliver: "origin"` or `deliver: "local"`). When running a delivery check, NEVER send finch journal content via `hermes send`. Only check `briefings.jsonl` for undelivered briefings. See `references/delivery-check-procedure.md` for the full procedure.
- **Corvus proposals.jsonl is a separate signal source** — In addition to individual `{proposal_id}.json` files in the Corvus proposals directory, Corvus also writes an aggregated `proposals.jsonl` file. This file can contain proposals that don't have individual `.json` files. During signal gathering, you MUST check both: (1) all individual `.json` files in the proposals directory, AND (2) the `proposals.jsonl` file. Parse each line of `proposals.jsonl` as a separate proposal. Cross-reference proposal IDs against `signals_evaluated.jsonl` to avoid reprocessing.
- **read_file output is tool wrapping, not file contents** — The `read_file` tool wraps all output in `{"content": "N|line1\nN|line2"}` — this is a tool presentation layer, NOT the file's actual on-disk format. When verifying file structure (JSONL delimiters, CSV headers, encoding), use `terminal head -c 500 file` or `terminal head -3 file` to see raw bytes. The pipe-delimited `N|` prefixes you see in tool output do NOT exist in the actual file.
- **Skill files live in two locations** — The git repo at `~/.hermes/skills/ocas-vesper/` is the update source. Sessions load from `~/.hermes/profiles/indigo/skills/ocas-vesper/`. After any `vesper.update`, the profile copy MUST be synced or the next session will run stale code. Always sync both `SKILL.md` and `references/` after pulling. See `references/update-procedure.md`.
- **Editing briefings.jsonl with `patch` is dangerous** — `briefings.jsonl` uses `N|` line number prefixes on each line. The `patch` tool operates on raw file content. If you include the `N|` prefix in both old_string and new_string, you can accidentally create duplicate prefixes (e.g., `27|27|`). SAFE alternatives: (1) Use `terminal` + `sed -i 'Ns/^N|N|/|/'` for surgical single-line prefix fixes. (2) Use `terminal` + Python (`json.load` per line, modify, `json.dump` per line) for structured edits. (3) Use `write_file` to rewrite the entire file from a parsed representation. NEVER use `patch` with the `N|` prefix included in both old and new strings — the prefix duplicates and corrupts the line, making it unparseable.
- **Failed briefings may have no `content` field** — When a briefing fails during generation (e.g., OAuth expired before data could gather), the JSONL entry may contain only metadata (`briefing_id`, `type`, `date`, `sections`, `delivery_status`) with NO `content` field. During delivery checks, skip entries that lack a `content` string — there is nothing to deliver. Mark them as `delivery_status: "skipped"` with a reason of "No content — generation failed" to prevent re-checking. If `content` exists but is empty string (`""`), also skip — the briefing was intentionally suppressed.

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
| `references/okrs.md` | Before evaluating or reporting OKR metrics |
| `references/update-procedure.md` | During `vesper.update` — conflict resolution and profile sync steps |
