#!/bin/bash
# entrypoint.sh: Runs before each agent session.
# - Copies host Claude credentials (mounted read-only) to a writable home location
# - Pre-trusts /workspace so Claude doesn't prompt on startup
set -e

# ── Copy host Claude credentials to writable home ─────────────────────────────
# ~/.claude is mounted read-only at /tmp/claude-host so we can copy it here
# and still have a writable config directory for the session.
if [[ -d /tmp/claude-host ]]; then
    mkdir -p "$HOME/.claude"
    cp -r /tmp/claude-host/. "$HOME/.claude/"
fi

if [[ -f /tmp/claude-host.json ]]; then
    cp /tmp/claude-host.json "$HOME/.claude.json"
fi

# ── Pre-trust /workspace ──────────────────────────────────────────────────────
SETTINGS="$HOME/.claude/settings.json"
if [[ -f "$SETTINGS" ]]; then
    updated=$(jq 'if .trustedDirectories then .trustedDirectories += ["/workspace"] | .trustedDirectories |= unique
                  else . + {"trustedDirectories": ["/workspace"]} end' "$SETTINGS")
    echo "$updated" > "$SETTINGS"
else
    mkdir -p "$(dirname "$SETTINGS")"
    echo '{"trustedDirectories":["/workspace"]}' > "$SETTINGS"
fi

exec "$@"
