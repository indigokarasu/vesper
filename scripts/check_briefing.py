import json, datetime, os, glob
from pathlib import Path

AGENT_ROOT = Path(os.environ.get("AGENT_ROOT", Path.home() / ".hermes"))

# Read the latest Vesper briefing
briefings_dir = str(AGENT_ROOT / "commons/data/ocas-vesper/briefings")
today = datetime.date.today().isoformat()

# Find the latest briefing file
all_files = glob.glob(f"{briefings_dir}*/*{today}*.json")
if not all_files:
    # Try most recent
    for week in sorted(os.listdir(briefings_dir), reverse=True):
        week_dir = os.path.join(briefings_dir, week)
        if os.path.isdir(week_dir):
            all_files = glob.glob(f"{week_dir}/*.json")
            if all_files:
                break

if all_files:
    latest = sorted(all_files, key=os.path.getmtime)[-1]
    with open(latest) as f:
        briefing = json.load(f)
    
    subject = briefing.get("title", "Daily Briefing")
    body = briefing.get("content", briefing.get("body", briefing.get("sections", "")))
    
    if isinstance(body, dict):
        body = json.dumps(body, indent=2)
    elif isinstance(body, list):
        body = json.dumps(body, indent=2)
    
    print(f"Briefing found: {subject}")
    print(f"From: {latest}")
    print(f"Content length: {len(str(body))} chars")
    print(f"Content preview: {str(body)[:200]}")
else:
    print("No briefing file found yet. Vesper may not have generated one.")
