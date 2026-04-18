# 20 · Risks, Failure Modes, Mitigations

## Approach

§03 named eight failure modes (F1–F8). This chapter adds the **operational and project-level risks** that sit outside those failure-mode definitions, and provides an integrated mitigation table. Each row pairs a risk with (a) its likelihood, (b) its severity, (c) the mitigation planned, (d) whether the risk is accepted with justification or fully mitigated.

## 20.1 Risk register

| # | Risk | L | S | Mitigation | Status |
|---|---|---|---|---|---|
| **R1** | Intent drift (F1) | H | H | §11 continuous drift detection + pause-on-threshold | Fully mitigated |
| **R2** | Context rot on primary orchestrator (F2) | H | H | §§6.3, 10 clean context + tiered memory | Fully mitigated |
| **R3** | Compounding error across hops (F3) | H | H | §§6.7, 9 verifier at every hop + confidence aggregation | Fully mitigated |
| **R4** | Local-agreement echo chamber (F4) | M | H | §6.6 deliberate swarm diversity + adversary role | Fully mitigated |
| **R5** | Unverifiable stochastic claims (F5) | H | M | §6.7 deterministic verifier precedence | Fully mitigated where testable |
| **R6** | Runaway token / latency cost (F6) | M | H | §§8, 14 budgets + parallelism bounds | Fully mitigated |
| **R7** | Prompt-injection / goal substitution (F7) | M | H | §12 guardrails + data/instruction separation | Fully mitigated (continuously adversarially tested) |
| **R8** | Silent failure on irreversible actions (F8) | H | Critical | §§02, 6.1 hard constraint + human gate | Fully mitigated (constitutional) |
| **R9** | Model provider availability / rate limiting | M | M | Adapter layer allows fallback to alternate model families per cohort | Partially mitigated |
| **R10** | Model provider pricing shifts | M | M | Cost budget per campaign; cost eval detects changes | Monitored |
| **R11** | Adapter drift — runtime primitive changes break adapter | M | M | Conformance tests (§15.11) gate adapter releases | Partially mitigated |
| **R12** | Eval set becomes stale / overfit | M | M | Rotate benchmark sets; hold out portions; track benchmark age in eval report | Partially mitigated |
| **R13** | Agent-prompt rot — retrospective updates accumulate drift across campaigns | L | M | Prompts are version-controlled; eval harness regression-gates proposed diffs | Partially mitigated |
| **R14** | Over-reliance on LLM-as-judge | M | M | Judge calibration against human-labeled set + deterministic precedence rule | Partially mitigated |
| **R15** | Constitutional bypass via clever prompt | L | H | Layered guardrails (schema + classifier + LLM-judge); constitutional rules duplicated across layers | Partially mitigated |
| **R16** | Memory leak — stale L2 entries used as fresh | M | M | `freshness`, `expires`, `supersedes` fields; retrospective periodically re-validates top-used entries | Partially mitigated |
| **R17** | Swarm homogenization — accidental loss of diversity over retrospectives | L | M | Diversity audit in eval harness; retrospective proposals flagged if they reduce diversity | Monitored |
| **R18** | Human approval fatigue — too many gates, human rubber-stamps | M | H | Tier gate thresholds; rubric on what requires gate; bundle non-critical approvals | Partially mitigated |
| **R19** | Adapter fragmentation — "works on Claude Code, broken on Codex" | M | M | Conformance tests + golden tasks run on every adapter per release | Partially mitigated |
| **R20** | Over-general architecture, under-delivered reality | M | H | Round 2 delivers runnable scaffolding; Round 3 runs real campaign end-to-end | Mitigated through phased delivery |

## 20.2 Explicitly accepted risks

Three risks are explicitly accepted, with rationale:

### A1. 15–20× token cost vs single-agent baseline
**Accepted because:** for tasks where this harness is appropriate (long-horizon, multi-specialist, high task value), the token cost is dwarfed by the value of a correctly-completed outcome vs a near-miss. §02 sets the ceiling at 20×; breaching it is a monitored regression.

### A2. Non-determinism in LLM outputs
**Accepted because:** LLMs are stochastic by design. We pair them with deterministic verifiers everywhere possible; we accept residual non-determinism on subjective judgments and pair it with confidence intervals. §02 hard constraint states the precedence rule.

### A3. No runtime lock-in means more work
**Accepted because:** the 10% adapter-layer cost buys us harness portability. The alternative (adapter-free, one-runtime design) saves 10% now and costs 70% on the first runtime migration. Historical precedent in agent frameworks strongly suggests at least one migration is coming.

## 20.3 Mitigations that impose trade-offs

### Drift control vs. exploration
Continuous drift detection with pause-on-threshold keeps intent-aligned but can limit legitimate creative tangents. Mitigation: the threshold is tunable per-cohort and per-campaign; exploratory research campaigns set looser thresholds.

### Deterministic precedence vs. model-right cases
If a test is wrong (flaky, mis-specified) and the LLM is right, the precedence rule still says test wins. Mitigation: tests that fail repeatedly with high-calibration agents' disagreement are surfaced to a human — the test itself may be wrong.

### Human gate vs. throughput
Every gate costs human latency. Mitigation: gate *only* irreversible actions and high-stakes decisions. Budget-burn within declared bounds does not gate; mid-campaign plan revisions below a threshold do not gate.

### Swarm diversity vs. consensus clarity
Deliberately diverse swarms produce more dissent, which is harder to communicate. Mitigation: Consensus Packet schema separates "headline consensus" from "preserved dissent", so primary orchestrator can act on the headline while the audit trail preserves dissent.

## 20.4 Unknown unknowns

Risks we can't enumerate. Mitigations:
- Retrospectives (§13.2) include a free-text "surprises" section.
- Eval harness (§14) includes a "regression on metric I'm not tracking" detector — if any measured quantity moves >1σ from historical baseline, it surfaces.
- Round 3 campaign-end review includes a "did we miss a failure mode?" question, and the answer updates §03's table.

## 20.5 When the harness is the wrong tool

This PRD is explicit about when not to use the harness (§03 assumptions):
- Task value < ~$10 — single-agent is fine.
- Task fits in one context window (≤ 100K tokens) and is single-specialist — single-agent wins on cost.
- Pure creative / exploratory with no verification possible — no verifier leverage.
- Real-time interactive chat UX — orchestration latency is too high.

Using this harness for the wrong task shape is itself a risk; the mitigation is upfront triage, documented in §08 decision tree.

## 20.6 Failure-mode coverage confirmation

Every failure mode named in §03 is addressed above (R1–R8). Additional operational risks (R9–R20) cover provider, adapter, eval, memory, and human-in-the-loop concerns that sit outside the agent-architecture surface.

## One-line summary

> All eight named failure modes are fully or substantially mitigated; twelve operational risks are tracked; three trade-offs are explicitly accepted with rationale; unknown-unknown detection is built into retrospectives and eval regression tracking.
