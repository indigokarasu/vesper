---
name: ocas-vesper
description: 'Vesper: daily briefing generator. Aggregates signals from across the
  system into concise morning and evening briefings. Surfaces outcomes, opportunities,
  and decisions in natural language without exposing internal processes. Trigger phrases:
  ''morning briefing'', ''evening briefing'', ''what''s happening'', ''daily brief'',
  ''pending decisions'', ''catch me up'', ''update vesper''. Do not use for deep research
  (use Sift), pattern analysis (use Corvus), or message drafting (use Dispatch).

'
license: MIT
metadata:
  author: Indigo Karasu
  version: 2.10.0
---

# Vesper

Vesper is the system's daily voice — it aggregates signals from every other skill and presents what matters as a concise, conversational morning or evening briefing, surfacing concrete outcomes, upcoming decisions, and actionable opportunities without exposing any internal architecture or analysis processes. Its signal filtering is strict: routine background activity, speculative observations, and already-experienced events are excluded, so every briefing earns attention rather than demanding it.

## When to use

- Generate morning or evening briefing
- Request an on-demand briefing
- Check pending decision requests
- Configure briefing schedule or sections

## When not to use

- Deep research — use Sift
- Pattern analysis — use Corvus
- Message drafting — use Dispatch
- Action execution — use relevant domain skill

## Account Isolation (CRITICAL)

See `references/account-credentials.md` for Google account isolation rules and OAuth credential configuration.

## Ownership & Responsibility

Vesper owns briefing generation, signal aggregation, and decision presentation. It aggregates signals from Corvus, Rally, Sands, Dispatch, and Calendar into morning and evening briefings, then writes completed briefings to its `briefings/` directory for Dispatch to pick up and deliver.

Vesper does **not** own: signal generation (Corvus), portfolio management (Rally), calendar management (Sands), communications delivery (Dispatch), research (Sift/Scout), or action decisions (Praxis). It surfaces outcomes; it does not act.

## Signal filtering rules

Read `references/signal_filtering.md` for full rules.

Summary: Include actionable information, meaningful outcomes, plan-affecting changes, multi-signal opportunities, and preparation-useful information. Exclude routine background activity, already-experienced events, internal system reasoning, and speculative observations. Evening-specific: no past weather, no summaries of attended meetings.

## Formatting rules

Read `references/briefing_templates.md` for structure and examples, `references/html-templates.md` for HTML layout, and `references/weather-codes.md` for weather rendering.

Key constraints (not covered by reference files):

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
- `vesper.briefing.deliver` — deliver undelivered briefings via email (`scripts/briefing_deliver.py`)
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

1. Read InsightProposal files from Corvus and Custodian `proposals/` directories. Apply signal filtering. Track consumed `proposal_id` values in `signals_evaluated.jsonl` to avoid reprocessing. Read Dispatch summary and Rally daily report if present.
2. Write briefing file to `{agent_root}/commons/data/ocas-vesper/briefings/YYYY-WXX/YYYY-MM-DD-{type}.json` using `VesperBriefingFile` schema. Create week directory if absent.
3. Persist briefing record and evaluated signals to local JSONL files. Log material decisions to `decisions.jsonl`.
4. Write journal via `vesper.journal`.
5. **Briefing quality check**: Re-read the generated briefing file and verify: (a) no internal system terminology leaked through (no skill IDs, DB names, or technical jargon), (b) all included sections have actual content — no empty sections, (c) the greeting matches the time-of-day format, and (d) `signals_evaluated.jsonl` was updated with all consumed proposal IDs. If any check fails, regenerate the briefing before marking the run complete.

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

- **Vibes** — applies voice identity and anti-AI rules from ocas-vibes if present
- **Corvus** — reads InsightProposal files (cooperative read)
- **Custodian** — reads InsightProposal files (cooperative read)
- **Dispatch** — reads DispatchSummaryReport; Dispatch picks up completed briefings from Vesper for delivery
- **Rally** — reads portfolio daily reports (cooperative read)
- **Calendar/Weather** — reads external context for briefing content
- **Elephas** — journal entity observations consumed during Chronicle ingestion

## Ontology types & Journal

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

## Visibility

public

## Gotchas

- **Account isolation is critical** — See `references/account-credentials.md`.
- **Upstream skill unavailability is silent** — Missing data means the affected section is omitted entirely. No error raised.
- **Signal filtering is strict** — Routine, speculative, and already-experienced signals are excluded.
- **Normal state is silence** — Never confirms "all systems normal." Empty sections are omitted with no placeholder.
- **Briefing files use ISO week directories** — Stored under `briefings/YYYY-WXX/`. Create the directory if absent.

## Recovery Behavior

When Vesper encounters a partial failure, it follows the recovery protocol in `spec-ocas-recovery.md`:

- **Partial signal loss**: Logs via journal, generates briefing with available data, omits missing sections silently.
- **Corrupted briefing file**: Archives with `.corrupted.{timestamp}` suffix and regenerates.
- **Interrupted run**: Checks `intents.jsonl` for incomplete entries, retries once, skips persistently failed entries.
- **Upstream unavailability**: Treated as normal empty state — section omitted.

All recovery actions logged to `evidence.jsonl`.

## Support file map

| File | When to read |
|---|---|
| `references/account-credentials.md` | Before any Google OAuth operation |
| `references/schemas.md` | Before creating briefings, sections, or decision requests; also contains storage layout and default config |
| `references/briefing_templates.md` | Before generating briefing content |
| `references/signal_filtering.md` | Before evaluating signals for inclusion |
| `references/journal.md` | Before vesper.journal; at end of every run |
| `references/html-templates.md` | Before rendering briefing email HTML |
| `references/weather-codes.md` | Before rendering the weather line (morning briefings) |
| `references/delivery-troubleshooting.md` | When a briefing is generated but not delivered |
| `references/okrs.md` | Before evaluating or reporting OKR metrics |
