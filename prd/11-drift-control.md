# 11 · Drift Control and Intent Preservation

## Why drift is the primary risk

Of the eight failure modes named in §03, **intent drift (F1)** is the one that kills campaigns silently. The others (context rot, echo chamber, runaway cost) produce *visible* failure signals — a wrong answer, a timeout, a billing spike. Drift produces output that looks correct, feels purposeful, and quietly answers a different question than the one the principal asked.

This chapter specifies how the harness measures drift continuously, surfaces it automatically, and pauses the campaign when the threshold is crossed.

## 11.1 The INTENT anchor

All drift detection is *relative to INTENT*. The anchor is `INTENT.md` (§02, §6.2) — an immutable document edited only by the human principal.

Its components:
- **Goal** — one paragraph, measurable.
- **Success criteria** — table with target + hard-floor per criterion.
- **Non-goals** — explicit exclusions.
- **Hard constraints** — things that cannot be traded.
- **Decision framework** — what to do when unspecified.

Drift detection reads these components structurally, not as prose.

## 11.2 The drift score

**Two-signal composite:**

### Signal A — semantic distance (quantitative)
- Embed `INTENT.md` at campaign start (one-time).
- Embed a rolling summary of the orchestrator's current context at each checkpoint.
- Compute cosine distance. Target ≤ 0.05. Hard floor 0.15 (§02).

### Signal B — LLM-judge qualitative score (qualitative, structured)
- Prompt: "Given INTENT and the orchestrator's current state, score 0–100 how well the current state advances each INTENT success criterion. List any decisions made that violate hard constraints."
- Target ≥ 90. Hard floor 75.

**Combined rule.** Both signals agree → proceed. One fails → flag for review. Both fail → pause the campaign.

## 11.3 Cadence

Drift checks run:
- **Every N orchestrator turns** (default: 3). Cheap — a small embedding call + a short LLM-judge call.
- **Every cohort packet** received by the primary orchestrator. Same two signals, scoped to whether the packet's addition to the state would increase drift.
- **End of campaign.** Final drift score is part of the retrospective rubric.

## 11.4 Drift responses

Depending on signal severity:

| Score | Action |
|---|---|
| Both signals within target | Proceed. Log the score. |
| One signal failing, other in target | Warn in orchestrator context. Proceed but request tighter scoping next step. |
| Both signals failing | **Pause.** Surface to human with a structured report: what drifted, what the current plan thinks the goal is, what INTENT says it is, what the proposed correction is. Require explicit approve/reject. |
| Hard floor breached on either | **Halt.** Campaign cannot continue until human resolves. |

The pause-on-drift is the enforcement arm that makes "intent preservation is the top invariant" (§02) operative. Without it, the invariant is just a nice-to-have.

## 11.5 Continuous tracking artifact

Every campaign produces a `drift.jsonl` log:

```json
{"t": "2026-04-18T09:12:00Z", "turn": 14, "signal_a": 0.03, "signal_b": 94, "action": "proceed"}
{"t": "2026-04-18T09:19:00Z", "turn": 17, "signal_a": 0.08, "signal_b": 78, "action": "warn"}
{"t": "2026-04-18T09:24:00Z", "turn": 20, "signal_a": 0.14, "signal_b": 71, "action": "pause"}
```

This is the evidence stream the retrospective (§13) uses to answer "when did the campaign start losing the plot?"

## 11.6 What counts as drift (with examples)

Drift is not the same as **plan revision**. The harness must tell them apart.

| Scenario | Drift? | Why |
|---|---|---|
| "User asked for rental acquisition; orchestrator starts researching commercial mortgages." | Yes | Shifts the asset class INTENT defined. |
| "User asked for rental acquisition; orchestrator adds a step to evaluate rentability before purchase." | No | Tighter execution against the same goal. |
| "User asked for a consensus answer; orchestrator picks one expert's answer without aggregation." | Yes | Abandons the consensus discipline. |
| "User asked for a consensus answer; orchestrator runs a swarm and returns with interval + dissent." | No | On goal. |
| "User asked for Florida-law analysis; orchestrator proposes a California comparison case." | Borderline | Flag for approval; proceed only with explicit user consent. |
| "User asked for a PRD; orchestrator expands Section 3 into 10K words." | Not drift, but scope creep | Caught by budget, not drift. |

The LLM-judge signal is trained on this kind of distinction. Prompts live in §16 adapter templates.

## 11.7 Drift versus replan

Sometimes the right response to drift detection is *to replan* — the original plan was wrong, new evidence justifies a shift. The harness accommodates this via the **plan revision** flow:

1. Orchestrator proposes a plan revision with justification.
2. Orchestrator writes the revision to the `plan_revisions/` folder as a diff.
3. The diff is surfaced to the human (if material) or auto-approved (if minor — the decision framework in INTENT specifies the threshold).
4. If auto-approved, the drift baseline is re-anchored: the revised plan becomes the new comparison point for subsequent drift checks, while INTENT itself never changes.

This preserves the "INTENT is immutable" invariant while allowing plans to adapt.

## 11.8 The drift detector as a portable program

Following the rental toolkit's `drift_check.py` pattern, the drift detector ships as a small, runnable Python program with the protocol:

**Input:** `INTENT.md`, rolling orchestrator context, cadence config.
**Output:** `drift.jsonl` entry + (if action != proceed) an `escalation.json` for the human.

It runs either as a library call from any harness adapter, or as a standalone subprocess. §16 specifies both wiring patterns.

## 11.9 Mitigates, specifically

- **F1 (intent drift)** — directly.
- **F2 (context rot on primary orchestrator)** — indirectly, since drift correlates with context rot.
- **F3 (compounding error)** — partially, since compounded error tends to surface as drift.
- **F8 (silent failure on irreversible actions)** — indirectly, since drift-paused campaigns can't reach the action gate.

## Diagram reference

- **D08 (Drift control loop)** — the checkpoint flow.

## One-line summary

> Embed INTENT once. Score every N turns with cosine distance and an LLM judge. On threshold breach, pause the campaign and surface the diff to the human. INTENT never changes silently; plans can, under review.
