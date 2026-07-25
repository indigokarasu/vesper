# Interactive Menu

When invoked interactively (via `/` command), present a two-level menu using the `clarify` tool so the user can pick which function to run.

**Level 1 — Category selection** (max 4 choices):

```python
result = clarify(
    question="What would you like to do?",
    choices=[
        "Briefings — generate morning, evening, or manual briefings",
        "Deliver & Check — deliver pending briefings, check undelivered",
        "Decisions & Config — pending decisions, set configuration values",
        "Status — show system status",
    ]
)
```

**Level 2 — Action selection** based on Level 1 choice:

- **Briefings** → clarify with choices: "briefing.morning — Generate morning briefing", "briefing.evening — Generate evening briefing", "briefing.manual — Generate custom briefing"
- **Deliver & Check** → clarify with choices: "briefing.deliver — Deliver pending briefings", "briefing.check — Check undelivered briefings"
- **Decisions & Config** → clarify with choices: "decisions.pending — List pending decisions", "config.set — Set configuration value"
- **Status** → run "status — Show system status" directly (single action — no sub-menu needed)

After the user selects an action, execute it following the relevant procedure in this skill. Loop back to the menu after each action completes, until the user chooses to exit or sends `/stop`.

### Response parsing

Match the user's response against the full choice string. Extract the action key by splitting on `" — "` and taking the first segment. If the response doesn't match any known choice (user typed free-form via "Other"), match key prefixes case-insensitively. Re-present the current menu level on no match.

### Platform adaptation

On CLI, choices are navigable with arrow keys. On messaging platforms, choices render as a numbered list. The two-level hierarchy ensures no more than 4 options appear at any level on any platform.




Vesper is the system's daily voice — it aggregates signals from every other skill and presents what matters as a concise, conversational morning or evening briefing, surfacing concrete outcomes, upcoming decisions, and actionable opportunities without exposing any internal architecture or analysis processes.
