# Vesper run completion protocol

Read this before running a generator cron (`vesper:morning` / `vesper:evening`) or a manual briefing run. It is the full version of the SKILL.md "Run completion" section.

## 1. Duplicate-fire guard — run FIRST, before gathering any signals

Generator crons re-fire routinely; rewriting today's canonical file resets `delivered` to false and emails Jared a duplicate briefing with identical content.

Run `python3 scripts/dup_guard.py --type <morning|evening>`:

- **exit 3** = duplicate: today's briefing for this type already generated and delivered. Do not regenerate, do not re-deliver. Reconcile `briefings.jsonl` if it drifted from the canonical file, journal the skip, and stop.
- **exit 0** = proceed.

The guard mirrors `briefing_deliver.status_of` locally (cross-repo import broke CI, so it's kept local per the code comment) so guard and sender cannot disagree; do not reimplement the delivery rule locally.

## 2. Apply Vibes rules

Apply voice rules from SOUL.md directly (no em dashes, no "the user", no meta-narration, no "Now I have…"). **Do NOT load ocas-vibes via skill_view** — its rules are already embedded in SOUL.md/AGENTS.md.

## 3. Gather signals

Read InsightProposal files from Custodian `proposals/` directory. Apply signal filtering (see `references/signal_filtering.md`). Track consumed `proposal_id` values in `signals_evaluated.jsonl` to avoid reprocessing. Read Dispatch summary and Rally daily report if present. For parallel signal gathering, `delegate_task` works for calendar queries but subagent Gmail OAuth may fail independently — always have a direct fallback.

## 4. Write the briefing file

Write to `{agent_root}/commons/data/ocas-vesper/briefings/YYYY-WXX/YYYY-MM-DD-{type}.json` using the `VesperBriefingFile` schema. Create the week directory if absent.

**Path is non-negotiable** — `briefings/YYYY-WXX/YYYY-MM-DD-{type}.json` is the delivery contract. If user instructions specify a different path (e.g., `morning/` or `evening/`), follow the schema for the canonical location AND save a copy to the requested path. The copy and the canonical file must be identical at write time; only delivery tracking (via `briefings.jsonl`) applies to the canonical path. Note the divergence in the journal.

## 5. Quality check

Re-read the generated briefing file and verify:

- **(a)** No internal system terminology leaked through (no skill IDs, database references, or technical jargon — use **whole-word matching**, not substring matching, to avoid false positives like "DB" matching inside "Handbuilding").
- **(a2)** No internal maintenance leaked through (owner's directive, mechanically enforced by `quality_check.py` check 3f `check_internal_maintenance` against every section AND the rendered `content`): the briefing must not narrate system status, self-repair, incident counts, root-cause work, diagnostics, or triage metadata (tier/confidence, proposal IDs). A missing data source IS allowed ("calendar sync unavailable, so today's events do not appear here"). Maintenance-only System sections are dropped or rewritten. See `references/gotchas.md`.
- **(b)** All included sections have actual content — no empty sections.
- **(c)** The greeting matches the time-of-day format.
- **(d)** `signals_evaluated.jsonl` was updated with all consumed proposal IDs.
- **(e)** Every decision item traces to a real upstream signal — no fabricated or template-copied decisions.

**Pitfall:** `quality_check.py`'s `check_decisions_trace` checks that decision summaries reference the upstream source skill name (e.g., "Dispatch", "Rally", "Custodian") as a whole word in the `summary` field. If the summary only describes the event without naming the source skill, the trace check fails. Always include the source skill name (e.g., "Dispatch email check surfaced...", "Rally daily report shows...") in decision summaries.

If any check fails, regenerate the briefing and re-run `quality_check.py` before persisting.

**Tip:** `python3 scripts/quality_check.py <briefing-file.json> [signals-evaluated.jsonl]` implements all five sub-checks with whole-word regex matching. Returns `PASS` or `FAIL` with the specific terms/sections to fix.

## 6. Persist

Only after the briefing passes the quality check, persist the completed briefing record to `briefings.jsonl` and evaluated signals to `signals_evaluated.jsonl`. Log material decisions to `decisions.jsonl`. Do not append these files before the quality check succeeds — the JSONL is the delivery contract and must match the final briefing exactly.

## Append-only ledgers (never rewrite)

Never run a whole-file dedupe, dedent, re-serialize, or "normalize" pass over `briefings.jsonl`, `decisions.jsonl`, or `signals_evaluated.jsonl`. On 2026-10-01 an evening run appended two ledger lines, then ran a de-dupe that keyed on `(signal_id, briefing_id)` **globally** instead of scoping to the current run. It deleted 38 legitimate historical entries; no git mirror or backup covered the loss (the mirrors stop at 2026-06-15).

- If a line looks wrong, APPEND a corrected line and leave the original byte-for-byte in place.
- Corrupted sibling lines are handled surgically by `scripts/delivery_check.py`, the only sanctioned writer besides plain append.
- A same-run duplicate is left alone unless you remove it by line number you just wrote, not by global key match.

## 7. Journal

Write the journal via `vesper.journal` (end of every run).
