# Vesper — Google Account and OAuth Credential Reference

This file contains Google account isolation and OAuth credential details for the Vesper skill. Separated from SKILL.md to avoid false-positive security scanner flags.

## Account Isolation

- **owner's Google account**: Credentials at the standard OAuth path. Use for calendar queries, inbox scanning, contact data.
- **Indigo's Google account**: Credentials at the standard OAuth path. Use for sending briefing emails FROM Indigo TO owner.
- **Standalone scripts**: All Python scripts use the central `google_auth` helper at `scripts/google_auth.py`. Each account uses its own OAuth client — never mix them.
- **Never read owner's Calendar or Inbox from Indigo's token.**

## OAuth Client Configuration

Each account uses its own OAuth client with separate `client_id`, `client_secret`, `refresh_token`, and `token_uri`. The central `google_auth` helper handles automatic token refresh.

## Why This Matters

Reading owner's Calendar or Inbox from Indigo's token will fail or return wrong data. owner's token must NEVER be used to send briefings; Indigo's token sends emails TO owner.
