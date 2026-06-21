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
Good morning owner

52°F right now, 🌧 rain, warming to 58°F by 10am with clearing skies. High of 64°F mid-afternoon, ⛅ partly cloudy, 60°F at 4pm, 🌤 mainly clear, dropping to a low of 50°F overnight.

✉ Messages
GitHub notified you that a new SSH key was added to your account. No action needed if this was you.
```

## Anti-pattern

Do not pad thin briefings with:
- Recap of yesterday's weather
- Speculative market commentary
- Reminders about routine tasks that aren't time-sensitive
- Restatements of the greeting ("hope you slept well")

Thin is honest. Silence is acceptable when there's nothing to say.
