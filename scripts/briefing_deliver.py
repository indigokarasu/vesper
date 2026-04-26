#!/usr/bin/env python3
"""
Dispatch Briefing Delivery Script
Reads undelivered Vesper briefings and emails them via Indigo's Gmail.
"""
import json
import os
import base64
from datetime import datetime
from email.mime.text import MIMEText
from pathlib import Path

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

HERMES_ROOT = Path(os.environ.get('HERMES_HOME', '/root/.hermes'))
VESPER_BRIEFINGS = HERMES_ROOT / 'commons/data/ocas-vesper/briefings'
TOKEN_PATH = '/root/.hermes/indigo_google_credentials.json'
RECIPIENT = 'jared.zimmerman@gmail.com'

def get_gmail_service():
    with open(TOKEN_PATH) as f:
        token_data = json.load(f)
    creds = Credentials.from_authorized_user_info(token_data)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_PATH, 'w') as f:
            json.dump(json.loads(creds.to_json()), f)
    return build('gmail', 'v1', credentials=creds)

def send_email(service, to, subject, html_body, text_body):
    message = MIMEText(html_body, 'html')
    message['to'] = to
    message['from'] = 'mx.indigo.karasu@gmail.com'
    message['subject'] = subject
    
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return service.users().messages().send(
        userId='me',
        body={'raw': raw}
    ).execute()

def find_latest_briefing():
    """Find the most recent undelivered briefing."""
    latest = None
    latest_time = None
    
    for week_dir in VESPER_BRIEFINGS.iterdir():
        if not week_dir.is_dir():
            continue
        for f in week_dir.glob('*.json'):
            try:
                with open(f) as fh:
                    d = json.load(fh)
                status = d.get('delivery_status', None)
                # Skip if already delivered
                if status == 'delivered':
                    continue
                generated = d.get('generated_at', '')
                briefing_type = d.get('type', 'unknown')
                date = d.get('date', '')
                subject = f"Evening Briefing — {date}" if briefing_type == 'evening' else f"Morning Briefing — {date}"
                
                if latest_time is None or generated > latest_time:
                    latest_time = generated
                    latest = (f, d, subject)
            except Exception as e:
                print(f"Error reading {f}: {e}", file=__import__('sys').stderr)
                continue
    
    return latest

def main():
    print(f"Checking for briefings in {VESPER_BRIEFINGS}")
    
    result = find_latest_briefing()
    if not result:
        print("No undelivered briefings found.")
        return
    
    briefing_file, briefing_data, subject = result
    print(f"Found briefing: {subject}")
    
    # Use HTML content if available, with fallbacks
    html_body = briefing_data.get('html_content') or briefing_data.get('rendered_html', '')
    # Try multiple fields for text content
    text_body = briefing_data.get('content') or briefing_data.get('briefing_text', '')
    
    if not html_body and text_body:
        # Convert plain text to basic HTML
        import re
        escaped = text_body.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        html_body = escaped.replace('\n\n', '</p><p>').replace('\n', '<br>')
        html_body = f'<p>{html_body}</p>'
    
    if not html_body:
        print("No HTML content in briefing, skipping.")
        return
    
    try:
        service = get_gmail_service()
        print(f"Sending to {RECIPIENT}...")
        sent = send_email(service, RECIPIENT, subject, html_body, text_body)
        print(f"Sent: {sent['id']}")
        
        # Mark as delivered
        briefing_data['delivery_status'] = 'delivered'
        briefing_data['delivered_at'] = datetime.utcnow().isoformat() + 'Z'
        with open(briefing_file, 'w') as f:
            json.dump(briefing_data, f, indent=2)
        print(f"Marked {briefing_file.name} as delivered.")
        
    except Exception as e:
        print(f"Failed to send: {e}", file=__import__('sys').stderr)
        # Don't raise - allow cron job to complete successfully
        # The briefing will remain pending for next attempt
        return

if __name__ == '__main__':
    main()
