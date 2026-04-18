# 14 · Evaluation Framework

## The evaluation discipline, in one paragraph

A multi-agent system that cannot be measured cannot be improved. This chapter specifies what is measured (dimensions), where (at three cadences), how (deterministic gates + LLM-as-judge + calibration scoring), and how the measurements feed back into the system (§13).

The eval framework is the closing loop that makes the whole harness more than a pile of prompts — it is what lets us honestly report "this performed better than the previous configuration on this task set."

## 14.1 The measurement dimensions

Seven dimensions, each measured with a specific instrument.

| Dimension | Instrument | Target | Hard floor |
|---|---|---|---|
| **Completion** | INTENT success-criteria rubric | ≥ 90% | ≥ 75% |
| **Intent-alignment** | LLM-as-judge against INTENT | ≥ 0.90 | ≥ 0.75 |
| **Drift** | §11 composite score | ≤ 0.05 cosine | ≤ 0.15 |
| **Calibration** | Brier + ECE on testable claims | Brier ≤ 0.15, ECE ≤ 0.10 | 0.25 / 0.20 |
| **Cost** | Tokens, wall-clock, USD | ≤ 20× single-agent baseline | ≤ 30× |
| **Safety** | Adversarial-eval false-allow rate | ≤ 0.1% | ≤ 1% |
| **Human-gate compliance** | Fraction of irreversible actions that hit the gate | 100% | 100% |

Three of these (calibration, drift, safety) are quantitative and deterministic-adjacent. Four (completion, intent-alignment, cost, gate compliance) are a mix of deterministic and rubric-judged. No pure vibes-based metric.

## 14.2 The three cadences

Repeated from §13, specialized for eval:

### 14.2.1 Per-turn evals
- Verifier result on every testable claim (pass / fail / abstain).
- BS Detector flags (clean / over-confident / unsupported / hallucinated).
- Schema-validation on structured outputs.
- Guardrail pass/reject counts.

These flow into the Signal/Noise Attributor (§6.4.4) in real time and into the per-campaign aggregate at campaign end.

### 14.2.2 Per-task evals
- Completion against the task's INTENT subset.
- Cohort-level calibration (how well did this cohort's reported confidences match ground truth).
- Dissent analysis (was dissent well-grounded? Was suppressed minority correct?).
- Cost vs. single-agent baseline for this specific task.

These flow into the Retrospective (§13.2).

### 14.2.3 Per-campaign evals
- Drift arc over the campaign.
- Intent-alignment at end vs start.
- Cross-task comparison (is this campaign's cohort config better than the last?).
- Safety: adversarial eval pass rate.

These flow into the Eval Harness (§13.3), and from there into system configuration.

## 14.3 Deterministic gates vs rubric judges

The eval harness distinguishes:

### Deterministic gates
- Unit test pass/fail.
- Schema validation.
- Type check.
- Numeric bound check.
- Regex match.
- Citation-resolves check.

If a deterministic gate fails, the claim is *incorrect* — not "likely incorrect." This is the Lightman et al. process-supervision insight applied at eval time.

### Rubric judges
- Intent-alignment (LLM-as-judge with explicit rubric).
- Dissent quality (was dissent principled?).
- Completion (multi-criteria rubric from INTENT).

Rubric judges are calibrated against human judgments on a ground-truth set; their own calibration is tracked.

### Precedence rule (§02 hard constraint)
When deterministic and rubric disagree on a testable claim, deterministic wins. Rubrics don't override tests.

## 14.4 The benchmark sets

The eval harness runs against held-out benchmark sets per domain:

### Rental acquisition (worked example §17)
- 20 scenarios with ground-truth outcomes (did the deal cash-flow at the target rate? did the lease stand?).
- Synthetic variations injecting zoning changes, tax changes, market shifts.

### Code architecture (worked example §18)
- **SWE-bench Verified** subset *(Jimenez et al., 2024)* — real GitHub issues + tests.
- **Multi-file refactor** scenarios with objective pass/fail (migration completes without breaking tests).

### AI research (worked example §19)
- **GAIA** *(Mialon et al., 2023)* — General AI Assistants benchmark, research-task subset.
- **BrowseComp** *(OpenAI, 2025)* — browse-and-synthesize.
- Internal adversarial set for hallucination & citation fabrication.

### Safety
- Prompt-injection payload set (published + internally-curated).
- Adversarial drift-induction scenarios.
- Harmful-content bait set.

Benchmark scores are reported per dimension and compared across system-configuration changes. A regression on any safety metric blocks a release.

## 14.5 Evaluator implementations

### Verifier
Python process that loads a claim and tries to execute a test. For code claims: runs pytest; for SQL: runs the query against a fixture DB; for URL: HEADs the URL; for citation: fetches the citation and matches title; for numeric claim: runs the calculation independently.

### LLM-as-judge (intent-alignment, completion, dissent quality)
Prompted with INTENT + the artifact + a rubric. Returns JSON with score + justification. Scores calibrated against a human-labeled reference set (~100 artifacts).

### Calibration scorer
Takes a stream of (claim, agent_confidence, verifier_outcome) tuples and computes Brier + ECE. Python.

### Drift scorer
Embed INTENT, embed rolling context, compute cosine. LLM-judge on structured INTENT sub-criteria. Combine per §11.

### Cost scorer
Integrates the event log's token-count fields and adapter-provided dollar conversions.

## 14.6 Regression policy

A proposed configuration change (new cohort composition, new agent prompt, new swarm size) must pass:
- No regression on safety hard-floors.
- No regression > 5% on completion or intent-alignment.
- Cost regression acceptable if completion uplifts > 2× the cost delta.
- Calibration can regress only if completion improves materially.

These gates live in the Eval Harness config. Proposed changes that fail are rejected automatically; proposed changes that pass are promoted with a human sign-off.

## 14.7 Eval as a first-class product

The harness ships the eval framework as a *runnable product*, not documentation. Round 2 delivers:
- `evals/` package (Python) with: deterministic-gate runner, consensus aggregator, Brier/ECE calculator, drift detector, judge orchestrator.
- CLI: `harness eval run --benchmark <name> --config <path>`.
- CI hook: blocks merges that regress metrics.

## 14.8 Reporting

Per campaign, a `report.md` is generated in the campaign folder. Structure:

```
# Campaign <id> report
## Completion         [pass/partial/fail] — criteria breakdown
## Intent-alignment   0.XX — rubric breakdown
## Drift              max 0.XX, final 0.XX — arc
## Calibration        Brier 0.XX, ECE 0.XX — per-cohort
## Cost               tokens, wall-clock, USD
## Safety             adversarial pass rate
## Human gates        N triggered, N approved, N rejected
## Retrospective notes (proposals for agent prompts, weights, memory)
```

This is the single artifact the human principal reads at campaign end. All of its claims are traceable to the event log.

## Diagram reference

- **D11 (Eval cadences)** — the concentric per-turn / per-task / per-campaign loops with arrow back into configuration.

## One-line summary

> Seven dimensions, three cadences, deterministic gates > rubric judges on testable claims, benchmark sets per domain, and a regression policy that gates configuration changes. Eval is shipped as a product, not described.
