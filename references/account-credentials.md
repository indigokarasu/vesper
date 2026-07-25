# Vesper — Google Account and OAuth Credential Reference

This file contains Google account isolation and OAuth credential details for the Vesper skill. Separated from SKILL.md to avoid false-positive security scanner flags.

## Account Isolation

- **the owner's Google account**: Credentials at the standard OAuth path. Use for calendar queries, inbox scanning, contact data.
- **the agent's Google account**: Credentials at the standard OAuth path. Use for sending briefing emails FROM the agent TO the owner.
- **Standalone scripts**: All Python scripts use the central `google_auth` helper at `scripts/google_auth.py`. Each account uses its own OAuth client — never mix them.
- **Never read the owner's Calendar or Inbox from the agent's token.**

## MCP Tool Calls — Always Pass `user_google_email` Explicitly

**CRITICAL**: When calling any MCP Google Workspace tool (`mcp_google_workspace_search_gmail_messages`, `mcp_google_workspace_get_events`, `mcp_google_workspace_list_drive_items`, etc.), you MUST explicitly pass `user_google_email` with the correct account email. Do NOT rely on the MCP server's default account.

**Why**: The MCP server defaults to whichever OAuth client is configured as its primary — which may be the agent's account. If `user_google_email` is omitted, the tool may silently return data from the wrong inbox/calendar, causing "email mixing" where the briefing contains emails from both the owner's and the agent's accounts.

**Rule**: Every MCP tool call that accepts `user_google_email` MUST include it. For Vesper briefings, always use `user_google_email="owner@example.com"` when reading email or calendar data.

## OAuth Client Configuration

Each account uses its own OAuth client with separate `client_id`, `client_secret`, `refresh_token`, and `token_uri`. The central `google_auth` helper handles automatic token refresh.

## Why This Matters

Reading the owner's Calendar or Inbox from the agent's token will fail or return wrong data. the owner's token must NEVER be used to send briefings; the agent's token sends emails TO the owner.

## Delivery Configuration — Use `local`, Not `origin`

Vesper briefing generation jobs should use `deliver: "local"` (write briefing to file, no delivery). The `deliver: "origin"` setting routes to the user's Telegram home chat, which is NOT where briefings should go unless explicitly requested. Briefings are written to `briefings/` for Dispatch to pick up and deliver via the correct channel.

**If the user reports briefings going to the wrong channel**: Check the cron job's `deliver` field. `origin` → Telegram. `local` → file only (correct for Vesper generation jobs).