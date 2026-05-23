# 🌅 Vesper

> **Daily briefing generator — aggregates signals from all skills into concise morning and evening briefings.**

## Why Vesper?

When you have 26+ skills generating signals, you need someone to tell you what actually matters. Vesper aggregates signals from every skill — portfolio outcomes from Rally, insight proposals from Corvus, pending commitments from Dispatch, upcoming calendar events from Sands — and assembles them into a concise, conversational briefing. No internal architecture, no system terminology — just what you need to know.

Skill packages follow the [agentskills.io](https://agentskills.io/specification) open standard and are compatible with OpenClaw, Hermes Agent, Claude, and any agentskills.io-compliant client.

## Quick Start

```
# Morning briefing
"What's my morning briefing?"

# Evening briefing
"What's on tap for tomorrow?"

# On-demand
"Brief me now"
```

Vesper auto-initializes on first use, registering morning and evening cron jobs.

## What It Does

Vesper aggregates signals from every other skill and assembles them into morning or evening briefings in natural language. Signal filtering is strict: routine background activity, speculative observations, and already-experienced events are excluded. The result is a briefing that earns attention rather than demanding it. Vesper also presents pending decision requests with option, benefit, and cost framing.

## Commands

| Command | Description |
|---|---|
| `vesper.briefing.morning` | Generate morning briefing |
| `vesper.briefing.evening` | Generate evening briefing |
| `vesper.briefing.manual` | On-demand briefing |
| `vesper.decisions.pending` | List unacted decision requests |
| `vesper.config.set` | Update schedule, sections, delivery |
| `vesper.status` | Last briefing time, pending decisions |
| `vesper.journal` | Write journal |
| `vesper.update` | Self-update |

## Dependencies

- [Corvus](https://github.com/indigokarasu/corvus) — receives InsightProposal files
- [Dispatch](https://github.com/indigokarasu/dispatch) — may deliver briefings
- [Rally](https://github.com/indigokarasu/rally) — portfolio outcome signals
- [Sands](https://github.com/indigokarasu/sands) — calendar events
- Calendar and Weather APIs

## Scheduled Tasks

| Job | Schedule | Command |
|---|---|---|
| `vesper:morning` | `0 7 * * *` | Morning briefing |
| `vesper:evening` | `0 18 * * *` | Evening briefing |
| `vesper:update` | `0 0 * * *` | Self-update |

## Changelog

### v2.10.0 — April 26, 2026
- Added briefing delivery and diagnostic scripts

### v2.8.4 — April 12, 2026
- Weather rendering and briefing HTML structure

### v2.0.0 — March 18, 2026
- Initial release

---

*Vesper is part of the [OCAS Agent Suite](https://github.com/indigokarasu).*