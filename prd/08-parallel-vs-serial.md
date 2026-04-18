# 08 · Parallel vs Serial — The Decision Tree

## The question

For a given task, should the harness:

- **A.** Run a single agent (single prompt, single LLM call, optionally with tool use)?
- **B.** Run a serial multi-agent chain (Agent A → Agent B → Agent C, each building on the prior)?
- **C.** Run parallel independent agents (N agents same task, aggregate)?
- **D.** Run a parallel swarm (N agents diverse-perspective, MoA-style consensus)?
- **E.** Run a bounded caucus (§07)?

The harness picks dynamically based on task characteristics. This chapter defines the decision rule.

## The decision tree, in plain words

1. Is the task narrow (one claim, one deliverable, narrowly scoped) AND verifier-testable AND cost-sensitive?
   → **A. Single agent.**
2. Is the task a sequence of dependent transformations where each step consumes the prior step's output?
   → **B. Serial chain**, but only if each step can be verifier-checked before the next step runs. Otherwise go to (3) or (4) to avoid F3.
3. Is the task independent-parallelizable — e.g., "research the legal framework in each of these 5 counties"?
   → **C. Parallel independent agents**, fan-out to the cohort, fan-in via aggregator.
4. Is the task subjective, high-stakes, or benefits from perspective diversity?
   → **D. Parallel swarm** (MoA), with deliberate specialization axes.
5. Does the task require real-time adversarial iteration between experts?
   → **E. Caucus**, bounded per §07.

## The decision tree, as a table

| Task shape | Verifier-testable? | High stakes? | Benefits from perspective diversity? | Needs real-time iteration? | Choice |
|---|---|---|---|---|---|
| Extract a number from a PDF | Y | any | N | N | **A. Single** |
| "Is this lease standard?" | N (semi) | Y | Y | N | **D. Swarm** |
| "Compute DSCR from these financials" | Y | Y | N | N | **A. Single** + Verifier |
| "Research X in counties A,B,C,D,E" | partial | any | N | N | **C. Parallel independent** |
| "Migrate legacy code from X to Y" | Y | Y | N | Y | **B. Serial chain** with per-step verify |
| "Evaluate zoning-code permissibility" | N | Y | Y | N | **D. Swarm** |
| "Build a consensus investment memo" | partial | Y | Y | partial | **D. Swarm** → summarize |
| "Debate: short-term vs long-term rental" | N | Y | Y | Y | **E. Caucus** (2 experts + judge) |
| "Write and critique a PRD section" | partial | Y | Y | Y | **E. Caucus** (author ↔ critic) |

## Cost-complexity ordering

Rough token-cost rule of thumb, relative to single-agent baseline:

| Choice | Token cost | Latency | When it pays back |
|---|---|---|---|
| A. Single | 1× | 1× | Always, when it fits |
| B. Serial (3-stage) | ~3× | ~3× | When sequential dependencies are real and each stage is verifiable |
| C. Parallel N=5 | ~5× | ~1× (wall-clock) | When fan-out is independent and aggregation is cheap |
| D. Swarm N=5 | ~7–10× (incl. aggregator) | ~2× | When task value ≥ ~10× single-cost |
| E. Caucus (6 turns, 2 agents + judge) | ~15–20× | ~3× | When real-time iteration is the point |

Anthropic's measured 15× cost for multi-agent research is in the D/E range for complex research tasks; that matches expectation.

## Fan-out / fan-in pattern

For C and D, the dispatch-and-aggregate pattern is:

```
Cohort receives task T
  ├─ Expert 1 ─► emission_1 ─┐
  ├─ Expert 2 ─► emission_2 ─┤
  ├─ Expert 3 ─► emission_3 ─┼─► Consensus Aggregator (§09) ─► Packet
  ├─ Expert 4 ─► emission_4 ─┤
  └─ Expert 5 ─► emission_5 ─┘
```

Each emission is independently validated by the Orchestrator System's verifier/BS-detector. Aggregation happens after validation, not before — verifier-failed emissions are excluded or down-weighted.

## Parallelism bounds (to prevent F6)

The Orchestrator System enforces these ceilings unless INTENT explicitly raises them:

| Bound | Default | Hard cap |
|---|---|---|
| Max swarm size (N agents same task) | 5 | 12 |
| Max cohorts active concurrently | 3 | 6 |
| Max experts per cohort active concurrently | 4 | 10 |
| Max caucus turns | 6 | 12 |
| Max tokens per task | 200K | 1M |
| Max wall-clock per task | 10 min | 60 min |

These defaults are conservative. The retrospective (§13) tunes them per campaign.

## When serial beats parallel — a note

Parallel is the right default for research and judgment. Serial is the right default for **transformations with real dependencies**: code migration (analyze → refactor → test → review), document editing (outline → draft → revise), or sequential optimizations. The marker: *does stage N+1 genuinely need stage N's output to exist?* If yes, serial. If no, parallel.

Naïve serial chains are where F3 (compounding error) lives. Every serial step must either (a) be verifier-checked before the next step runs, or (b) be promoted to a caucus where the downstream agent can push back on the upstream. Unchecked serial chains are the #1 cause of "the output looks great but is subtly wrong" failures.

## Adaptive scaling — a nuance

The Orchestrator System observes the task and may *scale swarm size dynamically*:

- Start with N = 3. Aggregate. If confidence interval is tight and consensus is clear → return early.
- If confidence interval is wide or dissent is principled → scale to N = 5 or N = 8 and re-aggregate.
- If still wide after N = 8 → surface to human as "ambiguous question, swarm cannot resolve."

This avoids paying for 8 experts when 3 are sufficient. Anthropic's MARS applies similar complexity-aware scaling *(Anthropic, 2025)*.

## Diagram reference

- **D05 (Dispatch decision tree)** — the flowchart version of this chapter.

## One-line summary

> Default to single-agent; use parallel swarms when diversity matters or stakes demand it; use serial only when stages genuinely depend on each other, and verify at every hop.
