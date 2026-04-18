# 21 · Phased Roadmap

## The three rounds

Delivery is phased to match risk and feedback. Each round ends with a concrete artifact set and a decision gate.

| Round | Scope | Duration | Artifact | Gate |
|---|---|---|---|---|
| **1 — Design** | This PRD | Done on completion | PRD + diagrams + bibliography + schema skeleton | Human approval to proceed to Round 2 |
| **2 — Scaffold & reference adapter** | Protocol + Claude Code adapter + eval harness prototype | ~3–5 weeks | Runnable scaffolding; one adapter passes conformance | One real campaign runs end-to-end on Claude Code adapter |
| **3 — Production + multi-adapter** | Codex and Cursor adapters + full eval suite + rental toolkit port | ~6–10 weeks | Three-adapter parity; rental toolkit re-implemented on harness; Round 3 benchmark pass | Metrics match or beat §02 targets on held-out benchmark |

## Round 1 — delivered (this PRD)

- **§00–23** full PRD (this repo).
- **11 Mermaid diagrams** in `/diagrams/`.
- **JSON-Schema skeleton** for all 5 protocol schemas in `/prd/appendices/D-schemas.md`.
- **Annotated bibliography** (~15 sources) in `/prd/appendices/C-bibliography.md`.
- **Next.js 16 docs site** rendering this PRD with MDX, Anthropic branding, embedded Mermaid.
- **Three worked examples** (rental, code architecture, AI research).
- **Proposed skills spec** for Round 2 `skill-creator` runs in `/prd/appendices/E-proposed-skills.md`.

**Exit gate:** Human review of PRD. Ratification of INTENT/goals/non-goals. Identification of any content this Round 1 missed.

## Round 2 — reference scaffolding + Claude Code adapter + eval harness

### 2.1 Protocol finalization
- Versioned JSON-Schema for Agent Contract, Event Envelope, Consensus Packet, Orchestrator State, Memory Index (v0.2.0).
- Schema validator Python package (`harness-protocol`) — used by all adapters.
- Schema conformance test suite.

### 2.2 Reference scaffolding
Published as a repo with plug-and-play files:
- `INTENT.md` template (generalized from the rental toolkit).
- `ORCHESTRATOR.md` template (primary orchestrator system prompt).
- `AGENTS.md` template (roster + pointer files).
- `COHORT.md` template (one per cohort).
- `SWARM.md` template (swarm composition + aggregator rules).
- `drift_check.py` — generalized from the rental toolkit's implementation, now library-importable.

### 2.3 Orchestrator System Python package
- `harness-os/` with:
  - `bs_detector.py` (LLM-judge based with rubric).
  - `validator.py` (bridge to deterministic verifier).
  - `signal_noise.py` (weighting module).
  - `weight_tweaker.py` (per-task + per-campaign updates).
  - `drift_detector.py` (embedding + LLM-judge composite).
  - `context_manager.py` (memory load, summarization, budget enforcement).

### 2.4 Eval harness prototype
- `evals/` package.
- Runner: `harness eval run --benchmark <name> --config <path>`.
- Benchmark loader (starts with a synthetic 20-task rental set).
- Calibration scorer (Brier + ECE).
- Drift scorer (per §11).
- Regression gate for proposed config changes.
- `report.md` generator.

### 2.5 Claude Code adapter
- `adapters/claude_code/` — Python package + a `.plugin` bundle.
- Skills: `bs-detector`, `validator`, `drift-detector`, `signal-attributor`, `retrospective`.
- Subagents: `orchestrator`, `finance-cohort`, `legal-cohort`, `research-cohort` (generic templates) + example experts per cohort.
- Hooks: PreToolUse (guardrail checks, approval gating), PostToolUse (event log write, drift check).
- MCPs: `harness-verifier` (Python) wrapping verifier tools.
- Conformance tests pass.

### 2.6 Rental toolkit port (partial)
- Rental toolkit's cohorts ported as concrete instances on the new scaffolding.
- At least the finance and legal cohorts runnable end-to-end.
- Event log backward-compat: ingest legacy rental-toolkit logs into the new event log format for retrospective continuity.

### 2.7 Documentation
- Update the Next.js docs site with a "Round 2 reference" section.
- Adapter-specific install/quickstart for Claude Code.
- Example campaign walkthrough (rental underwriting minireplay).

**Exit gate:** Run one real rental-underwriting campaign on the Round 2 scaffolding. Report: completion, drift, calibration, cost, human gates. Compare to baseline (existing rental toolkit).

## Round 3 — multi-adapter, production, benchmarked

### 3.1 Codex CLI adapter
- `adapters/codex_cli/` — Python package.
- Pattern mapping per §16.3.
- Conformance tests pass.

### 3.2 Cursor adapter
- `adapters/cursor/` — Python package + `.cursor/rules` templates.
- Pattern mapping per §16.4.
- Conformance tests pass.

### 3.3 Full eval suite
- Rental: 20-scenario held-out set with ground truth.
- Code architecture: SWE-bench Verified subset integration.
- AI research: GAIA + BrowseComp subset integration.
- Adversarial safety: prompt-injection + drift-induction payload set.
- Calibration: Brier/ECE across all testable claims.

### 3.4 Complete rental toolkit port
- All cohorts (research, finance, legal, physical, ops) on the harness.
- Performance matches or exceeds legacy toolkit.
- One full campaign (property acquisition) runs end-to-end with the harness.

### 3.5 Cross-adapter parity
- Golden-task scenario runs on all three adapters.
- Event logs cross-compatible.
- Consensus Packet bit-for-bit identical given identical inputs (where determinism allows).

### 3.6 Documentation + tutorials
- Complete quickstart per adapter.
- Worked-example notebooks (rental, code, research).
- Deployment guide for each adapter.
- Eval-harness user guide.

**Exit gate:** Round-3 benchmark run meets §02 targets:
- ≥ 90% intent-alignment on held-out tasks.
- ≤ 0.05 cosine drift on orchestrator context.
- Brier ≤ 0.15 on verifier-testable claims.
- 100% human-gate on irreversible actions.
- 0 prompt-injection goal substitutions in adversarial eval.
- Cost ≤ 20× single-agent baseline.

## Beyond Round 3

- **Round 4** — additional adapters (LangGraph, AutoGen, emerging agent IDEs).
- **Round 5** — production deployment templates, secrets management, compliance packaging (SOC 2 / ISO 27001 traceability).
- **Ongoing** — benchmark rotation, guardrail adversarial-set updates, retrospective-driven config improvements, yearly major version of the protocol.

## Cadence decisions

- **Protocol versions** — minor bumps (0.1.x) are additive; 0.2.0 comes with Round 2; 1.0.0 aligns with Round 3 completion.
- **Adapter versions** — tracked independently per adapter.
- **Eval benchmarks** — rotated quarterly after 1.0.0 to prevent overfit.
- **Constitutional rules** — changes only at major-version boundaries.

## Team shape (for planning)

Round 2 realistically: 1 tech lead + 2 engineers + 1 ML/eval engineer + 1 technical writer, ~4 weeks.
Round 3 realistically: same team + 1 more adapter engineer, ~8 weeks.

## One-line summary

> Round 1 ships the design. Round 2 ships runnable scaffolding + Claude Code adapter + eval harness + rental-toolkit port. Round 3 ships Codex + Cursor adapters, full benchmark suite, and a benchmarked rental campaign on the harness. Every round has a concrete exit gate.
