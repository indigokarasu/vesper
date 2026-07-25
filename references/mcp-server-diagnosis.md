# MCP Server Diagnosis — Google Workspace

When the Google Workspace MCP server is unresponsive or its tools are absent from a session, use this guide to diagnose and handle the failure.

## Failure Mode Map

| Symptom | Root cause | Evidence |
|---|---|---|
| MCP tools timeout (120s+) but exist in toolset | `send_gmail_message` tool hangs (known bug since 2026-06-05) | Tools appear but hang on call |
| MCP tools exist but return auth error | OAuth token expired | Error contains `invalid_grant` or `token expired` |
| `Email ✓ configured` in `hermes status` but no MCP process | MCP process killed/crashed | `ps aux | grep workspace-mcp` returns nothing |
| `Email ✗ not configured` in `hermes status` | MCP not discovered at startup | No MCP tools in toolset, `ps aux` shows no process |
| `workspace-mcp` binary calls `python -m main` but module missing | Server-side package not installed | `python -m main` → `ModuleNotFoundError: No module named main` |
| `mcp` Python SDK not installed | Hermes skipped MCP discovery | `python -c "import mcp"` → `ModuleNotFoundError` |

## Binary Chain Diagnosis

The MCP server wrapper chain:

```
config.yaml → command: workspace-mcp-fixed
  → /usr/local/bin/workspace-mcp-fixed
    → exec /usr/local/bin/workspace-mcp "$@"
      → /usr/local/bin/workspace-mcp
        → exec <hermes-venv>/bin/python -m main "$@"
```

**To diagnose:**
```bash
# 1. Check if the MCP process is running
ps aux | grep workspace-mcp | grep -v grep

# 2. Check the wrapper chain
cat /usr/local/bin/workspace-mcp-fixed
cat /usr/local/bin/workspace-mcp

# 3. Check if the entrypoint module exists
<hermes-venv>/bin/python -c "import main"  # Should succeed if installed

# 4. Check if the mcp SDK is installed
<hermes-venv>/bin/python -c "import mcp; print('OK')"
```

## Handling in Cron Sessions

When running as a cron job and MCP is unavailable:

1. **Set failure status** on both the individual briefing file AND `briefings.jsonl`:
   ```python
   status = {"status": "failed", "failed_at": <ISO timestamp>, "reason": "MCP server not running in cron session — <specific error>"}
   ```

2. **Do NOT retry in a loop** — the MCP process won't recover within a cron run.

3. **Do NOT use `googleapiclient` directly** — that's the old broken `briefing_deliver.py` path.

4. **Preserve content** — the briefing content remains in `briefings/YYYY-WXX/YYYY-MM-DD-{type}.json` for the next delivery attempt.

5. **Report content in response** — include the briefing text in the final response so the user receives it even without email delivery.

6. **Write journal** — record the delivery attempt and blocker in the vesper journal.

## Known Bugs

- **`send_gmail_message` timeout (since 2026-06-05):** The send tool hangs for 120s+ even on short messages. Workaround: use `draft_gmail_message` instead. Does NOT help in cron mode when the MCP process itself is dead.

- **Binary entrypoint broken:** The `workspace-mcp` script calls `python -m main` but the containing package may not be installed. No automated fix — the package must be reinstalled in the gatewayvenv.