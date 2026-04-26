## [2.10.0] - 2026-04-26

### Added
- `scripts/briefing_deliver.py` — Gmail-based briefing delivery (moved from `ocas-dispatch` per OCAS boundary discipline; briefing delivery is Vesper's responsibility, not Dispatch's)
- `scripts/check_briefing.py` — diagnostic utility to inspect the latest briefing file
- `vesper.briefing.deliver` and `vesper.briefing.check` commands documenting the new scripts

## [2.9.0] - 2026-04-18

### Changed
- Extracted delivery troubleshooting runbook (trigger conditions, three failure modes, diagnostic checklist) from SKILL.md into `references/delivery-troubleshooting.md`; SKILL.md now carries a short pointer under Error handling.
- Moved WMO weather code → emoji table and Open-Meteo rendering notes into `references/weather-codes.md`; SKILL.md Weather rendering section reduced to a pointer.
- Moved HTML briefing template into `references/html-templates.md`; SKILL.md Briefing email structure section reduced to a pointer.
- Fixed corrupted HTML artifacts (`<<pp>`, `<<strongstrong>`) introduced in the briefing-pipeline merge; now rendered correctly as `<p>` and `<strong>` in the template reference.
- Consolidated Account Isolation rules under a dedicated top-level section.

### Added
- `references/delivery-troubleshooting.md`
- `references/weather-codes.md`
- `references/html-templates.md`
- Support file map entries for the three new references.

## [2.8.4] - 2026-04-12

### Added
- Weather rendering: Open-Meteo Fahrenheit parameter, WMO code→emoji mapping table
- Briefing email HTML structure documented with correct section order
- Weather line appears in morning briefings only (clarified)

## [2026-04-04] Spec Compliance Update

### Changes
- Added missing SKILL.md sections per ocas-skill-authoring-rules.md
- Updated skill.json with required metadata fields
- Ensured all storage layouts and journal paths are properly declared
- Aligned ontology and background task declarations with spec-ocas-ontology.md

### Validation
- ✓ All required SKILL.md sections present
- ✓ All skill.json fields complete
- ✓ Storage layout properly declared
- ✓ Journal output paths configured
- ✓ Version: 2.7.0 → 2.7.1

# CHANGELOG

## [2.8.1] - 2026-04-08

### Storage Architecture Update

- Replaced $OCAS_DATA_ROOT variable with platform-native {agent_root}/commons/ convention
- Replaced intake directory pattern with journal payload convention
- Added errors/ as universal storage root alongside journals/
- Inter-skill communication now flows through typed journal payload fields
- No invented environment variables — skills ask the agent for its root directory


## [2.8.0] - 2026-04-08

### Multi-Platform Compatibility Migration

- Adopted agentskills.io open standard for skill packaging
- Replaced skill.json with YAML frontmatter in SKILL.md
- Replaced hardcoded ~/openclaw/ paths with {agent_root}/commons/ for platform portability
- Abstracted cron/heartbeat registration to declarative metadata pattern
- Added metadata.hermes and metadata.openclaw extension points
- Compatible with both OpenClaw and Hermes Agent


## [2.7.0] - 2026-04-03

### Changed
- Briefing output format: plain text/HTML for Gmail rendering, no markdown syntax
- Section markers: monochrome extended characters (▪ ✉ ⚑ ◈ ⟡ ⚙) replace color emoji headers
- Weather: narrative format with emoji directly before condition words, includes 10am/4pm commute forecasts, Friday weekend forecast
- Greeting: "Good morning owner" / "Good evening owner", no trailing punctuation
- Links: inline anchor text on relevant words (gcal, maps, gmail thread URIs), no trailing link labels
- Markets: morning shows previous close with change, evening shows open-to-close with change
- Silence on normal: empty sections omitted entirely, no "no flags" or normalcy confirmations
- ContentItem schema: `artifact_links` replaced with `inline_links` array (text, uri, uri_type)
- BriefingSection schema: `emoji_header` renamed to `section_marker`

### Added
- Vibes (ocas-vibes) cooperation: reads voice identity and anti-AI rules when present
- Silence-on-normal behavior constraint
- Weather emoji mapping table in briefing templates
- Link URI pattern reference (gcal, maps, gmail, status)

## [2.6.0] - 2026-04-02

### Added
- Structured entity observations in journal payloads (`entities_observed`, `relationships_observed`, `preferences_observed`)
- `user_relevance` tagging on journal observations (`user` for calendar/task entities, `agent_only` for external news context)
- Elephas journal cooperation in skill cooperation section

## 2.4.1 — 2026-03-30

### Added
- Ontology mapping: Vesper explicitly documented as aggregation-only, no entity extraction

### Changed
- Rally cooperation entry: clarified as cooperative read (Vesper reads daily report file)
- Dispatch cooperation entry: clarified as Vesper-initiated session-scoped request

## Prior

See git log for earlier history.
