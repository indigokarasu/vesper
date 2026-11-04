---
name: ocas-vesper
description: 'Daily morning and evening briefing generator. Aggregates signals from across the system into concise briefings. Surfaces outcomes, opportunities, and decisions in natural language without exposing internal processes. NOT for: deep research (use Sift), pattern analysis, message drafting (use Dispatch), or raw data queries (use Styx directly).'
license: MIT
source: https://github.com/indigokarasu/vesper
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
  version: "2.15.0"
  hermes:
    category: productivity
    tags:
    - daily-briefing
    - aggregation
    - natural-language
    - OCAS-core
    config:
    - key: VESPER_SENDER_EMAIL
      description: Sender address for briefing emails
      default: mx.indigo.karasu@gmail.com
    - key: VESPER_OWNER_EMAIL
      description: Recipient address for briefings
      default: jared.zimmerman@gmail.com
    - key: OCAS_OPERATOR_EMAIL
      description: Fallback recipient alias
      default: jared.zimmerman@gmail.com
    - key: AGENT_ROOT
      description: Hermes agent root
      default: ~/.hermes
required_environment_variables:
- name: AGENT_ROOT
  prompt: Agent root directory
  help: Hermes profile root containing commons/data and commons/journals
  required_for: optional
---

## Interactive Menu

When invoked interactively, present a two-level menu using the `clarify` tool. See `references/interactive-menu.md`.

Vesper is the system's daily voice — a concise, conversational morning/evening briefing aggregated from every other skill. Raw signals aren't actionable alone; this skill synthesizes them into natural language — no internal architecture exposed.

## When to Use

- Daily briefing generation (morning, evening, on-demand)
- Aggregate signals from all OCAS skills
- Morning summary of calendar, email, and system status
- End-of-day wrap-up and next-day preview
- List pending decision requests; configure schedule or sections

## When NOT to Use

- Deep research — Sift
- Pattern analysis
- Message drafting — Dispatch
- Action execution — the relevant domain skill
- Calendar management — Sands
- Email sending — Dispatch

## Account isolation

See `references/account-credentials.md` for Google account isolation rules and OAuth credential configuration.

## Responsibility boundary

Vesper owns briefing generation, signal aggregation, and decision presentation. It aggregates signals from Rally, Sands, Dispatch, and Calendar into morning and evening briefings, then writes completed briefings to `briefings/` for Dispatch to deliver.

Vesper does not own: signal generation, portfolio management (Rally), calendar management (Sands), communications delivery (Dispatch), research (Sift/Scout), or action decisions (Praxis). It surfaces outcomes; it does not act.

## Signal filtering rules

Read `references/signal_filtering.md` for full rules.

- Never narrate system maintenance, self-repair, or internal architecture (owner, 2026-09-28: "keep it to yourself"). Covers System, Today, decisions — maintenance-only System section DROPPED, not softened.
- Never route a maintenance item as a pending decision. Decisions are the owner's real choices (spending, committing, hiring); a broken job is yours to fix.
- Include: actionable info, outcomes, plan-affecting changes, multi-signal opportunities, prep-useful info. Exclude: background activity, past events, internal reasoning, speculation. Evening: no past weather, no attended-meeting summaries.

## Formatting rules

- **Delivery volume:** Only morning/evening vesper briefings may be emailed — no other job or skill emails Jared. Proactive findings surface inside the next briefing instead.

Read `references/briefing_templates.md` (structure + examples), `references/html-templates.md` (HTML layout), `references/weather-codes.md` (weather rendering).

