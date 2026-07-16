#!/usr/bin/env python3
"""
Vesper Briefing Quality Checker

Validates a briefing JSON file against the quality criteria defined in
SKILL.md run completion step 3. Outputs PASS/FAIL with specific issues.

Usage:
    python3 quality_check.py <path-to-briefing.json>

Exit codes:
    0 = PASS
    1 = FAIL (issues printed to stdout)
"""

import json
import re
import sys

_HELP_ARGS = {"--help", "-h"}
if set(sys.argv[1:]) & _HELP_ARGS:
    print((__doc__ or "").strip() or "Usage: python3 quality_check.py <path-to-briefing.json>")
    sys.exit(0)


def load_briefing(path):
    with open(path) as f:
        return json.load(f)


def check_terminology(content):
    """3a: No internal system terminology leaked through."""
    # Whole-word matching only — avoids false positives like "DB" in "Handbuilding"
    terms = [
        r'\bDB\b', r'\bAPI\b', r'\bMCP\b', r'\bOAuth\b', r'\bJSON\b',
        r'\bJSONL\b', r'\bREST\b', r'\bSQL\b', r'\bURL\b', r'\bURI\b',
        r'\bHTML\b', r'\bCSS\b', r'\bRPC\b', r'\bSDK\b',
        r'\bproposal_id\b', r'\bsignal_id\b', r'\bbriefing_id\b',
        r'\bthread_id\b', r'\bmessage_id\b', r'\bdelivery_status\b',
        r'\bdispatch\b', r'\bcustodian\b', r'\brally\b', r'\bsands\b',
        r'\bvesper\b', r'\bvibes\b', r'\bpraxis\b', r'\bsift\b',
        r'\bscout\b', r'\bhermes\b', r'\bcron\b', r'\bsubagent\b',
        r'\bintents\.jsonl\b', r'\bevidence\.jsonl\b', r'\bsignals_evaluated\.jsonl\b',
        r'\bhermes send\b', r'\bexecute_code\b',
    ]
    issues = []
    for term in terms:
        match = re.search(term, content)
        if match:
            # Get context: 20 chars before and after
            start = max(0, match.start() - 20)
            end = min(len(content), match.end() + 20)
            context = content[start:end].replace('\n', ' ')
            issues.append(f"  Term '{match.group()}' found: ...{context}...")
    return issues


def check_sections_have_content(briefing):
    """3b: All included sections have actual content."""
    issues = []
    for section in briefing.get('sections', []):
        items = section.get('content_items', [])
        # Support both 'summary' (VesperBriefingFile schema) and 'text' (legacy)
        has_text = any(
            item.get('summary', '').strip() or item.get('text', '').strip()
            for item in items
        )
        if not has_text:
            section_id = section.get('section_type', section.get('id', 'unknown'))
            issues.append(f"  Section '{section_id}' has no content")
    return issues


def check_greeting(briefing):
    """3c: Greeting matches time-of-day format."""
    content = briefing.get('content', '')
    greeting = content.split('\n')[0] if content else ''
    btype = briefing.get('type', '')
    
    if btype == 'morning' and not greeting.startswith('Good morning'):
        return [f"  Morning briefing greeting is '{greeting}', expected 'Good morning ...'"]
    if btype == 'evening' and not greeting.startswith('Good evening'):
        return [f"  Evening briefing greeting is '{greeting}', expected 'Good evening ...'"]
    if btype == 'manual' and not (greeting.startswith('Good morning') or greeting.startswith('Good evening')):
        return [f"  Manual briefing greeting is '{greeting}', expected 'Good morning/evening ...'"]
    return []


def check_signals_evaluated(briefing, signals_evaluated_path=None):
    """3d: signals_evaluated.jsonl was updated with consumed proposal IDs."""
    consumed = briefing.get('signals_consumed', [])
    if not consumed:
        return []  # No signals consumed is valid if there were none to consume
    
    if not signals_evaluated_path:
        return []  # Can't check without path
    
    try:
        with open(signals_evaluated_path) as f:
            lines = f.readlines()
        evaluated_ids = set()
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
                evaluated_ids.add(record.get('signal_id', ''))
            except json.JSONDecodeError:
                continue
        
        missing = [sid for sid in consumed if sid not in evaluated_ids]
        if missing:
            return [f"  Signals consumed but not in signals_evaluated.jsonl: {missing}"]
    except FileNotFoundError:
        return [f"  signals_evaluated.jsonl not found at {signals_evaluated_path}"]
    
    return []


def check_decisions_trace(briefing):
    """3e: Every decision item traces to a real upstream signal."""
    issues = []
    consumed = briefing.get('signals_consumed', [])
    for section in briefing.get('sections', []):
        section_type = section.get('section_type', section.get('id', ''))
        if section_type == 'decisions':
            for item in section.get('content_items', []):
                # Support both 'summary' (VesperBriefingFile schema) and 'text' (legacy)
                text = item.get('summary', '') or item.get('text', '')
                # Check if the decision references something from consumed signals
                # or mentions a known real signal name
                # Simple heuristic: check if any consumed signal_id keyword appears in text
                has_trace = False
                for sig_id in consumed:
                    # Extract meaningful parts from signal_id (e.g., "<vendor>-healthcare-it" from "<vendor>-healthcare-it-2026-06-24")
                    parts = sig_id.rsplit('-', 2)  # Remove date suffixes
                    keyword = parts[0] if len(parts) > 1 else sig_id
                    if keyword.lower() in text.lower():
                        has_trace = True
                        break
                # Also check for known real-source keywords
                real_sources = ['<vendor>', 'custodian', 'dispatch', 'rally', 'sands', 'wing', 'bywater', 'cigna']
                if any(src in text.lower() for src in real_sources):
                    has_trace = True
                
                if not has_trace:
                    issues.append(f"  Decision item doesn't trace to consumed signal: '{text[:80]}...'")
    return issues


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 quality_check.py <path-to-briefing.json> [path-to-signals-evaluated.jsonl]")
        sys.exit(1)
    
    briefing_path = sys.argv[1]
    signals_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        briefing = load_briefing(briefing_path)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"FAIL: Cannot load briefing file: {e}")
        sys.exit(1)
    
    content = briefing.get('content', '')
    
    all_issues = []
    
    # Run all checks
    all_issues.extend(check_terminology(content))
    all_issues.extend(check_sections_have_content(briefing))
    all_issues.extend(check_greeting(briefing))
    all_issues.extend(check_signals_evaluated(briefing, signals_path))
    all_issues.extend(check_decisions_trace(briefing))
    
    if all_issues:
        print("FAIL — Quality check issues found:")
        for issue in all_issues:
            print(issue)
        sys.exit(1)
    else:
        print("PASS — All quality checks passed.")
        sys.exit(0)


if __name__ == '__main__':
    main()
