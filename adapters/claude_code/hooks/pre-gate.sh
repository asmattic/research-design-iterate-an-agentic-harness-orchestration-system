#!/usr/bin/env bash
# PreToolUse gate: human gate on irreversible Bash actions (PRD §12, §6.1).
# Exit 2 + stderr reason blocks the call; exit 0 lets it through.
set -euo pipefail

INPUT="$(cat)"
COMMAND="$(printf '%s' "$INPUT" | jq -r '.tool_input.command // empty')"
[ -z "$COMMAND" ] && exit 0

deny() {
  printf 'BLOCKED by harness pre-gate: %s. Route this through the human approval gate.\n' "$1" >&2
  exit 2
}

match() { printf '%s' "$COMMAND" | grep -qE "$1"; }

match 'git[[:space:]]+push[[:space:]]+.*--force' \
  && deny "force push rewrites remote history (git push --force)"
match 'git[[:space:]]+push([[:space:]]+[^-][^[:space:]]*)*[[:space:]]+-f([[:space:]]|$)' \
  && deny "force push rewrites remote history (git push -f)"
match 'rm[[:space:]]+-(rf|fr|r[[:space:]]+-f)[[:space:]]+(/|~)([[:space:]]*$|\*)' \
  && deny "recursive delete of filesystem root or home (rm -rf)"
match '(^|[;&|][[:space:]]*)sudo[[:space:]]' \
  && deny "privilege escalation (sudo)"
match '(cat|less|more|head|tail|cp|scp|base64)[[:space:]][^|;&]*(\.aws/credentials|\.netrc|\.ssh/id_[a-z0-9]+|/etc/shadow)' \
  && deny "credential-file read"
match '(mkfs(\.[a-z0-9]+)?[[:space:]]|dd[[:space:]]+[^;|&]*of=/dev/)' \
  && deny "raw device write (mkfs / dd)"

if match '>[[:space:]]*/dev/' && ! match '>[[:space:]]*/dev/(null|std(out|err)|tty|fd/)'; then
  deny "redirect into a device node (> /dev/...)"
fi

exit 0
