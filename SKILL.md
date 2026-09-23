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
  version: "2.14.0"
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
- Opening: "Good morning" / "Good evening" (no punctuation after greeting)
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
- [ ] **Briefing quality check**: Re-read the generated briefing file and verify: (a) no internal system terminology leaked through (no skill IDs, database references, or technical jargon — use **whole-word matching**, not substring matching, to avoid false positives like "DB" matching inside "Handbuilding"), (b) all included sections have actual content — no empty sections, (c) the greeting matches the time-of-day format, (d) `signals_evaluated.jsonl` was updated with all consumed proposal IDs, and (e) every decision item traces to a real upstream signal — no fabricated or template-copied decisions. **Pitfall:** quality_check.py's `check_decisions_trace` function checks that decision summaries reference the upstream source skill name (e.g., "Dispatch", "Rally", "Custodian") as a whole word in the `summary` field. If the summary only describes the event without naming the source skill, the trace check fails. Always include the source skill name (e.g., "Dispatch email check surfaced...", "Rally daily report shows...") in decision summaries. If any check fails, regenerate the briefing before marking the run complete. **Tip:** Run `python3 scripts/quality_check.py <briefing-file.json> [signals-evaluated.jsonl]` for automated validation — it implements all five sub-checks with whole-word regex matching.
- [ ] **Only after the briefing passes quality check**, persist the completed briefing record to `briefings.jsonl` and evaluated signals to `signals_evaluated.jsonl`. Log material decisions to `decisions.jsonl`. (Do not append these files before the quality check succeeds — the JSONL is the delivery contract and must match the final briefing exactly.)
- [ ] Write journal via `vesper.journal`.

## Inter-skill interfaces

**Custodian → Vesper:** Custodian writes InsightProposal files (`anomaly_alert` type) to `{agent_root}/commons/data/ocas-custodian/proposals/{proposal_id}.json`. Vesper reads them during briefing generation.

**Dispatch → Vesper:** Dispatch writes `DispatchSummaryReport` to `{agent_root}/commons/data/ocas-dispatch/reports/YYYY-MM-DD-{period}.json`. Vesper uses this for the Messages section.

**Rally → Vesper:** Rally writes daily portfolio reports to `{agent_root}/commons/data/ocas-rally/reports/YYYY-MM-DD-daily.json`. Vesper uses this for the Markets section.

**Schedule/venue intake polling (per [[`spec-ocas-suite-cross-skill-updates.md` ⚠️ Pending spec] ⚠️ Pending spec — not yet authored]):** Vesper polls the following intake directories during briefing generation and merges their briefs into the schedule / agenda sections:
- **Sands → Vesper intake** — `{agent_root}/commons/data/ocas-vesper/intake/` (daily schedule briefs)
- **Voyage → Vesper intake** — `{agent_root}/commons/data/ocas-vesper/intake/` (travel schedule briefs)
- **Spot → Vesper intake** — `{agent_root}/commons/data/ocas-vesper/intake/` (appointment-confirmation briefs)
- **Taste → Vesper** — recommendation highlights (read from `{agent_root}/commons/data/ocas-taste/recommendations/` or `intake/`), surfaced as a preference-aware Recommendations section.

Consumed briefs are cleaned from the intake dir after merge (Vesper owns intake cleanup). If an intake source wrote no brief, omit that section gracefully — never fail the briefing.

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
- [ ] Register cron jobs `vesper:morning`, `vesper:evening`, `vesper:update` if not already present
- [ ] Log initialization as a DecisionRecord in `decisions.jsonl`

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

Read `references/gotchas.md` for the full operational knowledge — account isolation, cron-mode constraints, delivery desyncs, MCP failures, weather API, tool quirks, and quality check pitfalls.

Key rules live here; the reference file holds the details.

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

## Support Files

- `scripts/update.sh` — Wrapper to update ocas-vesper

## Tests

`tests/test_smoke.py` covers:
- `is_undelivered()` with boolean, string, and dict `delivery_status` variants
- `has_content()` presence and emptiness checks

Run: `python3 -m unittest discover -s tests`

CI via GitHub Actions (`.github/workflows/ci.yml`) runs the suite on every push to `main`.
