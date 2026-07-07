# Briefing HTML Templates

Minimal HTML suitable for Gmail rendering. No markdown syntax.

## Morning / Evening Briefing Structure

```html
<p>Good morning</p>
<p style="font-size: 15px;">{weather_emoji} {temp}°F. {10am_emoji} {10am_temp}°F by 10am. High of {high}°F, {4pm_emoji} {4pm_temp}°F at 4pm, dropping to {overnight_temp}°F overnight.</p>
<!-- Weather line appears in MORNING briefings only -->
<p><strong>▪ Today/Tomorrow</strong></p>
<p>{Calendar events or "clear day"}</p>
<p><strong>✉ Inbox</strong></p>
<p>{Top 5 interesting threads with Gmail links}</p>
<p><strong>◈ Markets</strong></p>
<p>{Rally portfolio + market data}</p>
<p><strong>⟡ Decisions</strong></p>
<p>{Pending items}</p>
```

Evening briefings use `<p>Good evening</p>` and omit the weather line.

## Rendering Notes

- Output is plain text or minimal HTML suitable for Gmail rendering. No markdown syntax (`#`, `**`, `---`).
- Section headers use monochrome extended characters: ▪ Today, ✉ Messages, ⚑ Logistics, ◈ Markets, ⟡ Decisions, ⚙ System.
- Sections with no content are omitted entirely. Do not render empty sections or "nothing to report" placeholders.
- Links are inline: the relevant words become the anchor text. No trailing link labels.
- URI formats:
  - gcal: `https://calendar.google.com/calendar/event?eid={event_id}`
  - maps: `https://maps.google.com/?q={place+name+address}`
  - gmail: `https://mail.google.com/mail/u/0/#inbox/{thread_id}`
