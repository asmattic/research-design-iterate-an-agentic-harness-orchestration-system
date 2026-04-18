# 16 · Adapters — Claude Code, Codex CLI, Cursor

## The principle

The architecture (§§05–13) and the protocol (§15) are runtime-agnostic. This chapter specifies how the protocol maps to runtime primitives for three current runtimes. Each adapter is a thin layer — roughly 10% of total code surface — that translates protocol schemas into runtime idioms and back.

## 16.1 Mapping overview

| Protocol concept | Claude Code | Codex CLI | Cursor |
|---|---|---|---|
| Primary orchestrator | Root session + `CLAUDE.md` | Root session + `AGENTS.md` | Composer + project rules |
| Cohort sub-orchestrator | Subagent (invoked via Task tool) | Subagent (invoked via `codex` handoff) | Custom role via rules file |
| Expert agent | Subagent with focused system prompt | Subagent | Role-prompted chat with rules |
| Expert swarm | Parallel Task tool calls + aggregator | Parallel `codex exec` + aggregator | Parallel composer windows + aggregator (custom) |
| Deterministic verifier | MCP tool + hooks | Codex exec shell tool | Cursor bash/terminal tool |
| Memory L2 | Skills + filesystem | `AGENTS.md` + filesystem | `.cursor/rules` + filesystem |
| Event log L3 | Filesystem (JSONL) | Filesystem (JSONL) | Filesystem (JSONL) |
| Guardrails | Hooks (PreToolUse, PostToolUse) | Codex middleware | Cursor rules + custom hooks |
| Drift detector | Background skill + hooks | Background subprocess | Background subprocess |
| Human approval gate | Hooks + permission prompts | Hooks | Composer confirmation prompts |

## 16.2 Claude Code adapter

**Claim.** Claude Code is the most complete runtime for this architecture as of April 2026 — its Skills, subagents, MCP, and hooks map nearly one-to-one to the protocol's concepts.

**Component mapping.**

- **Primary orchestrator** — the root Claude Code session, with `CLAUDE.md` that loads INTENT and links to `ORCHESTRATOR.md`.
- **Orchestrator System** — runs as a set of Skills (`bs-detector`, `validator`, `signal-attributor`, `drift-detector`) invoked via the root session's Task tool or via hooks.
- **Cohort sub-orchestrators** — subagents (`~/.claude/agents/*.md`), one per cohort. Each cohort subagent has its own system prompt and its own tool allowlist.
- **Expert agents** — subagents under the cohort, invoked via nested Task calls.
- **Swarms** — the cohort subagent uses parallel Task tool calls to spawn N experts and aggregates.
- **Deterministic verifier** — exposed as MCP tools (Python processes) so Claude Code can call them directly.
- **Memory L2** — Skills folder pattern (`~/.claude/skills/<name>/SKILL.md`) plus a `memory/` directory in the project.
- **Event log** — written by a PostToolUse hook to a JSONL file.
- **Guardrails** — PreToolUse hooks reject disallowed tool calls; PostToolUse hooks scan outputs for PII and constitutional violations.
- **Drift detector** — a background process + a PostToolUse hook that writes drift scores to the event log.
- **Human approval gate** — Claude Code's permission prompts serve as the user-facing gate; hooks confirm "did approval actually arrive" before letting irreversible tool calls through.

**Implementation notes.**
- Install the harness as a **plugin** (`.plugin` bundle) that registers skills, subagents, hooks, and MCPs.
- The plugin's `AGENTS.md` provides a roster and links into `COHORT.md` files per cohort.
- Round 2 ships a reference implementation of this adapter; the other two adapters are implemented by analogy.

## 16.3 Codex CLI adapter

**Claim.** Codex CLI is strong on controlled shell execution and multi-session handoff. Its weakness relative to Claude Code is the lack of first-class Skills; the adapter uses `AGENTS.md` and sub-session handoffs to compensate.

**Component mapping.**

- **Primary orchestrator** — root `codex` session with `AGENTS.md` loading INTENT and the orchestrator prompt.
- **Orchestrator System** — a Python package (`harness-os`) invoked via `codex exec` or as MCP tools.
- **Cohort sub-orchestrators** — spawned with `codex -s <cohort-session>` and provided their own `AGENTS.md` stub.
- **Expert agents** — either further sub-sessions or LLM API calls from a cohort's Python code. Codex CLI is less opinionated about sub-agents than Claude Code, so the adapter is more code-heavy here.
- **Swarms** — Python orchestrator code calls the LLM API N times in parallel, aggregates.
- **Deterministic verifier** — plain shell / Python scripts called via `codex exec`.
- **Memory** — filesystem (same as Claude Code adapter); Codex's `AGENTS.md` loading pattern is used for the memory index.
- **Event log** — Python logger writing JSONL.
- **Guardrails** — Codex middleware layer (there is a hook analogue) plus an LLM-judge pass.
- **Drift detector** — Python subprocess polling the state.
- **Human approval gate** — Codex's permission confirmation prompts.

