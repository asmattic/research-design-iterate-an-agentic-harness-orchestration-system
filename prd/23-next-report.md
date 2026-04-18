# 23 · Next Report — Round 2 Specification

## Purpose of this chapter

Define the exact deliverables of the next report (Round 2) so that (a) progress is unambiguous, (b) scope is disciplined, and (c) the deliverables include the **reference scaffolding and eval harness prototype** the principal explicitly called out as required next-step outputs.

## 23.1 The Round 2 artifact set

Everything below is in scope. Nothing else is.

### 23.1.1 Protocol schemas, finalized
- Versioned JSON-Schema documents for all five schemas:
  - `agent-contract.schema.json`
  - `event-envelope.schema.json`
  - `consensus-packet.schema.json`
  - `orchestrator-state.schema.json`
  - `memory-index.schema.json`
- Version `0.2.0`.
- Published as a Python package `harness-protocol` plus a Node/TypeScript package `@harness/protocol` for adapter convenience.
- Schema conformance tests runnable in CI.

### 23.1.2 Reference scaffolding
Delivered as a public repository, `harness-reference/`:

**Template files:**
- `INTENT.md` — generalized from the rental toolkit's template.
- `ORCHESTRATOR.md` — primary orchestrator system prompt.
- `AGENTS.md` — roster + pointer list.
- `COHORT.md` — per-cohort system prompt template.
- `SWARM.md` — swarm composition + aggregator rules template.
- `CONSTITUTION.md` — constitutional rules template (with a starting set).
- `HANDOFF.md` — session-to-session continuity template.

**Executable code:**
- `drift_check.py` — generalized drift detector with both quantitative and qualitative signals; library-importable and CLI-runnable.
- `retrospective.py` — post-campaign analyzer that produces proposal diffs.
- `consensus.py` — the aggregator with confidence intervals and three-valued outcome.
- `memory_index.py` — the memory index reader/writer, SQLite-backed.
- `event_log.py` — JSONL event-log writer/reader with replay support.

All executables are ≤ 500 lines each, documented, typed, and unit-tested against the protocol.

### 23.1.3 Orchestrator System — Python package
`harness-os/` implementing §6.4's six sub-responsibilities:

- `context_manager.py` — memory load + summarization + budget enforcement.
- `bs_detector.py` — LLM-judge with a rubric file; deterministic precedence where possible.
- `validator.py` — bridge to the deterministic verifier (which lives in `harness-verifier/`).
- `signal_noise.py` — weighting module.
- `weight_tweaker.py` — per-task + per-campaign update.
- `drift_detector.py` — the continuous drift composite.

Each module has:
- A clear input/output contract (typed).
- Unit tests.
- Prompts in `prompts/` with versioning.
- Integration test against a recorded campaign log.

### 23.1.4 Deterministic verifier — Python package
`harness-verifier/`:

- Core: a runner that loads a claim + a test spec and returns pass/fail/abstain + evidence.
- Built-in verifiers:
  - `code_test_runner` (pytest/vitest).
  - `schema_validator` (JSON-Schema).
  - `citation_resolver` (URL/DOI check, quote match).
  - `numeric_bound` (range check).
  - `type_check` (ts/mypy).
