# Vesper inter-skill interfaces

Contracts for reading data produced by other skills. Vesper is a consumer here — it surfaces outcomes; it does not act.

## Custodian → Vesper

InsightProposal files (`anomaly_alert`) at `{agent_root}/commons/data/ocas-custodian/proposals/{proposal_id}.json`. Cooperative read; consumed proposal IDs are tracked in `signals_evaluated.jsonl`.

## Mentor + Finch → Vesper

Project tags + changes feed the ◆ Projects section. Read only; see `references/briefing_templates.md`.

## Dispatch → Vesper

`DispatchSummaryReport` at `{agent_root}/commons/data/ocas-dispatch/reports/YYYY-MM-DD-{period}.json` → Messages section.

**Messages must come from bodies, not counts.** A count-based triage reports `status: ok` while never opening a message body, so a paid consultation invite and a stalled application stay invisible. Require a report whose items were produced by reading thread bodies and scoring for value (`opportunity_triage.py`). Reject noise by CONTENT, not sender convention (`noreply`/`donotreply` is what legitimate recruiters use). `tests/test_smoke.py` pins the delivery-status logic the sender depends on.

## Rally → Vesper

Daily portfolio reports at `{agent_root}/commons/data/ocas-rally/reports/YYYY-MM-DD-daily.json` → Markets section.

## Intake polling (Sands / Voyage / Spot / Taste)

Merge briefs from `{agent_root}/commons/data/ocas-vesper/intake/` into schedule/agenda; clean consumed briefs; omit gracefully if absent.

## Vesper → Dispatch

Completed briefings in `briefings/` (see `references/schemas.md`). Dispatch picks them up for delivery (email only — see `references/delivery-channel.md`).