**Implementation notes.**
- Codex's sandbox / permission model is a benefit here: irreversible actions already pass through a permission check.
- The adapter assumes Codex's `exec` tool can run arbitrary shells; if the user has tightened this, the harness shell calls must be allowlisted.

## 16.4 Cursor adapter

**Claim.** Cursor is primarily a code editor with an agent mode; its strength is the in-IDE context, its weakness (for this harness) is the lack of subagent primitives. The adapter emulates orchestration by leaning on `.cursor/rules` and parallel Composer windows.

**Component mapping.**

- **Primary orchestrator** — Cursor Composer session with `.cursor/rules` loading INTENT.
- **Orchestrator System** — external Python process; Cursor Composer calls it via the Cursor shell tool.
- **Cohort sub-orchestrators** — either (a) separate Composer windows each with a cohort-scoped rules file, or (b) external Python processes. In practice (a) is ergonomic for interactive sessions; (b) is necessary for unattended runs.
- **Expert agents** — inside a cohort's Python, or as further sub-Composer sessions.
- **Swarms** — Python multi-call + aggregator.
- **Deterministic verifier** — Python, same as other adapters.
- **Memory** — filesystem + `.cursor/rules`.
- **Event log** — Python logger writing JSONL.
- **Guardrails** — `.cursor/rules` entries + external Python guardrail module.
- **Drift detector** — external Python.
- **Human approval gate** — Cursor Composer confirmation prompts plus explicit "waiting for user" states surfaced by the Python orchestrator.

**Implementation notes.**
- Cursor's agent-mode is evolving; the adapter is more reliant on external Python and less on runtime primitives. As Cursor adds subagent support, the adapter migrates back toward parity with Claude Code.
- For headless / CI use, Cursor is the weakest adapter; Claude Code or Codex are preferred for unattended runs.

## 16.5 Adapter interface — Python sketch

```python
class HarnessAdapter(Protocol):
    name: str                          # "claude_code", "codex_cli", "cursor"
    protocol_version: str              # e.g., "0.1.0"

    def load_intent(self, path: Path) -> Intent: ...

    def spawn_cohort(self, cohort: CohortSpec, intent: Intent) -> CohortHandle: ...
    def spawn_expert(self, cohort: CohortHandle, agent_contract: AgentContract) -> ExpertHandle: ...
    def emit(self, expert: ExpertHandle, prompt: str, input: dict) -> AgentEmission: ...

    def run_verifier(self, claim: TestableClaim) -> VerifierResult: ...
    def write_event(self, envelope: EventEnvelope) -> None: ...
    def read_events(self, campaign_id: str, filter: dict) -> Iterator[EventEnvelope]: ...
    def request_human_approval(self, action: Action) -> ApprovalDecision: ...
    def drift_check(self, state: OrchestratorState) -> DriftResult: ...
    def memory_load(self, query: MemoryQuery) -> list[MemoryEntry]: ...
    def memory_write(self, entry: MemoryEntry) -> None: ...
```

Adapter implementations live under `adapters/<name>/` in the reference scaffolding and are plug-swappable.

## 16.6 Conformance

§15.11 specifies conformance tests. Every adapter must pass before being accepted into the reference set. The tests are:
- Round-trip every schema.
- Replay a recorded event log and produce identical derived state.
- Run the "golden task" (a small rental-underwriting scenario) and match expected output within declared tolerances.

## 16.7 Choosing an adapter per campaign

A given campaign runs on one adapter at a time. Choice drivers:

- **Claude Code** — interactive, IDE-light, Skills ecosystem, best subagent ergonomics.
- **Codex CLI** — unattended / CI runs, strong shell control, terminal-native.
- **Cursor** — IDE-heavy code campaigns, strong in-editor context.

The harness's runtime is not locked; a campaign can be ported between adapters (same INTENT, same cohorts, different runtime). The event log format is adapter-agnostic, so retrospectives read across adapters.

## 16.8 Future adapters (not shipping in Round 1/2)

- LangGraph / AutoGen / CrewAI Python-native adapter — for teams running their own Python orchestration.
- Cline / Windsurf / other emerging agent IDEs.
- A "null adapter" that runs pure Python with direct LLM API calls, used primarily for eval harness runs.

The protocol is designed so each of these is ≤ ~800 lines of code plus a conformance-test pass.

## Diagram reference

- Mermaid not assigned specifically to this chapter; the adapter layer appears as the bottom of **D01 (System Layers)** and in **D03 (Hub topology)**.

## One-line summary

> Three adapters today (Claude Code, Codex CLI, Cursor); one protocol, one interface, thin translation. Claude Code is the reference implementation because its subagent + Skills + hooks stack maps most cleanly. Adapters pass conformance tests or don't ship.
