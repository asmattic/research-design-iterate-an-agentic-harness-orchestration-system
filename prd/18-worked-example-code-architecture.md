# 18 · Worked Example — Code Architecture (MetaGPT / ChatDev critique and redesign)

## Why this case study

The open-source literature on multi-agent code generation is dominated by three systems that ship working code and have published results: **MetaGPT** *(Hong et al., 2024)*, **ChatDev** *(Qian et al., 2023)*, and **AutoGen** *(Wu et al., 2023)*. Each encodes a different stance on orchestration. Examining them side-by-side — what each does well, where each fails — is the clearest way to validate this PRD's architectural choices against real, publicly-inspectable systems.

This chapter does three things:
1. Summarizes each system's design stance.
2. Identifies the failure modes each exhibits in practice.
3. Redesigns a code-architecture campaign on this PRD's harness to directly address those failures.

## 18.1 MetaGPT (Hong et al., 2024)

**Architecture stance.** Encode real-world Standard Operating Procedures (SOPs) as multi-agent workflows. Each agent has a role (Product Manager, Architect, Project Manager, Engineer, QA). Communication is via **structured documents** (PRD, Design Doc, Task List, Code, Test Report) rather than free-form dialog.

**What it gets right.**
- **Structured documents as the inter-agent contract.** This is the insight this PRD generalizes as Agent Contracts + Consensus Packets.
- **Role specialization** reflects real team structure; different prompts per role.
- **Publishable results.** Reported strong HumanEval / MBPP performance.

**Where it fails.**
- **Serial waterfall.** Stages happen in sequence (PM → Architect → Engineer → QA). F3 (compounding error) is systemic — a bad assumption at PM stage cascades all the way.
- **No verifier arbitration.** QA agent is an LLM; no deterministic test gate between stages.
- **No confidence intervals.** Single-agent emissions at each stage.
- **No drift control.** If the PRD drifts from user intent, later stages amplify.

**How this PRD addresses.**
- Replace waterfall with a primary orchestrator + cohorts (PM-cohort, Architecture-cohort, Engineering-cohort, QA-cohort) running with per-stage verifier gates.
- Replace single-agent QA with a 3-agent QA swarm + deterministic test runner; disagreement routes back to Engineering.
- Drift detector reads the PM output vs user INTENT at every transition.

## 18.2 ChatDev (Qian et al., 2023)

**Architecture stance.** Simulated software company with CEO, CTO, Programmer, Designer, Reviewer, Tester agents. Workflow follows a simulated project lifecycle.

**What it gets right.**
- **Full-lifecycle coverage** — design, code, test, docs.
- **Role-playing** produces richer critiques than a single agent.

**Where it fails.**
- **Free-form inter-agent dialog** between roles. This is F4 (echo chamber) in classical form: a Reviewer who likes the Programmer's code and a Programmer who respects the Reviewer converge on a local optimum without testing it.
- **No external ground truth.** Tests are hypothetical, not executed.
- **No cost control.** The simulated company's dialogs expand until the LLM is bored.

**How this PRD addresses.**
- Replace free-form dialog with caucus (§07), time-boxed and turn-count-bounded.
- Mandatory deterministic verifier: code is executed, tests are run, failures block progression.
- Explicit budget per cohort (§08 parallelism bounds) to prevent dialog sprawl.

## 18.3 AutoGen (Wu et al., 2023)

**Architecture stance.** Conversable agents with a generic orchestrator; agents chat in a directed graph. Ships with coordinator patterns (GroupChatManager, sequential, nested).

**What it gets right.**
- **Generic orchestration primitives** — the base unit is correct.
- **Tool use first-class**, including code execution.
- **Flexible** — easy to build a variety of agent graphs.

