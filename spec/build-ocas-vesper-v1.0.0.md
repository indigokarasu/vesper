---
name: ocas-vesper
version: 1.0.0
author: Indigo Karasu
email: mx.indigo.karasu@gmail.com
description: Generates concise morning and evening briefings for the system owner by aggregating relevant signals and presenting them as a daily update.
privacy: public
category: orchestration
---

# Skill: ocas-vesper

## Purpose

ocas-vesper generates daily briefings for the system owner.

The skill gathers signals from across the environment and converts them into two concise reports: a morning briefing that prepares the owner for the day and an evening briefing that surfaces meaningful developments.

The skill presents outcomes and opportunities in natural assistant language while hiding internal system processes.

---

# Invocation

The skill supports three invocation modes.

Automatic invocation (morning)  
Triggered during the configured morning window.

Automatic invocation (evening)  
Triggered during the configured evening window.

Manual invocation  
Triggered when the owner requests a briefing.

---

# Inputs

The skill evaluates signals from the environment, including:

calendar events  
communication threads  
messages  
financial logs  
system artifacts  
long-term memory records  
pattern signals  
journal entries

Each source may produce candidate signals.

---

# Signal Filtering

Signals are evaluated for briefing relevance.

A signal is included if it represents:

actionable information  
an outcome with meaningful impact  
a change affecting plans or awareness  
an opportunity produced from multiple signals  
information useful for upcoming preparation

Signals are excluded when they represent:

routine background activity  
events already experienced directly by the owner  
internal reasoning or system processes  
speculative or curiosity-only observations

---

# Morning Briefing Generation

The morning briefing prepares the owner for the upcoming day.

Structure:

Greeting

Weather summary for the relevant location(s)

Optional sections:

📅 Today  
Upcoming meetings or events that may require preparation.

✉️ Messages  
Important communications that require attention.

🧭 Logistics  
Scheduling coordination or practical opportunities.

📈 Markets  
Financial outcomes written in plain language.

🔐 Decisions  
Optional approvals involving spending or permissions.

🛠 System  
Only when a meaningful system capability changed.

Weather formatting rules:

Weather appears in the opening paragraph without a section header.

Example

Today in San Francisco it will be sunny ☀️ with a high around 72°F.

If travel occurs that day, weather may include multiple locations.

---

# Evening Briefing Generation

The evening briefing surfaces developments that occurred during the day.

Structure:

Greeting

Optional sections:

✉️ Messages  
Important replies or developments.

📈 Markets  
Financial outcomes that occurred during the day.

🧭 Logistics  
Items affecting the following day.

🔐 Decisions  
Non-urgent approvals or opportunities.

🛠 System  
System improvements that affect the owner.

The evening briefing never summarizes meetings already attended and never reports past weather.

---

# Opportunity Presentation

Some signals originate from detected behavioral patterns.

The briefing never exposes pattern analysis.

Instead it surfaces the resulting opportunity in natural language.

Example

🧭 Logistics  
There’s an opening at [[Gloss Nail Spa]] at 4:00 PM next Wednesday and that time is free on your calendar. Would you like me to book it?

The briefing presents the opportunity without explaining the underlying analysis.

---

# Formatting Rules

Briefings follow consistent formatting constraints.

conversational paragraphs  
section headers use emoji  
links use [[artifact name]] format  
sender names appear outside link text

Example

Carlos regarding [[Countertop Installation Scheduling]].

Financial language must remain understandable to non-experts.

---

# Decision Requests

Decision entries must include:

the option  
the benefit or rationale  
the cost or scope if applicable

Requests are framed as optional opportunities rather than requirements.

Example

I found a tool called [[Granola Meeting Recorder]] that converts meeting recordings into structured notes. It costs $18 per month and would integrate with recorded meetings. If you’d like I can set it up.

---

# Behavior Constraints

The skill follows strict assistant behavior rules.

no nagging  
ignored decisions are treated as intentional  
no internal system terminology  
no references to architecture or analysis  
no speculative observations

Only concrete outcomes and actionable opportunities are surfaced.

---

# Outputs

The skill produces a single structured briefing message.

Possible delivery channels include:

email  
messaging  
direct assistant interaction

---

# Journals

The skill writes journal entries recording:

signals evaluated  
signals surfaced  
decisions presented  
briefing delivery events

## Skill OKRs

signal relevance accuracy  
briefing signal-to-noise ratio  
decision engagement rate  
artifact link usage

---

## Skill Identity

- Skill name: `ocas-vesper`
- Version: `1.0.0`
- Skill type: `system`
- Author: `Indigo Karasu`
- Email: `mx.indigo.karasu@gmail.com`

---

## Universal OKRs

This skill must implement the universal OKRs defined in the OCAS Journal Specification (spec-ocas-Journals.md).

Required universal OKRs:

- Reliability: success_rate >= 0.95, retry_rate <= 0.10
- Validation Integrity: validation_failure_rate <= 0.05
- Efficiency: latency trending downward, repair_events <= 0.05
- Context Stability: context_utilization <= 0.70
- Observability: journal_completeness = 1.0

The Vesper-specific OKRs defined in this spec measure signal relevance and briefing quality.

---

## Responsibility Boundary

Vesper generates daily briefings by aggregating and filtering signals from across the system.