- Extension point for domain-specific verifiers (e.g., rental-toolkit's `hcpa_lookup`, `mortgage_amortizer`).
- MCP server wrapper so Claude Code can call verifiers as tools.

### 23.1.5 Eval harness prototype
`evals/`:

**Runner CLI:**
```
harness eval run --benchmark <name> --config <path> --output <dir>
```

**Benchmarks (starting set):**
- Rental 20-scenario synthetic set (ground-truth outcomes).
- Protocol conformance benchmark (adapter-focused).
- Adversarial safety set (prompt-injection + drift-induction payloads).

**Scorers:**
- Calibration (Brier + ECE).
- Drift (§11 composite).
- Completion (rubric-based judge).
- Cost (token + USD aggregator).
- Safety (false-allow rate on adversarial set).

**Regression gate:**
- A CI-integrable command that returns non-zero if any proposed config change regresses safety, completion, or intent-alignment beyond threshold.

**Report generator:**
- Produces `report.md` in the format from §14.8.

### 23.1.6 Claude Code adapter (reference implementation)
`adapters/claude_code/`:

- Package + `.plugin` bundle.
- **Skills**:
  - `bs-detector`
  - `validator`
  - `drift-detector`
  - `signal-attributor`
  - `retrospective`
  - `orchestrator-plan`
- **Subagents**:
  - `primary-orchestrator`
  - `finance-cohort`, `legal-cohort`, `research-cohort`
  - Representative experts per cohort (5 total).
- **Hooks**:
  - PreToolUse: guardrail checks, approval gating.
  - PostToolUse: event log append, drift check, BS detector.
- **MCPs**:
  - `harness-verifier`
- Install script and quickstart docs.
- Conformance test pass.
- One recorded demo campaign.

### 23.1.7 Rental toolkit port (partial)
- Port cohorts: finance + legal on Round 2; others in Round 3.
- Migration script for legacy rental-toolkit event logs → new protocol.
- One end-to-end test campaign (a held-out property) runs on the harness.

### 23.1.8 Documentation updates
- Next.js docs site gains a Round 2 section.
- Adapter install/quickstart for Claude Code.
- Example campaign walkthrough (a rental underwriting minireplay).
- Protocol schema reference auto-generated from schemas.
- Developer guide: "how to add a new cohort", "how to add a new verifier", "how to add a new adapter".

## 23.2 Acceptance criteria for Round 2

Round 2 is accepted when:
1. All schemas validate against their conformance suite.
2. Reference scaffolding repo clones, installs, and passes its own tests.
3. Claude Code adapter passes conformance.
4. Eval harness runs the synthetic rental benchmark end-to-end and produces a report.
5. Rental toolkit's finance + legal cohorts run on the harness and complete a test campaign.
6. Drift detector triggers correctly in an intentionally-induced drift test.
7. Human approval gate engages on all irreversible actions in the test campaign.
8. Documentation site deploys with the Round 2 content.

## 23.3 Explicit out-of-scope for Round 2
- Codex CLI adapter.
- Cursor adapter.
- Full SWE-bench / GAIA / BrowseComp integrations (Round 3).
- Multi-adapter parity tests (Round 3).
- Production compliance packaging (Round 5+).

## 23.4 Dependencies to clarify before Round 2 starts
1. **Model-access agreements.** Which API keys / quotas are available.
2. **Deployment target.** Where do artifacts live — team GitHub? Private registry?
3. **Legacy rental-toolkit access.** Need the event log artifacts from existing campaigns for migration testing.
4. **Security review.** Constitutional rules for the target deployment (PII handling, financial data).

## 23.5 Round 2 resource estimate
- **Team:** 1 tech lead + 2 engineers + 1 ML/eval engineer + 1 tech writer.
- **Duration:** 3–5 weeks once dependencies clear.
- **Cost:** model spend for benchmark runs; adapter infra; CI resources. Rough budget: $5K–$15K in API cost across all testing.

## 23.6 Questions for Round 2 kickoff
- Do we build the Orchestrator System's context manager to use vector embeddings from day 1, or defer to lexical summarization for Round 2?
- Do we ship retrospective proposals as PR diffs against a central config repo, or as local files per campaign?
- What's the target benchmark corpus size for the synthetic rental set (20 scenarios is the plan — should we scale to 50)?

## 23.7 The handoff

This PRD's Round 1 handoff to whoever executes Round 2 includes:
- This repo (PRD + diagrams + appendices + docs site).
- A ratified `INTENT.md` for Round 2 itself.
- A kickoff meeting to resolve §23.6 questions.

Round 2 begins with writing Round 2's own INTENT.md; the harness is its own first customer.

## One-line summary

> Round 2 ships finalized protocol schemas, reference scaffolding (templates + drift-check + retrospective + consensus + memory index), the Orchestrator System Python package, a deterministic verifier, an eval-harness prototype, the Claude Code adapter, a partial rental-toolkit port, and updated docs — behind a clear set of acceptance gates.
