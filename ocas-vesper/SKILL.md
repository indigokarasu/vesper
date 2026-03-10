---
name: ocas-vesper
description: >
  Daily briefing generator. Aggregates signals into concise morning and
  evening briefings. Surfaces outcomes and opportunities in natural
  language without exposing internal system processes.
---

# Vesper

Vesper generates concise daily briefings by aggregating signals from across the system. It presents outcomes and opportunities in natural assistant language while hiding internal processes.

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

## Core promise

Concise, actionable briefings. Signal, not noise. Opportunities surfaced without exposing the analysis that found them. Decisions framed as optional, not demanded.

## Commands

- `vesper.briefing.morning` — generate morning briefing
- `vesper.briefing.evening` — generate evening briefing
- `vesper.briefing.manual` — on-demand briefing
- `vesper.decisions.pending` — list unacted decision requests
- `vesper.config.set` — update schedule, sections, delivery
- `vesper.status` — last briefing time, pending decisions, schedule

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

## Behavior constraints

- No nagging — ignored decisions are treated as intentional
- No internal system terminology
- No references to architecture or analysis processes
- No speculative observations
- Only concrete outcomes and actionable opportunities

## Support file map

- `references/schemas.md` — Briefing, BriefingSection, ContentItem, DecisionRequest, SignalEvaluation
- `references/briefing_templates.md` — morning/evening structure, section formats, weather rules, opportunity presentation
- `references/signal_filtering.md` — inclusion/exclusion criteria, source expectations, Corvus opportunity handling

## Storage layout

```
.vesper/
  config.json
  briefings.jsonl
  signals_evaluated.jsonl
  decisions_presented.jsonl
  decisions.jsonl
```

## Validation rules

- Briefings contain only included signals, not excluded ones
- No internal system terminology in output
- Decision requests include option, benefit, and cost
- Weather appears only in morning briefing opening
