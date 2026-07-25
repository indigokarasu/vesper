# Signal Gathering

## Parallel signal fetching

For faster briefing generation, fetch signals from multiple sources in parallel using `delegate_task`. Known reliability:

| Source | Parallel-safe | Notes |
|--------|--------------|-------|
| Calendar (MCP) | ✓ | Native MCP tools work reliably in subagents |
| Gmail (MCP) | ⚠️ | Subagent OAuth may fail independently — connection state can be "initializing" even when direct calls work |
| Weather (curl) | ✓ | Stateless HTTP, no auth issues |
| Custodian | ✓ | File-based reads, no auth |
| Dispatch | ✓ | File-based reads, no auth |
| Rally | ✓ | File-based reads, no auth |

**Fallback pattern**: If a subagent returns an auth failure for Gmail, retry the query directly in the parent session. Do not block the entire briefing on one source's auth state.

## Signal evaluation workflow

1. Gather raw signals into a list: `{signal_id, source, raw_summary, relevance_score}`
2. Apply filtering rules from `references/signal_filtering.md`
3. For each included signal, create a `content_items` entry
4. For excluded signals, log to `signals_evaluated.jsonl` with `exclusion_reason`
5. Briefing JSONL entry should contain ONLY included signals in the `content` field

## Thin briefing example (2026-06-24)

When only email signals are available (no calendar events, no Custodian/Dispatch/Rally):

```
Good morning the owner

54°F right now, ☁️ overcast. Climbing to 59°F by 10am, still ☁️ overcast.
High of 67°F mid-afternoon, ☁️ overcast, then ⛅ partly cloudy around 4pm
at 62°F, dropping to a low of 53°F overnight.

✉ Messages
[Actionable email 1]
[Actionable email 2]

[No Today section — no calendar events]
[No Logistics section — no travel items]
[No Decisions section — no genuine decision signals]
```

This is correct behavior. Thin briefings are better than padded ones.