---
name: ocas-vesper
source: https://github.com/indigokarasu/vesper
install: openclaw skill install https://github.com/indigokarasu/vesper
description: Use when generating morning or evening briefings, requesting an on-demand system brief, checking pending decisions, or configuring the briefing schedule. Aggregates signals from across the system into concise natural-language summaries. Trigger phrases: 'morning briefing', 'evening briefing', 'what's happening', 'daily brief', 'pending decisions', 'catch me up', 'update vesper'. Do not use for deep research (use Sift), pattern analysis (use Corvus), or message drafting (use Dispatch).
metadata: {"openclaw":{"emoji":"🌅"}}
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


## Responsibility boundary

Vesper owns briefing generation, signal aggregation, and decision presentation.

Vesper does not own: pattern analysis (Corvus), web research (Sift), communications delivery (Dispatch), action decisions (Praxis).

Vesper receives InsightProposal files from Corvus. Vesper may request Dispatch to deliver briefings.


## Commands

- `vesper.briefing.morning` — generate morning briefing
- `vesper.briefing.evening` — generate evening briefing
- `vesper.briefing.manual` — on-demand briefing
- `vesper.decisions.pending` — list unacted decision requests
- `vesper.config.set` — update schedule, sections, delivery
- `vesper.status` — last briefing time, pending decisions, schedule
- `vesper.journal` — write journal for the current run; called at end of every run
- `vesper.update` — pull latest from GitHub source; preserves journals and data


## Invocation modes

- **Automatic morning** — during configured morning window
- **Automatic evening** — during configured evening window
- **Manual** — on user request


## Signal filtering rules

Include: actionable information, meaningful outcomes, plan-affecting changes, multi-signal opportunities, preparation-useful information.

Exclude: routine background activity, already-experienced events, internal system reasoning, speculative observations.

Evening-specific: no past weather, no summaries of attended meetings.

Read `references/signal_filtering.md` for full rules.


## Formatting rules

- Conversational paragraphs, not bullet dumps
- Section headers use emoji: 📅 Today, ✉️ Messages, 🧭 Logistics, 📈 Markets, 🔐 Decisions, 🛠 System
- Links use `[[artifact name]]` format
- Weather in opening paragraph, no section header
- Decision requests: option, benefit, cost — framed as optional
- Opportunities surfaced without exposing underlying analysis

Read `references/briefing_templates.md` for structure and examples.


## Run completion

After every briefing generation:

1. Check `~/openclaw/data/ocas-vesper/intake/` for InsightProposal files from Corvus; apply signal filtering; move processed files to `intake/processed/`
2. Persist briefing record and evaluated signals to local JSONL files
3. Log material decisions to `decisions.jsonl`
4. Write journal via `vesper.journal`

## Behavior constraints

- No nagging — ignored decisions are treated as intentional
- No internal system terminology
- No references to architecture or analysis processes
- No speculative observations
- Only concrete outcomes and actionable opportunities


## Inter-skill interfaces

Vesper receives InsightProposal files from Corvus at: `~/openclaw/data/ocas-vesper/intake/{proposal_id}.json`

Vesper checks its intake during briefing generation. Applies signal filtering rules before including. After processing each file, move to `intake/processed/`.

See `spec-ocas-interfaces.md` for the InsightProposal schema and handoff contract.


## Storage layout

```
~/openclaw/data/ocas-vesper/
  config.json
  briefings.jsonl
  signals_evaluated.jsonl
  decisions_presented.jsonl
  decisions.jsonl
  intake/
    {proposal_id}.json
    processed/

~/openclaw/journals/ocas-vesper/
  YYYY-MM-DD/
    {run_id}.json
```


Default config.json:
```json
{
  "skill_id": "ocas-vesper",
  "skill_version": "2.3.0",
  "config_version": "1",
  "created_at": "",
  "updated_at": "",
  "schedule": {
    "morning_window": "07:00-09:00",
    "evening_window": "17:00-19:00",
    "timezone": "America/Los_Angeles"
  },
  "sections": {
    "today": true,
    "messages": true,
    "logistics": true,
    "markets": true,
    "decisions": true,
    "system": true
  },
  "retention": {
    "days": 30,
    "max_records": 10000
  }
}
```


## OKRs

