# 🌆 Vesper

Vesper generates personalized briefings at configurable times (morning/evening). It aggregates signals from multiple systems—outcomes, opportunities, recommendations, briefings—filters for relevance, and synthesizes concise, actionable natural language summaries. Vesper excludes routine activity and speculative reasoning, surfacing only what's decision-relevant.

---

## 📖 Overview

Daily briefing generator. Aggregates signals into concise morning and evening briefings. Surfaces outcomes and opportunities in natural language.

---

## 🔧 Tool Surface

- `vesper.briefing.generate` — generate briefing for specified time
- `vesper.signals.ingest` — ingest signal (outcome, opportunity, etc.) for briefing
- `vesper.schedule.set` — configure briefing times
- `vesper.filters.configure` — set signal filtering and relevance rules
- `vesper.briefing.history` — past briefings with signal composition
- `vesper.status` — next briefing time, pending signals, filter configuration

---

## 📊 Output & Journals

Produces: Produces briefing records with signal composition, filtering decisions, and synthesis outputs.

---

## ⏱️ Heartbeat & Background Tasks

**Scheduled Briefing Generation**: Vesper runs at configured times to generate briefings. Background signal filtering runs continuously to surface relevant signals.

---

## 📚 Documentation

Read `SKILL.md` for operational details, schemas, and validation rules.

See `references/` for detailed specifications and examples.

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