**Where it fails (relative to this PRD's goals).**
- **No opinionated signal-weighting layer.** The framework is unopinionated; the user has to build the Orchestrator System themselves.
- **No first-class drift or intent preservation.** The system is a set of chat loops.
- **No calibration or eval framework built in.**

**How this PRD addresses.**
- AutoGen is *a runtime* we could in principle adapt to (future work; see §16.8). The protocol would slot in above AutoGen's orchestration graph; we'd enforce the Orchestrator System behaviors via middleware.

## 18.4 Redesign — a code-architecture campaign on this harness

**The task.** Refactor a medium-size open-source library (say, a 25-file TypeScript logging module) to migrate from callback-based APIs to Promise-based APIs, preserving behavior, with tests green.

**INTENT.md (excerpt).**
```
# Goal
Migrate <library> from callback-based public APIs to Promise-based APIs. All existing tests pass. No breaking API changes beyond the callback→Promise shift. TypeScript strict mode holds.

# Success criteria
- All existing unit tests pass.
- Integration tests pass.
- TypeScript compiles in --strict.
- Public API surface preserved (symbol compatibility via codemod).
- Bundle size does not grow > 5%.
# Non-goals
- Behavioral changes (no new features).
- Internal refactors unrelated to the API shift.
# Hard constraints
- No test may be deleted or skipped to make green.
- No `any` escape hatches introduced.
```

**Cohort dispatch.**

| Cohort | Role | Experts |
|---|---|---|
| **Architecture** | Plan the migration; identify API boundaries | architect_lead, architect_critic (adversary) |
| **Codemod** | Mechanical transformations | codemod_author (×3 with different codegen strategies) + codemod_judge |
| **Engineering** | Hand-refactor edge cases the codemod misses | senior_engineer, junior_engineer, code_reviewer |
| **QA** | Verify correctness | test_runner (deterministic), coverage_analyst, differential_tester |

**Deterministic verifier tools.** `tsc --noEmit --strict`, `pytest` / `vitest`, coverage delta, bundle-size delta, AST-diff on public API.

**End-to-end flow.**
1. Primary orchestrator dispatches to Architecture cohort. 2-agent caucus (architect_lead vs architect_critic) produces migration plan with risks and rollback strategy. Caucus output → Consensus Packet.
2. Orchestrator approves plan. Dispatches to Codemod cohort with one module at a time.
3. Codemod cohort: 3 codemods generate independently; judge compares and selects the best. Verifier runs `tsc` and tests. Iterates until green per module.
4. Engineering cohort picks up modules the codemod can't handle. Swarm of senior+junior+reviewer produces a hand-refactor; verifier gates.
5. QA cohort runs full test suite + coverage + bundle size after every module merge. Differential tester compares behavior with the pre-migration baseline for a held-out set of I/O traces.
6. Primary orchestrator monitors drift (are we expanding scope?) and cost. Pauses if either crosses threshold.
7. Final irreversible action: merge to main. Human gate.

**Why this beats MetaGPT/ChatDev/AutoGen on the same task.**
- **Parallelism where independent.** Per-module refactor runs in parallel (dispatch pattern §08).
- **Serial where dependent.** Plan → implement → test is serial, but each hop has a verifier gate.
- **Confidence intervals.** Codemod cohort reports "codemod A wins with 0.87 confidence; codemod B is a 0.11 minority" rather than picking silently.
- **No free-form dialog.** Caucus is bounded to the plan step; everything else is packet-mediated.
- **Real tests are the oracle.** No LLM-only QA signoff.
- **Drift catch.** If an agent proposes "while we're here, let's also refactor X", drift rises and the orchestrator pauses.

## 18.5 Benchmark anchor — SWE-bench Verified

**SWE-bench Verified** *(Jimenez et al., 2024)* is the current standard for evaluating agent code-modification systems. Real GitHub issues paired with real test patches. Pass = the generated patch makes the hidden tests pass without breaking any prior tests.

This harness's code-architecture adapter should score competitively on SWE-bench Verified. Our reference target (Round 3):
- Baseline (single-agent Opus 4): ~50% (public numbers from summer 2025).
- This harness with 3-cohort config (plan / edit / verify): target ≥ 58%.
- Ablations:
  - Without deterministic verifier: -6 points (predicted).
  - Without drift control: -2 points (predicted).
  - With mesh instead of hub: -4 points (predicted).

Ablations are part of the eval harness (§14) and validate each architectural decision.

## 18.6 Mitigates, mapped

| Failure | Mitigation in this example |
|---|---|
| F1 drift | Orchestrator pauses when agents propose scope-expanding refactors |
| F2 context rot | Primary orchestrator sees packets, not module-level diffs |
| F3 compounding error | `tsc` + tests gate every hop |
| F4 echo chamber | Architect vs architect_critic caucus surfaces principled dissent on migration risk |
| F5 unverifiable | Differential tester gives deterministic ground truth on behavior preservation |
| F6 runaway cost | Per-module budget + parallelism ceiling |
| F7 prompt injection | Codemod output runs only under the verifier's sandboxed process; no arbitrary code execution in orchestrator context |
| F8 silent merge | Final merge to main is a human gate |

## One-line summary

> MetaGPT's structured-documents pattern is correct but missing verifier arbitration and confidence intervals. ChatDev's free-form dialog is a classical echo-chamber case. AutoGen is a runtime; this harness is the opinionated layer on top. Putting them side by side confirms the PRD's architectural bets.