Universal OKRs from spec-ocas-journal.md apply to all runs.

```yaml
skill_okrs:
  - name: signal_precision
    metric: fraction of included signals rated actionable by user
    direction: maximize
    target: 0.85
    evaluation_window: 30_runs
  - name: terminology_compliance
    metric: fraction of briefings free of internal system terminology
    direction: maximize
    target: 1.0
    evaluation_window: 30_runs
  - name: decision_framing
    metric: fraction of decision requests including option, benefit, and cost
    direction: maximize
    target: 1.0
    evaluation_window: 30_runs
```


## Optional skill cooperation

- Corvus — receives InsightProposal files via intake directory
- Dispatch — may request Dispatch to deliver briefings
- Rally — reads portfolio outcome signals
- Calendar/Weather — reads external context for briefing content


## Journal outputs

Action Journal — every briefing generation run.


## Initialization

On first invocation of any Vesper command, run `vesper.init`:

1. Create `~/openclaw/data/ocas-vesper/` and subdirectories (`intake/`, `intake/processed/`)
2. Write default `config.json` with ConfigBase fields if absent
3. Create empty JSONL files: `briefings.jsonl`, `signals_evaluated.jsonl`, `decisions_presented.jsonl`, `decisions.jsonl`
4. Create `~/openclaw/journals/ocas-vesper/`
5. Register cron jobs `vesper:morning`, `vesper:evening`, and `vesper:update` if not already present (check `openclaw cron list` first)
6. Log initialization as a DecisionRecord in `decisions.jsonl`


## Background tasks

| Job name | Mechanism | Schedule | Command |
|---|---|---|---|
| `vesper:morning` | cron | `0 7 * * *` (daily 7am) | `vesper.briefing.morning` |
| `vesper:evening` | cron | `0 18 * * *` (daily 6pm) | `vesper.briefing.evening` |
| `vesper:update` | cron | `0 0 * * *` (midnight daily) | `vesper.update` |

Cron options: `sessionTarget: isolated`, `lightContext: true`, `wakeMode: next-heartbeat`.

Registration during `vesper.init`:
```
openclaw cron list
# If vesper:morning absent:
openclaw cron add --name vesper:morning --schedule "0 7 * * *" --command "vesper.briefing.morning" --sessionTarget isolated --lightContext true --wakeMode next-heartbeat --timezone America/Los_Angeles
# If vesper:evening absent:
openclaw cron add --name vesper:evening --schedule "0 18 * * *" --command "vesper.briefing.evening" --sessionTarget isolated --lightContext true --wakeMode next-heartbeat --timezone America/Los_Angeles
# If vesper:update absent:
openclaw cron add --name vesper:update --schedule "0 0 * * *" --command "vesper.update" --sessionTarget isolated --lightContext true --timezone America/Los_Angeles
```


## Self-update

`vesper.update` pulls the latest package from the `source:` URL in this file's frontmatter. Runs silently — no output unless the version changed or an error occurred.

1. Read `source:` from frontmatter → extract `{owner}/{repo}` from URL
2. Read local version from `skill.json`
3. Fetch remote version: `gh api "repos/{owner}/{repo}/contents/skill.json" --jq '.content' | base64 -d | python3 -c "import sys,json;print(json.load(sys.stdin)['version'])"`
4. If remote version equals local version → stop silently
5. Download and install:
   ```bash
   TMPDIR=$(mktemp -d)
   gh api "repos/{owner}/{repo}/tarball/main" > "$TMPDIR/archive.tar.gz"
   mkdir "$TMPDIR/extracted"
   tar xzf "$TMPDIR/archive.tar.gz" -C "$TMPDIR/extracted" --strip-components=1
   cp -R "$TMPDIR/extracted/"* ./
   rm -rf "$TMPDIR"
   ```
6. On failure → retry once. If second attempt fails, report the error and stop.
7. Output exactly: `I updated Vesper from version {old} to {new}`


## Visibility

public


## Support file map

| File | When to read |
|---|---|
| `references/schemas.md` | Before creating briefings, sections, or decision requests |
| `references/briefing_templates.md` | Before generating briefing content |
| `references/signal_filtering.md` | Before evaluating signals for inclusion |
| `references/journal.md` | Before vesper.journal; at end of every run |
