# 22 · Open Questions

Questions this PRD does not fully resolve. Each has a proposed Round 2 / Round 3 decision path.

## Q1 — How many experts per swarm is the sweet spot per domain?

**Context.** §08 defaults to N = 5 with a ceiling of 12. Anthropic MARS scales adaptively.

**What we don't know.** The cost/quality curve likely differs per domain (finance may saturate at N=3; research may benefit from N=7).

**Resolution path.** Round 2 eval harness runs ablations on swarm size per cohort per benchmark. Round 3 publishes defaults per domain.

## Q2 — Which model families for which cohort roles?

**Context.** §6.6 specifies model diversity as one swarm axis. The adapter layer lets any model slot in.

**What we don't know.** Whether mixing Claude + GPT-class consistently improves outcomes, or whether same-family with temperature/prompt diversity is enough.

**Resolution path.** Round 2 ablation: single-family swarm vs cross-family swarm. Measured by calibration and dissent quality.

## Q3 — Retrospective auto-ratification thresholds

**Context.** §13 allows weight adjustments up to ±10% to auto-ratify; larger changes need human.

**What we don't know.** Whether 10% is the right cutoff, or whether we should look at magnitude × historical-calibration-of-the-proposal instead.

**Resolution path.** Round 2 shadows auto-ratification (log proposal, but still require human) for several campaigns to calibrate the threshold. Round 3 activates.

## Q4 — Minimum viable caucus bounds

**Context.** §07 bounds caucus at 6 turns / 20K tokens / 2 minutes.

**What we don't know.** Whether these are too tight (valuable debates get cut off) or too loose (cost runaway).

**Resolution path.** Per-cohort customization in Round 2; eval harness reports caucus cost/quality correlation; Round 3 publishes defaults per cohort type.

## Q5 — Drift threshold calibration per domain

**Context.** §11 sets target ≤ 0.05 cosine / hard floor ≤ 0.15.

**What we don't know.** Whether creative/exploratory cohorts should have looser thresholds and if so how much.

**Resolution path.** Round 2 lets each cohort override thresholds. Round 3 publishes defaults per cohort type.

## Q6 — How to handle legitimate INTENT evolution during a long campaign

**Context.** §02 says only human can change INTENT; §11 says plan can revise with tracking. For long campaigns (weeks), new information may genuinely change what the principal wants.

**What we don't know.** The clean workflow for a mid-campaign INTENT amendment.

**Current answer.** Stop, human writes an INTENT amendment diff, re-embed INTENT, resume. The amendment is logged in the event stream.

**Resolution path.** Round 2 implements the amendment workflow explicitly. Round 3 evaluates whether that disruption cost is acceptable vs. alternatives.

## Q7 — Event log retention and search at scale

**Context.** §10 sets 2-year default retention. A high-throughput deployment could produce hundreds of GB / year.

**What we don't know.** The right storage backend at scale — flat JSONL works for low volume; larger deployments may need Parquet + columnar query engine.

**Resolution path.** Round 2 ships JSONL; Round 3 adds an optional Parquet archiver for L3 cold storage. Decision deferred until a deployment actually hits the scale.

## Q8 — How to handle tool failures gracefully

**Context.** Deterministic verifier tools can fail (network, rate limit, bug). §15.10 specifies a structured error response; §6.7 has the verifier "abstain" option.

**What we don't know.** The right retry/degradation policy per tool. Some tools are idempotent and safe to retry; some aren't.

**Resolution path.** Each tool declares its retry policy in the Agent Contract's tool registry. Round 2 implements; Round 3 tunes defaults.

## Q9 — Cross-campaign memory gravity

**Context.** L2 memory (§10) accumulates over time. A cross-campaign memory that was correct in 2025 may be wrong in 2027.

**What we don't know.** How aggressively to `supersede` or re-validate. Too slow → stale knowledge. Too fast → loss of genuine durable knowledge.

**Resolution path.** Round 2 adds periodic re-validation jobs for top-used L2 entries. Round 3 tunes.

## Q10 — Human-gate UX

**Context.** §6.1 requires gates on irreversible actions. The actual UX depends on the adapter.

**What we don't know.** The best gating UX (inline prompt? separate approval UI? Slack/email out-of-band?). Fatigue (R18) matters.

**Resolution path.** Round 2 uses each adapter's native permission prompt. Round 3 ships a web-based approval dashboard as an optional add-on.

## Q11 — Confidence scoring honesty

**Context.** §9 uses self-reported confidences as an input to weighting. §14 calibrates with Brier/ECE.

**What we don't know.** Whether agents under adversarial pressure (or just over time) learn to game the confidence score.

**Resolution path.** Adversarial eval set checks honesty-under-pressure. Weight Tweaker applies penalty for miscalibration. Round 3 publishes honesty benchmarks.

## Q12 — The right scope for the Orchestrator System's BS Detector

**Context.** §6.4.2 runs an LLM-judge on every expert emission.

**What we don't know.** Whether this double-billing on every turn is net positive vs running BS detection less often but deeper.

**Resolution path.** Round 2 runs both (per-emission vs per-packet) in shadow; measures false-positive rate vs cost.

## Q13 — Interoperability with external agent ecosystems

**Context.** The protocol is portable across our three named runtimes. External teams may want to interoperate with LangGraph, AutoGen, OpenAI Agents SDK.

**What we don't know.** Whether the protocol should be standardized at a scope broader than this project, or remain project-internal.

**Resolution path.** Round 3 proposes an interop spec. If there's uptake, evolve toward an RFC-style standard.

## Q14 — What the "retrospective agent" itself is

**Context.** §13.2 says "LLM-as-judge reviews the event log and proposes diffs."

**What we don't know.** Whether this is a single model call, a multi-agent swarm (a mini-cohort for retrospectives), or an entirely separate system.

**Resolution path.** Round 2 starts with single LLM call + rubric. If calibration is poor, promote to mini-swarm in Round 3.

## Q15 — Compliance posture

**Context.** Depending on deployment, SOC 2 / ISO 27001 / HIPAA may apply.

**What we don't know.** The full compliance story. Event log is a clear audit artifact; privacy tiers (§10.5) map to data classification; but full compliance mapping is Round 5+ work.

**Resolution path.** Round 3 ships a compliance traceability matrix (controls → harness features). Round 5 handles full certification prep.

## How this file evolves

This file is updated at every round boundary. Closed questions get struck through with a "resolved in §X" note. New questions get appended. The file is itself part of the campaign's memory.

## One-line summary

> Fifteen known-unknowns, each with a resolution path mapped to Round 2 or Round 3 work. The list gets shorter at every round; the list does not get silently shorter.
