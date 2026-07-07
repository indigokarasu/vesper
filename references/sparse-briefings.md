# Sparse Briefings

When most or all upstream signal sources are unavailable, the briefing will be thin. This is correct behavior, not a failure.

## When it happens

- Corvus: no proposals directory or empty
- Custodian: no anomaly alerts
- Dispatch: no summary report
- Rally: no daily report
- Calendar: no events in range
- Gmail: no actionable messages

## What to do

1. Still fetch weather (morning) — this is always available and grounds the briefing.
2. Still check Gmail — even without Dispatch summaries, direct email checks can surface actionable items.
3. Write the briefing with whatever signals exist. A briefing with only weather + 1-2 messages is valid.
4. If literally nothing actionable exists (no weather-relevant events, no messages, no signals), consider suppressing the briefing entirely — mark as `delivery_status: "silent"` with reason "No actionable signals available."

## Example thin briefing

```
Good morning the owner

52°F right now, 🌧 rain, warming to 58°F by 10am with clearing skies. High of 64°F mid-afternoon, ⛅ partly cloudy, 60°F at 4pm, 🌤 mainly clear, dropping to a low of 50°F overnight.

✉ Messages
GitHub notified you that a new SSH key was added to your account. No action needed if this was you.
```

## Evening-specific sparse briefings

Evening briefings have no weather section, so they can feel even thinner than morning briefings. This is normal.

When the only available signal is a routine email (shipment notification, marketing newsletter, etc.):
- Include it only if it has planning value (e.g., overnight delivery window affects tomorrow morning).
- Exclude pure marketing/newsletter emails with no action needed.
- A 2-line briefing (greeting + one sentence about tomorrow's delivery) is valid.
- A closing line like "No calendar events tomorrow either. Quiet end to the day." is acceptable — it's informational closure, not padding.

Example minimal evening briefing:
```
Good evening the owner

✉ Messages
Amazon shipped your Cat6 patch cable order — two packs, $39.62 total. Arriving overnight tomorrow, delivery window 7 to 11 AM. No action needed, just flagging so you know it's coming.

No calendar events tomorrow either. Quiet end to the day.
```

## Tomorrow-empty, day-after-has-events

When tomorrow (e.g. Sunday) has no events but the next business day does, include the next event in the Today section with a clear day label. The section still uses `section_type: "today"` and `section_marker: "▪"`, but the content distinguishes the days:

```
▪ Tomorrow
No calendar events tomorrow. Quiet Sunday.

New patient visit with Sophie Patzek Monday at 8:45am.
```

This is correct — the "Today" section in evening briefings is really "upcoming," not strictly "tomorrow." Labeling the day avoids ambiguity.

## Weather-only briefings (all other signals absent)

When the only available signal is weather (common on weekends or quiet mornings), the briefing is just greeting + weather paragraph. No sections at all.

**Correct JSON structure** — `sections` is an empty array:
```json
{
  "briefing_id": "vesper-morning-20260628-0600",
  "type": "morning",
  "date": "2026-06-28",
  "week": "2026-W26",
  "generated_at": "2026-06-28T06:00:00-07:00",
  "content": "Good morning the owner\n\n50°F right now, ☀️ clear. Warming to 68°F by 10am, ☀️ sunny. High of 76°F mid-afternoon, ☀️ sunny, holding around 75°F through 4pm. Low near 50°F overnight. Tomorrow looks just as good — ☀️ clear, high of 77°F, low around 53°F.",
  "delivery_status": "pending",
  "delivered": false,
  "sections": []
}
```

**Do NOT add an empty section object** as a placeholder:
```json
// WRONG — empty section object violates "no empty sections" rule
"sections": [
  {
    "section_type": "today",
    "section_marker": "▪",
    "content_items": []
  }
]
```

The quality check (`check_sections_have_content`) will flag empty section objects. If there are no actionable signals beyond weather, `sections` must be `[]`.

## Anti-pattern

Do not pad thin briefings with:
- Recap of yesterday's weather
- Speculative market commentary
- Reminders about routine tasks that aren't time-sensitive
- Restatements of the greeting ("hope you slept well")
- Empty section objects as placeholders

Thin is honest. Silence is acceptable when there's nothing to say.