Key constraints:
- No markdown (#, **, ---) — plain text/minimal HTML for Gmail; conversational paragraphs, not bullet dumps
- Section headers: ▪ Today, ✉ Messages, ⚑ Logistics, ◈ Markets, ⟡ Decisions, ⚙ System — omit empty sections; normal-state health is silence ("all clear" never appears)
- Opening: "Good morning" / "Good evening" (no punctuation after greeting)
- Markets: morning = yesterday's close; evening = open + close; notable movers only when material
- Decision requests: option, benefit, cost — framed as optional
- Links inline, meaningful anchor text
- No nagging, no internal terminology, speculation, or architecture references; apply Vibes voice rules

## Commands

- `vesper.briefing.morning` — generate morning briefing
- `vesper.briefing.evening` — generate evening briefing
- `vesper.briefing.manual` — on-demand briefing
- `vesper.briefing.deliver` — deliver undelivered briefings by EMAIL only (owner rule, 2026-09-25; no Telegram). Automated: Dispatch's `briefing_deliver.py` via `dispatch:briefing-deliver` cron, both to `jared.zimmerman@gmail.com`. Manual fallback: scan files for non-delivered status, render HTML, send via MCP, update both file and `briefings.jsonl`. Cron fallback without the email MCP: `python3 scripts/delivery_check.py --type <morning|evening|all> --deliver`. See `references/delivery-channel.md` — a docstring is not enforcement.
- `vesper.briefing.check` — inspect the latest briefing file (`scripts/check_briefing.py`)
- `vesper.decisions.pending` — list unacted decision requests
- `vesper.config.set` — update schedule, sections, delivery
- `vesper.status` — last briefing time, pending decisions, schedule
- `vesper.journal` — write journal for the current run (end of every run)
- `vesper.update` — pull latest from GitHub source; preserves journals and data

## Run completion

See `references/run-completion.md` for the full protocol: duplicate-fire guard runs first, signal gathering, briefing file contract, quality check, append-only JSONL persistence, journaling. Read before running a generator cron.

## Inter-skill interfaces

See `references/inter-skill-interfaces.md` for the Custodian, Dispatch, Rally, and intake contracts.

## Storage layout & configuration

Data under `{agent_root}/commons/data/ocas-vesper/`, journals under `{agent_root}/commons/journals/ocas-vesper/`. Default `config.json`: morning 07:00–09:00 PT, evening 17:00–19:00 PT, six sections, 30-day retention, 10k cap. Briefings in ISO week directories as `YYYY-MM-DD-{type}.json`. See `references/schemas.md`.

**Minimal briefing file example (weather-only morning):**
```json
{"briefing_id":"vesper-morning-2026-11-03","type":"morning","date":"2026-11-03","week":"2026-W45","generated_at":"2026-11-03T06:00:00-08:00","content":"Good morning\n\n58°F right now, ☁️ overcast. Warming to 63°F by 10am. High of 74°F mid-afternoon, ☀️ sunny, 71°F at 4pm, dropping to a low of 55°F overnight.","sections":[],"delivery_status":"pending","delivered":false}
```

## OKRs

Five OKRs — signal precision, terminology compliance, decision framing, schedule adherence, data integrity — evaluated over 30-run windows. Targets: 85%+ actionable signals, 100% terminology-free briefings, 100% complete decision framing, 95%+ schedule compliance, 99%+ data integrity. See `references/okrs.md`.

## Optional skill cooperation

- Vibes — voice rules from SOUL.md/AGENTS.md (do not load ocas-vibes via skill_view; rules already embedded). No em dashes, no "the user" (use "you"), no meta-narration ("Now I have…", "Let me check…").
- Custodian — reads InsightProposal files
- Dispatch — reads DispatchSummaryReport; picks up completed briefings for delivery
- Rally — reads portfolio daily reports
- Calendar/Weather — reads external context for briefing content

## Ontology types & journal

Vesper observes entities during aggregation (Entity/Person, Concept/Event, Place) and records `entities_observed`, `relationships_observed`, `preferences_observed`, plus `user_relevance` (`user`, `agent_only`, `unknown`) for Chronicle ingestion. Read `references/journal.md` before `vesper.journal`.

## Initialization

Run `vesper.init` on first invocation:
- [ ] Create data directories (including `briefings/`)
- [ ] Write default `config.json` if absent
- [ ] Create empty JSONL files
- [ ] Create journal directory
- [ ] Register cron jobs `vesper:morning`, `vesper:evening`, `vesper:update`
- [ ] Log initialization as a DecisionRecord in `decisions.jsonl`

## Background tasks

| Job name | Schedule | Command |
|---|---|---|
| `vesper:morning` | `0 6 * * *` daily 6am PT | `vesper.briefing.morning` |
| `vesper:evening` | `0 20 * * *` daily 8pm PT | `vesper.briefing.evening` |
| `vesper:update` | `0 0 * * *` midnight PT | `vesper.update` |

## Disabling briefings

Pause BOTH generation and sending — pausing delivery alone does not work.

- **Sending:** pause `dispatch:briefing-deliver` (`enabled: false`, `state: paused`).
- **Generation:** pause `vesper:morning`, `vesper:evening`, `touchpoint:agenda`, `touchpoint:midday`, `touchpoint:wrap`.

Why: pausing `dispatch:briefing-deliver` stops at its own tick; generators keep writing today-dated briefings and the delivery script has no disabled gate — it sends any today-dated briefing past its earliest send time, including via the email fallback. Pause all five generation jobs first, then confirm the sender is paused.

## Self-update

`vesper.update` pulls the latest package from `source:` in this file's frontmatter. Silent unless version changed or error; retries once on failure. Success output: `I updated Vesper from version {old} to {new}`.

Procedure: `references/update-procedure.md` — stash changes, pull, stash pop, resolve conflicts; then sync `~/.hermes/profiles/indigo/skills/ocas-vesper/` (sessions load from the profile copy).

## Gotchas

Read `references/gotchas.md` for the full operational knowledge.

## Error Handling

| Failure | Symptom | Handling |
|---|---|---|
| Google Workspace MCP down | `Email ✗ not configured`, no `workspace-mcp` process | Set `delivery_status: {status:"failed", reason:"MCP server not running in cron session"}` on the individual file and `briefings.jsonl`; no retry loop — preserve content for the next run. See `references/mcp-server-diagnosis.md`. |
| OAuth token expired | `invalid_grant` / `token expired` | Update `failed_at` + reason; report the blocker (browser reauth — impossible in cron mode). |
| Partial JSONL write | `JSONDecodeError` on a ledger line | Repair surgically by matching `run_id` — never whole-file rewrite. See `references/jsonl-debug.md`. |
| All upstream signals absent | Thin or weather-only briefing | Valid: write `sections: []`, mark `delivery_status: "silent"` if nothing actionable. See `references/sparse-briefings.md`. |
| Cron double-fire | Duplicate briefing email | `scripts/dup_guard.py` exits 3 → skip regeneration and re-delivery. |
| Flag desync | `delivered`/`delivery_status` disagree | Trust the timestamp; fix with `scripts/delivery_check.py`. See `references/delivery-check-procedure.md`. |

## Recovery behavior

- **Partial signal loss:** journal, generate with available data, omit missing sections silently.
- **Corrupted briefing file:** archive with `.corrupted.{timestamp}` suffix, regenerate.
- **Interrupted run:** check `intents.jsonl` for incomplete entries, retry once, skip persistently failed entries.
- **Upstream unavailability:** normal empty state — omit section.

Recovery actions logged to `evidence.jsonl`.

## Support File Map

| File | When to read |
|---|---|
| `references/gotchas.md` | Before any operational work |
| `references/interactive-menu.md` | When invoked interactively via `/` |
| `references/account-credentials.md` | Before any Google OAuth operation |
| `references/schemas.md` | Before creating briefings/sections/decisions; storage layout + default config |
| `references/briefing_templates.md` | Before generating briefing content |
| `references/signal_filtering.md` | Before evaluating signals |
| `references/journal.md` | Before `vesper.journal`; end of every run |
| `references/html-templates.md` | Before rendering briefing email HTML |
| `references/weather-codes.md` | Before rendering the weather line |
| `references/weather-api.md` | Before fetching weather data (Open-Meteo curl command) |
| `references/delivery-channel.md` | **Before touching delivery** — email only, never Telegram |
| `references/delivery-check-procedure.md` | During delivery-check cron runs — undelivered entries, flag desyncs |
| `references/mcp-server-diagnosis.md` | When the Google Workspace MCP server is down |
| `references/okrs.md` | Before evaluating OKR metrics |
| `references/update-procedure.md` | During `vesper.update` |
| `references/cron-mode-operations.md` | During cron execution — tool constraints, paths |
| `references/sparse-briefings.md` | When upstream signals are unavailable — thin briefings without padding |
| `references/signal-gathering.md` | During signal fetching — parallel fetching, subagent OAuth pitfall |
| `references/cron-mode-briefing-generation.md` | During cron execution — end-to-end workflow |
| `references/jsonl-debug.md` | When `briefings.jsonl` has corrupted entries |
| `references/run-completion.md` | **Before running a generator cron** |
| `references/inter-skill-interfaces.md` | **Before reading or writing cross-skill data** |
| `scripts/check_briefing.py` | Manual inspection of the latest briefing |
| `scripts/dup_guard.py` | **First in every generator run** — exit 3 = already delivered today |
| `scripts/quality_check.py` | After generating a briefing file — PASS/FAIL with terms to fix |
| `scripts/delivery_check.py` | Delivery-check cron runs — scans + sends by email, updates both records |

## Tests

`tests/test_smoke.py` — `is_undelivered()` (boolean/string/dict `delivery_status`) and `has_content()`.

Run: `python3 -m unittest discover -s tests` (CI: `.github/workflows/ci.yml` on every push to `main`).
