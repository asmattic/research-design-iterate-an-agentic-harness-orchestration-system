# 13 · Feedback Loops

## Three cadences

The harness runs three distinct feedback loops on three cadences, because **different kinds of learning need different scopes and different write targets.**

| Cadence | Name | Scope | Writes to | Approximate cost |
|---|---|---|---|---|
| Per-turn | Reflexion | Single agent, single turn | That agent's `learnings` section (L1) | Small — one extra LLM call |
| Per-task | Retrospective | One task, multi-agent | Agent-prompt diffs, L2 memory entries | Moderate — a multi-agent review |
| Per-campaign | Eval Harness | All campaigns of a task type | System config, cohort composition, constitutional updates | Large — full benchmark run |

## 13.1 Per-turn: Reflexion

**Origin.** *Shinn et al., Reflexion: Language Agents with Verbal Reinforcement Learning (2023).* Pattern: after an agent attempts a task, the same agent (or a dedicated reflector) writes a short verbal critique — what went well, what didn't, what to try next. The critique is appended to the agent's episodic memory.

**Here:** After every expert-agent emission, if the verifier/BS-detector/cross-agent-agreement scores are notably off, a reflector LLM writes a one-paragraph critique into that agent's `learnings` section in L1 memory. The next turn for that same agent re-loads the learnings.

**Trigger conditions.**
- Verifier flagged a claim.
- BS Detector flagged over-confidence or hallucination.
- Cross-agent disagreement was high.
- Agent self-reported low confidence (< 0.5) on a claim the orchestrator accepted.

**Why not every turn.** Reflecting on clean runs is expensive and unhelpful. Reflect on turns where signal suggests something to learn.

## 13.2 Per-task: Retrospective

**Purpose.** After a task finishes (success or failure), an LLM-as-judge reviews the task's event log and proposes concrete prompt-level improvements.

**Inputs.**
- The task's event log (L3 read).
- The task's consensus packets (L1 read).
- Any verifier failures or drift alarms during the task.
- The task's completion criteria (from INTENT subsetted to the task).

**Outputs (three types of diff):**
1. **Agent-prompt diff** — proposed change to a specialist agent's system prompt. Written to `proposals/agent_prompts/<agent>.diff`. Human ratifies between campaigns.
2. **L2 memory entry** — a new or superseding memory row ("Hillsborough County zoning ordinance X was re-interpreted this week to permit Y; confidence 0.8"). Written to L2 directly, with `source`, `confidence`, `supersedes`.
3. **Weight adjustment** — proposed change to the Signal/Noise Attributor weights for this cohort. Written to `proposals/weights/<cohort>.json`. Human or auto-ratified per configuration.

**Separation of proposals from ratification.** The retrospective never silently mutates agent prompts or INTENT (§02 hard constraint). It writes diffs; the human ratifies. This is the discipline that keeps auto-improvement from becoming auto-degradation.

## 13.3 Per-campaign: Eval Harness

**Purpose.** Across a benchmark set of tasks, compute system-level metrics and use them to tune system-level configuration.

**Benchmarks.** A held-out task set per domain:
- Finance / Rental: held-out set of 20 rental-acquisition scenarios with ground-truth outcomes.
- Code architecture: SWE-bench Verified subset (§18).
- AI research: GAIA research-task subset (§19).
- Plus synthetic adversarial tasks (prompt-injection, drift-induction) for safety guardrails.

**Metrics computed.**
- Completion rate — fraction of tasks reaching "done" per INTENT criteria.
- Intent-alignment — retrospective rubric score per task.
- Drift — mean + worst-case drift score per task.
- Brier / ECE — calibration across testable claims.
- Cost — tokens + wall-clock + dollar per task.
- Safety — guardrail false-allow rate on adversarial payload set.

**Outputs (system-level).**
- Default swarm sizes per cohort.
- Default confidence thresholds per claim class.
- Per-cohort guardrail overrides.
- Proposed constitutional additions (always human-ratified).

**Cadence.** Once per planned release cycle — not once per campaign. The eval harness is an expensive operation (multi-hour run on ~100 tasks); running it too often produces noise.

## 13.4 Feedback hierarchy — what writes what

```
INTENT
  └── human-only writer
Constitution
  └── human-only writer (eval harness proposes)
Cohort composition, guardrail config
  └── cohort-owner writer (eval harness proposes)
Agent prompts
  └── human ratifies retrospective-proposed diffs between campaigns
Signal weights
  └── auto-ratified up to ±10% move; human ratifies larger shifts
L2 memory entries
  └── retrospective writes directly; flagged for audit but not blocked
Agent learnings (L1)
  └── Reflexion writes directly; reset at campaign end (promoted to L2 if retrospective approves)
Event log (L3)
  └── append-only, every agent / tool / orchestrator / verifier action
```

This ordering encodes a simple principle: **the closer to INTENT, the harder to change.** INTENT is human-only; constitution is human-ratified; per-cohort config is owner-ratified; per-agent prompts are between-campaign ratified; weights can auto-tune within bounds; memory learns continuously. Drift up the hierarchy is not allowed.

## 13.5 Anti-pattern — self-modifying in-campaign prompts

An agent that rewrites its own system prompt *during a campaign* to adapt to what it's learning is **explicitly forbidden** (§02 non-goal). The reasons:

- It defeats reproducibility — you can't replay the campaign.
- It defeats the eval harness — metrics are about the agent-as-configured, not a moving target.
- It is a known jailbreak vector — a prompt-injection payload can rewrite the agent's prompt.

In-campaign *learnings* (L1 additions) are allowed and helpful. In-campaign *prompt changes* are not.

## 13.6 Feedback loops and the three-valued outcome

When the retrospective re-examines a prior claim via a fresh swarm:
- If new evidence supports the prior → emit `strengthened` outcome, raise confidence.
- If new evidence contradicts → emit `revised`, surface the diff for review.
- If no new evidence but methodology refined → emit `unchanged-but-calibrated`, update interval only.

(Same three-valued contract as §9.3.)

## 13.7 Mitigates

- **F1 (intent drift)** — retrospective rubric includes drift score; recurring drift triggers agent-prompt updates.
- **F3 (compounding error)** — Reflexion catches turn-level error early; retrospective fixes the source.
- **F4 (echo chamber)** — retrospective audits cohort composition; eval harness tunes diversity axes.
- **F6 (runaway cost)** — eval harness surfaces cost/quality curves; cohort sizes tune.

## Diagram reference

- **D10 (Feedback loops)** — three concentric cadences.

## One-line summary

> Reflexion per turn, retrospective per task, eval harness per campaign. All write proposals; humans ratify changes near INTENT. No in-campaign self-rewrite.
