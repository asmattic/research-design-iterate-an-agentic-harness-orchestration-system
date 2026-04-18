# 09 · Signal Weighting and Consensus

## The problem this chapter solves

N specialist agents produce N answers. Naïve approaches — "take the majority", "take the first", "average them" — discard information. The discarded information is usually the *principled dissent*, which is the single most important signal in hard problems.

This chapter specifies how the harness:
1. Weights incoming signals (per-agent, per-tool, per-verifier-result),
2. Aggregates a swarm's output into a confidence-interval consensus,
3. Emits a three-valued outcome (*strengthened / revised / unchanged-but-calibrated*),
4. Preserves dissent for later review.

## 9.1 Signal weighting — the inputs

Every expert emission carries metadata used by the Signal/Noise Attributor (§6.4.4):

| Factor | Description | Default weight |
|---|---|---|
| Agent calibration score | Brier score on this agent's historical testable claims | 0.30 |
| Verifier result | Pass / fail / abstain from deterministic verifier | 0.30 |
| Cross-agent agreement | Fraction of swarm-mates whose answer this agrees with semantically | 0.20 |
| BS-detector flags | Clean / over-confident / unsupported / hallucinated | 0.15 |
| Tool-result authority | Primary source vs secondary vs tertiary | 0.05 |

Weights are *configurable* per cohort — e.g., a legal cohort weights primary-source citation more heavily, a research cohort weights cross-agent agreement less heavily (dissent is the point there).

**Update rule.** After each campaign, retrospectives measure which weight combinations best predicted ground truth. The Weight Tweaker (§6.4.5) updates weights via simple gradient on a held-out task set.

## 9.2 Consensus aggregation

For a swarm of N agents emitting potentially different answers, the aggregator does not majority-vote. It runs:

1. **Semantic grouping** — LLM-as-judge clusters the N answers into semantic-equivalence classes. Two numerically-close answers with the same reasoning form one cluster; two numerically-close answers with different reasoning form two clusters.
2. **Weighted cluster score** — sum of member weights.
3. **Interval derivation** — for numeric claims, take min/max across all emissions + confidence-scaled padding; for categorical claims, report the probability mass in each category.
4. **Dissent preservation** — minority clusters with weight ≥ 15% of the leading cluster are preserved in the output packet.

**Formula sketch (numeric claim):**
```
estimate       = weighted_mean(answer_i, w_i)
interval_low   = min(answer_i | w_i > threshold) - k * weighted_stddev
interval_high  = max(answer_i | w_i > threshold) + k * weighted_stddev
confidence     = sum(w_i in leading cluster) / sum(all w_i)
```

For categorical claims, the packet reports the top-K categories with probability mass, preserving minority positions.

## 9.3 The three-valued outcome

When a follow-up swarm re-examines a prior conclusion (e.g., after new evidence arrives, or during a retrospective pass), the outcome must be one of three values — not just "changed" or "unchanged."

### Strengthened
The new analysis finds additional supporting evidence. The prior conclusion stands; its confidence rises; the interval narrows. Example: "We concluded rent comps supported $2,150/mo. New analysis from a 5-agent swarm with expanded dataset raises confidence from 0.75 to 0.90."

### Revised
The new analysis finds evidence that substantively changes the prior conclusion. Direction or magnitude flips. Example: "We concluded the lease permits short-term rentals. New zoning-ordinance reading reveals a municipal restriction that supersedes HOA docs — revised to 'prohibited.'"

### Unchanged-but-calibrated
The new analysis finds no new evidence either way. The prior conclusion stands. Its interval may widen or narrow based on the new analysis' methodology. Example: "Original DSCR estimate was 1.28 ± 0.04. Re-run with more rigorous sensitivity analysis confirms 1.28 ± 0.05. No revision; calibration refreshed."

**Why three values, not two.** The most common failure in iterative analysis is *silent revision*: the new answer quietly replaces the old without anyone noticing that (a) the old stands and has been *strengthened*, or (b) the new is just *re-saying* the old. Forcing one of three values makes the information content of each pass explicit.

