#!/bin/bash
# SessionStart hook for Claude Code on the web.
# Starts MySQL provisioned by .claude/cloud-setup.sh (running processes are not
# kept in the environment snapshot) and exports the dev/test environment.
if [ "$CLAUDE_CODE_REMOTE" != "true" ] || ! command -v feder-env >/dev/null; then
  exit 0
fi
cd "$CLAUDE_PROJECT_DIR" || exit 0

ENV_LINES=$(feder-env) || { echo "feder: MySQL failed to start" >&2; exit 0; }
[ -n "$CLAUDE_ENV_FILE" ] && echo "$ENV_LINES" >> "$CLAUDE_ENV_FILE"

[ -d /opt/feder-e2e/node_modules ] && [ ! -e tests/node_modules ] \
  && ln -s /opt/feder-e2e/node_modules tests/node_modules
exit 0
