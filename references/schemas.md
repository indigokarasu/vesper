# Vesper Schemas

## Briefing
```json
{"briefing_id":"string","type":"string — morning|evening|manual","timestamp":"string","location":"string","sections":["BriefingSection"],"delivery_status":"string"}
```

## BriefingSection
```json
{"section_type":"string — today|messages|logistics|markets|decisions|system","section_marker":"string — ▪|✉|⚑|◈|⟡|⚙","content_items":["ContentItem"]}
```

## ContentItem
```json
{"item_id":"string","source_skill":"string","summary":"string","inline_links":[{"text":"string","uri":"string","uri_type":"string — gcal|maps|gmail|status"}],"decision_request":"DecisionRequest|null"}
```

## DecisionRequest
```json
{"decision_id":"string","option":"string","benefit":"string","cost":"string|null","status":"string — pending|accepted|ignored|expired"}
```

## SignalEvaluation
```json
{"signal_id":"string","source":"string","relevance_score":"number","included":"boolean","exclusion_reason":"string|null"}
```

## VesperBriefingFile
Written to `briefings/YYYY-WXX/YYYY-MM-DD-{type}.json` after every briefing generation. Read by Dispatch for delivery.
```json
{"briefing_id":"string","type":"string — morning|evening|manual","date":"string — YYYY-MM-DD","week":"string — YYYY-WXX","generated_at":"string","content":"string — rendered briefing text","sections":["BriefingSection"]}
```

## Default config.json
Written to `{agent_root}/commons/data/ocas-vesper/config.json` during initialization.
```json
{
  "skill_id": "ocas-vesper",
  "skill_version": "2.7.0",
  "config_version": "1",
  "created_at": "",
  "updated_at": "",
  "schedule": {
    "morning_window": "07:00-09:00",
    "evening_window": "17:00-19:00",
    "timezone": "America/Los_Angeles"
  },
  "sections": {
    "today": true,
    "messages": true,
    "logistics": true,
    "markets": true,
    "decisions": true,
    "system": true
  },
  "retention": {
    "days": 30,
    "max_records": 10000
  }
}
```

## Storage layout
```
{agent_root}/commons/data/ocas-vesper/
  config.json
  briefings.jsonl
  signals_evaluated.jsonl
  decisions_presented.jsonl
  decisions.jsonl
  intents.jsonl
  evidence.jsonl
  briefings/
    YYYY-WXX/
      YYYY-MM-DD-morning.json
      YYYY-MM-DD-evening.json

{agent_root}/commons/journals/ocas-vesper/
  YYYY-MM-DD/
    {run_id}.json
```
