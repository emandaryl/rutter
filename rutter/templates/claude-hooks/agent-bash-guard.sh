#!/bin/sh
# rutter-managed: copied verbatim by Rutter to .claude/hooks/agent-bash-guard.sh.
# Do not hand-edit; re-run Rutter to update. Wrapper for agent-bash-guard.py (same folder).
# Fails closed: a missing python3 or guard file blocks the call (exit 2), because Claude Code
# treats any other non-zero exit from a hook as a non-blocking error.
command -v python3 >/dev/null 2>&1 || {
  echo "agent-bash-guard: python3 is required, so Bash is blocked for this agent" >&2
  exit 2
}
GUARD="$(dirname "$0")/agent-bash-guard.py"
[ -f "$GUARD" ] || {
  echo "agent-bash-guard: $GUARD is missing, so Bash is blocked for this agent" >&2
  exit 2
}
exec python3 "$GUARD" "$@"
