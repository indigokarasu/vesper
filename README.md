# 🌅 Vesper

Daily briefing generator aggregating signals from across the system.

**Skill name:** `ocas-vesper`
**Version:** 2.2.0
**Type:** system
**Layer:** Interface
**Author:** Indigo Karasu

---

## Files

| File | Purpose |
|---|---|
| `skill.json` | Package metadata and routing description |
| `SKILL.md` | Operational instructions for the agent |
| `references/` | Support files referenced by SKILL.md |

---

## Changelog

### 2.2.0 (2026-03-22)

- Added short-name routing aliases to skill.json description and SKILL.md frontmatter for natural invocation ('Scout', 'Sift', etc.)
- Added trigger phrases to descriptions for improved routing accuracy
- Cross-skill references in descriptions now use 'use X' format for routing clarity

### 2.1.0 (2026-03-22)

- Added Run completion section with explicit intake processing and journal write
- Added Initialization section with cron registration
- Added Background tasks section: vesper:morning (daily 7am), vesper:evening (daily 6pm)
- Removed non-conformant OCAS_ROOT environment variable reference

### 2.0.0 (2026-03-18)

- Initial build of all OCAS skills as a unified suite