**Mitigates.** F3 (compounding error — re-runs don't silently overwrite), F5 (unverifiable claims — distinguishes "still unverifiable" from "unverifiable but calibrated").

## 9.4 Calibration — Brier score and ECE

**Brier score** (lower is better, bounded [0,1]):
```
Brier = mean_over_claims( (predicted_probability - actual_outcome)^2 )
```
where `actual_outcome` is 0/1 from the verifier.

**Expected Calibration Error (ECE)** — bucket predictions by reported confidence; compare per-bucket reported confidence to per-bucket empirical accuracy. Lower is better.

**Target:** Brier ≤ 0.15, ECE ≤ 0.10 on verifier-testable claims (§02 success criteria).

**Computation cadence.** Per-task (rolling window) and per-campaign (full). The eval harness (§14) owns this.

## 9.5 Two ways the consensus aggregator fails — and how we catch it

### Failure A: False consensus on a shared wrong premise
All five experts read the same outdated Wikipedia article and agree. Consensus is high, confidence is high, answer is wrong.

**Mitigation.** Swarm specialization axis #2 (§6.6) — at least one agent is *literature-first / primary-source only* with distinct retrieval. If all five agents share a retrieval path, we've mis-configured the swarm.

### Failure B: Legitimate dissent ignored
Four experts agree on the expected answer. One expert dissents with a principled reason that turns out to be correct.

**Mitigation.** Dissent preservation rule: minority clusters ≥ 15% are promoted to the packet. The primary orchestrator sees dissent explicitly, not as a filtered-out edge case. In high-stakes decisions, dissent at any level is surfaced.

## 9.6 The Consensus Packet schema (preview)

Full JSON-Schema lives in Appendix D. The shape:

```json
{
  "campaign_id": "…",
  "cohort": "finance",
  "task_id": "…",
  "outcome_type": "strengthened | revised | unchanged_but_calibrated",
  "consensus": {
    "value": "…",
    "value_type": "numeric | categorical | structured | prose",
    "interval": { "low": "…", "high": "…", "units": "…" },
    "confidence": 0.87
  },
  "dissent": [
    {
      "position": "…",
      "agents": ["agent_4"],
      "reasoning": "…",
      "weight_share": 0.16
    }
  ],
  "contributing_agents": [ … ],
  "verifier_results": [ … ],
  "bs_flags": { "hallucinated": 0, "over_confident": 1, "clean": 4 },
  "context_used": { "memory_refs": [ … ], "tools_called": [ … ] },
  "cost": { "tokens": 47213, "wall_clock_ms": 42189, "usd": 0.47 }
}
```

## 9.7 Orchestrator ingestion of the packet

The Primary Orchestrator receives the packet and reads:
1. `consensus.value` (the headline)
2. `consensus.confidence` (how much to lean on it)
3. `dissent[]` (what to flag to the human, especially if weight_share ≥ 25%)
4. `verifier_results[]` (deterministic anchors)
5. `cost` (budget accounting)

The primary orchestrator does **not** read:
- Raw agent transcripts.
- Tool call outputs.
- Internal swarm deliberation.

These are in the event log and retrievable on explicit request (e.g., for a human audit), but they don't bloat primary context.

## 9.8 Worked example — numeric consensus

**Task:** "Estimate the DSCR for this rental under 3 financing scenarios."

5-agent finance swarm, after verifier pass:

| Agent | Scenario A DSCR | Scenario B | Scenario C | Calibration weight |
|---|---|---|---|---|
| budget-conservative | 1.22 | 1.08 | 0.97 | 0.90 |
| budget-aggressive | 1.31 | 1.18 | 1.06 | 0.82 |
| tax-expert | 1.27 | 1.12 | 1.01 | 0.75 |
| market-comps | 1.29 | 1.15 | 1.04 | 0.88 |
| adversary (bear case) | 1.19 | 1.05 | 0.93 | 0.70 |

Packet emits:

- Scenario A: **1.26 [1.19, 1.31], confidence 0.88** — all agents in range, outcome_type = strengthened vs single-agent prior.
- Scenario B: **1.12 [1.05, 1.18], confidence 0.83**
- Scenario C: **1.00 [0.93, 1.06], confidence 0.81** — dissent flagged: 2 of 5 agents below 1.0; weight share 0.34 → promoted to primary orchestrator.

Primary orchestrator action: flag to human that Scenario C's DSCR is ambiguous around the 1.0 threshold and request approval before proceeding with that scenario.

## Diagram reference

- **D06 (Consensus aggregation)** — fan-in + cluster + interval derivation.

## One-line summary

> Weight each signal by source calibration, verifier result, cross-agent agreement, and BS flags. Cluster answers semantically. Report intervals and preserve principled dissent. Classify every iteration as strengthened, revised, or unchanged-but-calibrated. Calibrate with Brier/ECE continuously.
