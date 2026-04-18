# 06 · Core Components

Each component gets (a) a purpose statement, (b) its inputs/outputs, (c) the failure mode(s) from §03 it mitigates, and (d) the citation that justifies its existence.

---

## 6.1 Human Principal

**Purpose.** Sets intent, ratifies INTENT changes, approves irreversible actions, consumes final output.

**I/O.**
- In: high-level goal ("acquire a rental in Tampa that cash-flows ≥$300/mo"), approvals on gated actions, corrections to the plan.
- Out: ratified `INTENT.md`, approvals/rejections on action requests, post-campaign feedback.

**Mitigates.** F8 (silent failure on irreversible actions).

**Not optional.** The human is the mandatory serialization point for money-movement, external messaging, or any irreversible side effect. The primary orchestrator cannot bypass this even when confidence is at ceiling. (§02 hard constraint.)

---

## 6.2 INTENT anchor (`INTENT.md`)

**Purpose.** The immutable root-of-truth for the campaign. Every plan must trace to it. Drift is measured against it. Only the human can mutate it.

**Structure (patterned on the rental toolkit's INTENT.md):**
```
# Goal
# Success criteria (measurable)
# Non-goals (explicitly excluded)
# Hard constraints
# What "done" looks like
# Decision framework when something isn't specified
# What changes this file
```

**I/O.**
- In: human-authored; modified only via explicit human ratification.
- Out: loaded into every cohort sub-orchestrator, every drift check, every retrospective.

**Mitigates.** F1 (intent drift).

---

## 6.3 Primary Orchestrator

**Purpose.** The strategic, thin layer. Holds the campaign plan; delegates domain work to cohorts; reads back validated packets; decides next step; escalates to human when required.

**Context budget.** Strictly bounded. Guidance: ≤ 40K tokens at steady state, ≤ 80K at peak, with aggressive summarization. The context budget is a design constraint, not a suggestion *(Anthropic, "Effective context engineering," 2025; Liu et al., "Lost in the Middle," 2023)*.

**What's in context.**
- `INTENT.md` (full)
- Current campaign plan / roadmap
- Latest N packets from the Orchestrator System (summaries, not raw logs)
- Latest drift check result
- Outstanding human-approval requests
- Budget status (tokens, time, cost)

**What's *not* in context.**
- Raw expert-agent transcripts
- Tool call logs
- Memory tier L3 (cold archive)
- Other cohorts' internal deliberations

**Prompt skeleton.**
```
You are the Primary Orchestrator for campaign <id>.
INTENT (immutable): <INTENT.md>
Plan: <current plan>
Latest packets: <orchestrator-system packets>
Drift status: <drift score, threshold>
Budget: <tokens used / budget>
Pending approvals: <list>

Decide:
(a) proceed to next plan step,
(b) revise plan (requires drift justification),
(c) request human approval,
(d) declare campaign complete.
Output must be one of the four actions with justification.
```

**Mitigates.** F2 (context rot), F1 (intent drift), F6 (runaway cost via explicit budget visibility).

---

## 6.4 Orchestrator System

This is the **most load-bearing and least standard** component. Six sub-responsibilities, each implemented as a separate prompt / program, run in parallel on every expert-agent output before it reaches the primary orchestrator.

### 6.4.1 Context Manager
- **Purpose.** Decide what each downstream component receives from memory tiers. Summarize long transcripts. Prune redundant or superseded state.
- **Key behavior.** Implements the context-engineering discipline from §04. Every load operation is budget-aware.
- **Citation.** Anthropic context-engineering 2025; Liu et al. 2023.

### 6.4.2 BS Detector
- **Purpose.** Catch hallucinations, fabricated citations, over-confident claims, and suspiciously convenient conclusions before they propagate.
- **Technique.** LLM-as-judge against a skeptic rubric + cross-reference against deterministic verifier where possible + heuristics (e.g., citation plausibility check, numerical sanity bounds).
- **Output.** Flags: `hallucinated`, `over-confident`, `unsupported`, `clean`. Flagged content routes back to the cohort with a reject reason.
- **Citation.** Kadavath et al. 2022 on self-calibration; Zheng et al. 2024 on LLM-as-judge.

### 6.4.3 Validator / Verifier bridge
- **Purpose.** Route testable claims to the deterministic verifier; collect verifier results and attach them to the packet.
- **Key behavior.** Every claim that can be tested (code, SQL, JSON schema, numeric range, URL existence, date consistency) gets tested. Untestable claims are marked as such; LLM judgment is the fallback only when no deterministic option exists.
- **Mitigates.** F3 (compounding error), F5 (unverifiable stochastic claims).
- **Citation.** Lightman et al. 2023 (process supervision).

### 6.4.4 Signal / Noise Attributor
- **Purpose.** Assign each incoming claim a signal-weight based on (a) source agent's historical calibration, (b) verifier result, (c) cohort confidence interval, (d) cross-agent agreement.
- **Output.** Weighted claims ranked for inclusion in the orchestrator packet.
- **Citation.** Brier 1950 (scoring rules); Platt 1999 (probability calibration); Wang et al. 2023 (Self-Consistency).

### 6.4.5 Weight Tweaker
- **Purpose.** Adjust per-agent and per-tool trust weights over time based on retrospective outcomes. If the budget-expert has been right 92% of the time and the tax-expert 71%, their claims get scaled accordingly.
- **Output.** Updated weight table used by the Signal/Noise Attributor.
- **Cadence.** Per-task update; per-campaign recalibration. Not per-turn (would overfit).
- **Citation.** Kadavath et al. 2022; Lin et al. 2022 (truthfulness under tuning).

### 6.4.6 Drift Detector
- **Purpose.** Continuously measure semantic distance between current orchestrator state and INTENT. Alert when distance crosses threshold.
- **Technique.** Cosine distance between INTENT-embedding and rolling-context-embedding + LLM-judge qualitative check.
- **Action on alarm.** Pause, surface the drift to the human, require explicit continue/revise.
- **Mitigates.** F1 (intent drift).
- **Citation.** Generalization of the rental toolkit's `drift_check.py`; the pattern is novel-in-combination, not novel-in-isolation.

---

## 6.5 Cohort Sub-Orchestrators

**Purpose.** Domain-scoped managers. A cohort is defined by (a) its domain (finance, legal, security, research, ops), (b) its tools (Stripe API, Clerk-of-Court lookup, Grep, vector DB), (c) its experts (N specialists), (d) its SLAs (latency/cost bounds).

**I/O.**
- In: a task from the Primary Orchestrator, scoped to the cohort's domain.
- Out: a packet (structured JSON, see §15) containing: consensus answer, confidence interval, dissenting views, verifier results, cost/latency telemetry.

**Internal behavior.** A cohort decides whether the task needs a single expert or a swarm (§08 decision tree). For swarms, it orchestrates the N expert calls, aggregates via the Consensus Packet schema, and emits.

**Mitigates.** F2 (keeps primary context clean — cohort absorbs the expert-level detail), F4 (echo chamber — cohort enforces perspective diversity within swarms).

---

## 6.6 Expert Agents and Expert Swarms

**Purpose.** The specialists. An expert is an agent with a focused system prompt, a specific toolset, and a structured-I/O contract.

**Contract.** Every expert returns JSON matching the Agent Contract schema (§15). Free-form prose lives in a `notes` field; machine-consumable results live in typed fields.

**Single expert vs swarm — decision rule.**
- **Single** if: the task is narrowly scoped and verifier-testable (e.g., "extract the HOA dues from this PDF"), *or* cost-sensitive.
- **Swarm** if: the task benefits from perspective diversity (e.g., "evaluate whether this zoning code permits short-term rentals"), involves subjective judgment, or is high-stakes.

**Swarm composition — deliberate diversity.** A swarm of five agents should NOT be five copies of the same prompt. Specialization axes:
1. **Adversarial role** — one agent explicitly asked to argue against the leading hypothesis.
2. **Literature-first vs data-first** — one agent grounded in static knowledge, another in live retrieval.
3. **Different model families** — where cost allows, mix Claude and GPT-class for epistemic diversity.
4. **Different retrieval views** — different top-k, different rerankers, different query rewrites.
5. **Different temperatures** — low for factual agents, higher for creative/exploration agents.

**Swarm output.** Confidence-interval consensus via the Consensus Packet schema (§15). Three-valued outcome: *strengthened / revised / unchanged-but-calibrated* (§09).

**Mitigates.** F3 (compounding error — multiple perspectives catch errors), F4 (echo chamber — designed diversity).

---

## 6.7 Deterministic Verifier

**Purpose.** The only oracle that is not itself an LLM. Runs code, executes SQL, validates JSON schemas, checks URLs, runs lint/type/security scanners.

**When it runs.** Every expert emission that contains a testable claim goes through the verifier via the Validator/Verifier bridge (§6.4.3).

**When it wins.** Always — over any LLM opinion. (§02 hard constraint.)

**When it abstains.** When the claim is not testable (subjective judgment, novel domain, unknown ground truth). In that case, LLM-as-judge takes over but at lower signal-weight.

**Mitigates.** F3, F5.

**Citation.** Lightman et al. 2023 (process reward).

---

## 6.8 Tiered Memory

See §10 for the full treatment. The one-line summary here: four tiers (L0 working, L1 hot, L2 indexed, L3 cold) with explicit load/eviction policies, privacy tagging, and a memory index that the orchestrator consults rather than globbing storage directly.

---

## 6.9 Guardrails

See §12. The one-line summary: policy / safety / quality / privacy checks at every agent → orchestrator boundary, implemented as composable programmable rules in the adapter layer (NeMo Guardrails / Llama Guard / bespoke).

---

## 6.10 Feedback Loops

See §13. Per-turn Reflexion, per-task retrospective, per-campaign eval harness.

---

## Component interaction summary

```
Expert emission
   → Validator/Verifier bridge → Deterministic Verifier (if testable)
   → BS Detector (hallucination + over-confidence flags)
   → Signal/Noise Attributor (weights by source + verifier + agreement)
   → Context Manager (summarize, bounds to budget)
   → Packet emitted to Primary Orchestrator
   ← Drift Detector runs in parallel; pauses campaign if threshold crossed
```

Diagram **D02 (Orchestrator System detail)** in `/diagrams/`.
