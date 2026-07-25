# Vesper OKRs

Universal OKRs from spec-ocas-journal.md apply to all runs.

```yaml
skill_okrs:
  - name: signal_precision
    metric: fraction of included signals rated actionable by user
    direction: maximize
    target: 0.85
    evaluation_window: 30_runs
  - name: terminology_compliance
    metric: fraction of briefings free of internal system terminology
    direction: maximize
    target: 1.0
    evaluation_window: 30_runs
  - name: decision_framing
    metric: fraction of decision requests including option, benefit, and cost
    direction: maximize
    target: 1.0
    evaluation_window: 30_runs
  - name: schedule_adherence
    metric: fraction of briefings generated within the configured schedule window
    direction: maximize
    target: 0.95
    evaluation_window: 30_runs
  - name: data_integrity
    metric: fraction of briefing runs with zero dropped or malformed signals
    direction: maximize
    target: 0.99
    evaluation_window: 30_runs
```