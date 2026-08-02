#!/usr/bin/env bash
# PostToolUse bridge: append one event-envelope line to the L3 event log
# (PRD §10, §16.2). Log path: $HARNESS_EVENT_LOG or .harness/events.jsonl.
set -euo pipefail

INPUT="$(cat)"
LOG="${HARNESS_EVENT_LOG:-.harness/events.jsonl}"
mkdir -p "$(dirname "$LOG")"

TOOL="$(printf '%s' "$INPUT" | jq -r '.tool_name // "unknown"')"
if command -v uuidgen >/dev/null 2>&1; then
  EVENT_ID="evt_$(uuidgen | tr '[:upper:]' '[:lower:]')"
else
  EVENT_ID="evt_$(date -u +%s)_$$"
fi
T="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

jq -cn \
  --arg event_id "$EVENT_ID" \
  --arg campaign_id "${HARNESS_CAMPAIGN_ID:-camp_adapter_local}" \
  --arg t "$T" \
  --arg tool "$TOOL" \
  '{
    event_id: $event_id,
    campaign_id: $campaign_id,
    t: $t,
    emitter: {kind: "orchestrator", id: "claude_code_session", adapter: "claude_code"},
    kind: "tool_result",
    payload: {tool_name: $tool}
  }' >> "$LOG"

exit 0
