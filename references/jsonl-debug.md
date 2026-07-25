# JSONL Debugging Reference

## Diagnosing Corrupted briefings.jsonl Entries

When `briefings.jsonl` has a corrupted entry, you'll get `json.decoder.JSONDecodeError` when trying to parse it.

### Step 1: Find the broken line

```python
import json
<<<<<<< Updated upstream
with open('<hermes-home>/commons/data/ocas-vesper/briefings.jsonl', 'r') as f:
=======
with open('~/.hermes/commons/data/ocas-vesper/briefings.jsonl', 'r') as f:
>>>>>>> Stashed changes
    for i, line in enumerate(f, 1):
        line = line.strip()
        if not line: continue
        try:
            json.loads(line)
        except json.JSONDecodeError as e:
            print(f"Line {i}: ERROR at char {e.pos}: {e.msg}")
```

### Step 2: Analyze the bracket mismatch

For each corrupted line, count opens vs closes in the `sections` array portion:

```python
line = "...corrupted line..."
idx = line.find('"sections"')
chunk = line[idx:]
opens_b = chunk.count('{')
closes_b = chunk.count('}')
opens_s = chunk.count('[')
closes_s = chunk.count(']')
print(f"Braces: {{={opens_b}, }}={closes_b}, diff={opens_b-closes_b}")
print(f"Brackets: [={opens_s}, ]={closes_s}, diff={opens_s-closes_s}")
```

A negative diff means extra closing brackets. A positive diff means missing closing brackets.

### Step 3: Known corruption pattern — missing content_items item close

**Symptom:** `JSONDecodeError: Expecting ',' delimiter` at the `]` after a decision_request's `"status":"pending"}`.

**Root cause:** The content_items item object `{"item_id":..., "decision_request":{...}}` is missing its closing `}`. The sequence `"status":"pending"}]}]` should be `"status":"pending"}}]}]`.

**Fix:**
```python
fixed = line.replace('"status":"pending"}]}],"delivered"', '"status":"pending"}}]}],"delivered"')
```

**Verification:**
```python
json.loads(fixed)  # Should not raise
```

### Step 4: Write back

```python
<<<<<<< Updated upstream
with open('<hermes-home>/commons/data/ocas-vesper/briefings.jsonl', 'w') as f:
=======
with open('~/.hermes/commons/data/ocas-vesper/briefings.jsonl', 'w') as f:
>>>>>>> Stashed changes
    for line in fixed_lines:
        f.write(line + '\n')
```

## UTF-8 Multi-byte Character Caution

The briefing text contains emoji section markers (▪, ✉, ⚙, ⟡) and em-dashes (—) which are multi-byte UTF-8. Byte positions from raw reads will differ from character positions in Python strings. Always decode to string first before doing character-position analysis:

```python
with open(path, 'rb') as f:
    raw = f.read()
text = raw.decode('utf-8')  # Now character positions match
```