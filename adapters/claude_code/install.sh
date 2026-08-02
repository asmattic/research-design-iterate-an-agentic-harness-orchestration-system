#!/usr/bin/env bash
# Install the harness-orchestrator Claude Code adapter.
# Default is a DRY RUN: prints what it would do. Pass --link to actually
# pip-install the packages and link skills/agents into ~/.claude/.
set -euo pipefail

ADAPTER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${ADAPTER_DIR}/../.." && pwd)"
MODE="dry-run"
[ "${1:-}" = "--link" ] && MODE="link"

if ! command -v python3 >/dev/null 2>&1; then
  echo "error: python3 not found" >&2
  exit 1
fi
if ! python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)'; then
  echo "error: python >= 3.10 required (found $(python3 --version))" >&2
  exit 1
fi

PKGS=(
  "packages/harness-protocol-py"
  "packages/harness-reference"
  "packages/harness-os"
  "packages/harness-verifier[mcp]"
  "packages/harness-evals"
)

run() {
  if [ "$MODE" = "link" ]; then
    echo "+ $*"
    "$@"
  else
    echo "[dry-run] $*"
  fi
}

echo "== harness-orchestrator adapter install ($MODE) =="
echo "repo root: $REPO_ROOT"

for pkg in "${PKGS[@]}"; do
  run python3 -m pip install --quiet -e "${REPO_ROOT}/${pkg}"
done

SKILLS_DEST="${HOME}/.claude/skills"
AGENTS_DEST="${HOME}/.claude/agents"
run mkdir -p "$SKILLS_DEST" "$AGENTS_DEST"

for skill in "${ADAPTER_DIR}"/skills/*/; do
  name="$(basename "$skill")"
  run ln -sfn "${skill%/}" "${SKILLS_DEST}/${name}"
done

for agent in "${ADAPTER_DIR}"/agents/*.md; do
  run ln -sfn "$agent" "${AGENTS_DEST}/$(basename "$agent")"
done

echo
echo "Next steps:"
echo "  1. Re-run with --link to apply (default made no changes)." \
     "The link step is idempotent."
echo "  2. Register the verifier MCP server (needs harness-verifier[mcp]):"
echo "       claude mcp add harness-verifier -- harness-verify-mcp"
echo "     (config also in ${ADAPTER_DIR}/mcp/mcp-servers.json)"
echo "  3. Wire hooks: merge ${ADAPTER_DIR}/hooks/hooks.json into your"
echo "     settings, with CLAUDE_PLUGIN_ROOT=${ADAPTER_DIR}."
echo "  4. Smoke test: pytest ${ADAPTER_DIR}/tests -q"