Vesper does not analyze patterns or generate insights. Pattern analysis belongs to Corvus.

Vesper does not send messages directly. Message delivery belongs to Dispatch.

---

## Optional Skill Cooperation

This skill may cooperate with other skills when present but must never depend on them.
If a cooperating skill is absent, this skill must still function normally.

- Corvus — receive pattern-derived opportunity signals for briefing inclusion.
- Dispatch — receive communication thread summaries for message sections.
- Rally — receive portfolio outcome summaries for market sections.
- Elephas — query Chronicle for entity context when composing briefing items.
- Relay — receive device context for location-aware briefing content.

---

## Journal Outputs

This skill emits the following journal types as defined in the OCAS Journal Specification (spec-ocas-Journals.md):

- Action Journal

Vesper emits Action Journal entries recording briefing generation events, signal selection decisions, and delivery confirmations.

---

## Visibility

visibility: public

---

## Required Package Output

Forge must produce a complete Agent Skill package:

```text
ocas-vesper/
  skill.json
  SKILL.md
  references/
    schemas.md
    briefing_templates.md
    signal_filtering.md
```

### `skill.json` Requirements

Create a valid `skill.json` with:
- `name`: `ocas-vesper`
- `version`: `1.0.0`
- `description`: routing-optimized text
- `author`: `Indigo Karasu`
- `email`: `mx.indigo.karasu@gmail.com`

The description must make clear that this skill is for:
- generating concise morning and evening briefings
- aggregating signals from across the system into actionable daily updates
- surfacing opportunities, decisions, and developments in natural language
- presenting outcomes without exposing internal system processes

### `SKILL.md` Requirements

`SKILL.md` must begin on line 1 with valid YAML frontmatter delimited by `---`.

Target size: 150 to 250 lines.

#### Required `SKILL.md` Sections

The markdown body must contain these sections in this order:

1. `# Vesper`
2. `## When to use`
3. `## When not to use`
4. `## Core promise`
5. `## Commands`
6. `## Invocation modes`
7. `## Signal filtering rules`
8. `## Formatting rules`
9. `## Behavior constraints`
10. `## Support file map`
11. `## Storage layout`
12. `## Validation rules`

### Commands

The built skill must implement these commands:

- `vesper.briefing.morning` — generate the morning briefing for the configured location(s)
- `vesper.briefing.evening` — generate the evening briefing
- `vesper.briefing.manual` — generate an on-demand briefing outside the scheduled windows
- `vesper.decisions.pending` — list decision requests that have not been acted on
- `vesper.config.set` — update briefing configuration (time windows, sections, delivery channel)
- `vesper.status` — return current state including last briefing time, pending decisions, and configured schedule

### Storage Layout

```text
.vesper/
  config.json
  briefings.jsonl
  signals_evaluated.jsonl
  decisions_presented.jsonl
  decisions.jsonl
```

### Config

File: `.vesper/config.json`

Required fields:
- `schedule.morning_window`: time range for automatic morning briefing
- `schedule.evening_window`: time range for automatic evening briefing
- `schedule.timezone`: timezone for briefing schedule
- `location.primary`: primary location for weather and logistics
- `location.travel_aware`: whether to include travel destination weather
- `sections.enabled`: list of enabled briefing sections
- `delivery.channel`: delivery channel (email, messaging, direct)
- `behavior.nag_suppression`: whether ignored decisions are suppressed from future briefings

### `references/schemas.md`

Must define schemas for:
- `Briefing` — briefing_id, type (morning|evening|manual), timestamp, location, sections, delivery_status
- `BriefingSection` — section_type, emoji_header, content_items
- `ContentItem` — item_id, source_skill, summary, artifact_links, decision_request
- `DecisionRequest` — decision_id, option, benefit, cost, status (pending|accepted|ignored|expired)
- `SignalEvaluation` — signal_id, source, relevance_score, included, exclusion_reason
- `DecisionRecord` — decision_id, decision_type, evidence_refs, outcome, timestamp

### `references/briefing_templates.md`

Must document:
- morning briefing structure: greeting, weather, then optional sections (Today, Messages, Logistics, Markets, Decisions, System)
- evening briefing structure: greeting, then optional sections (Messages, Markets, Logistics, Decisions, System)
- weather formatting rules (inline in opening paragraph, no section header, multi-location for travel days)
- section emoji headers (📅 Today, ✉️ Messages, 🧭 Logistics, 📈 Markets, 🔐 Decisions, 🛠 System)
- link formatting (`[[artifact name]]` format)
- sender name formatting (outside link text)
- decision request formatting (option, benefit, cost, framed as optional)
- opportunity presentation (surface the opportunity, never expose the underlying analysis)

### `references/signal_filtering.md`

Must document:
- inclusion criteria: actionable information, meaningful outcomes, plan-affecting changes, multi-signal opportunities, preparation-useful information
- exclusion criteria: routine background activity, already-experienced events, internal system reasoning, speculative observations
- evening-specific exclusions: no past weather, no summaries of attended meetings
- signal source expectations: calendar, communications, financial logs, memory records, pattern signals, journal entries
- how Corvus-originated opportunity signals are presented without exposing pattern analysis


---

## Final Response Format for the Coder

Return:

1. package tree
2. full contents of every file
3. brief validation summary

Do not return planning commentary, process narration, or references to absent documents.
