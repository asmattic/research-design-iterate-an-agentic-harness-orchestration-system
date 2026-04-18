# 02 · Intent, Goals, Non-Goals

*This document is patterned directly on the author's rental-toolkit `INTENT.md`. Every downstream section in the PRD defers to this one.*

---

## Goal

**Design, specify, and roadmap a harness-agnostic agentic orchestration system that enables long-horizon, multi-specialist AI workflows to complete reliably, verifiably, and without intent drift — portable across Claude Code, Codex CLI, and Cursor.**

## Success criteria (for the PRD itself — measurable)

| Criterion | Target | Hard floor |
|---|---|---|
| Coverage of original requirements | 100% of the concept list named in the request | 100% |
| Research citations directly justifying a design decision | ≥ 15 | ≥ 10 |
| Worked examples spanning domains | 3 (financial/legal/ops, code architecture, AI research itself) | 2 |
| Mermaid diagrams | 11 (one per architectural question) | 8 |
| Protocol schemas specified | Agent Contract, Event Envelope, Consensus Packet, Orchestrator State, Memory Index | all 5 |
| Adapters specified for | Claude Code, Codex CLI, Cursor | all 3 |
| Eval-framework cadences defined | per-turn, per-task, per-campaign | all 3 |

## Success criteria (for the harness, once implemented — also measurable)

| Criterion | Target | Hard floor |
|---|---|---|
| Intent-alignment score at campaign end (rubric-judged, 0–1) | ≥ 0.90 | ≥ 0.75 |
| Semantic drift of primary orchestrator context vs INTENT | ≤ 0.05 cosine distance | ≤ 0.15 |
| Calibration (Brier score) on verifier-testable claims | ≤ 0.15 | ≤ 0.25 |
| Irreversible actions passing human-approval gate | 100% | 100% |
| Prompt-injection-driven goal substitutions (adversarial eval) | 0 | ≤ 1 per 1000 turns |
| Swarm-consensus confidence coverage (fraction within reported interval) | ≥ 90% | ≥ 80% |
| Campaign cost vs. single-agent baseline (same task) | ≤ 20× tokens, ≥ 2× completion rate | Anthropic's reported 15× cost with 1.9× completion is the reference point |

## Non-goals — explicitly excluded and should not be traded against the goal

- **A new agent framework from scratch.** This PRD layers *on top of* existing runtimes (Claude Code, Codex, Cursor) via a thin protocol + adapters. No bespoke runtime.
- **Lock-in to one vendor's primitives.** The protocol is portable by design; any section that looks vendor-specific lives in the adapter chapter (§16), not the architecture chapter (§§05–13).
- **Self-modifying orchestrator prompts during a campaign.** The retrospective agent proposes prompt updates; the human approves them between campaigns. No silent in-campaign prompt rewrites.
- **Unbounded autonomous peer chat between specialist agents.** The orchestrator mediates almost all cross-agent traffic. Bounded "caucus" exceptions are strictly scoped (§07).
- **Replacing the human.** The human approves irreversible actions. Always. This is a throughput tool, not an autonomy tool.
- **Ultra-low-cost operation.** Multi-agent systems cost more. The point is higher-value outcomes per unit human attention, not cheapest tokens per answer.
- **Perfect determinism.** LLMs are stochastic; we accept that and pair them with deterministic checks where possible (§§06, 14). We do not pretend to eliminate stochasticity.
- **Replacing dedicated ML infra.** Tiered memory is designed to run on filesystem + SQLite + optional vector DB for Round 2. Replacing that with Weaviate / Pinecone / etc. is a configuration choice, not a PRD requirement.

## Hard constraints

- **Intent preservation is the top-priority invariant.** Any design choice that trades intent-alignment for other metrics must be explicitly called out and justified in the risks section (§20).
- **Irreversible actions require human approval.** Money movement, external messaging, signing, publishing, code execution against production, data deletion — always gated. The primary orchestrator does not have permission to bypass this even when confident.
- **Privacy: sensitive data is scoped in memory.** PII / secrets / financial figures / health data are tagged in the memory index and redacted from any context loaded into the primary orchestrator unless the memory index explicitly allows it for that campaign.
- **No silent goal mutation.** Retrospectives propose INTENT-adjacent changes in a diff file; the human ratifies. An agent cannot rewrite INTENT.
- **No network side-effects from expert agents without human approval.** Reading is fine; sending is gated.
- **Deterministic verifier outputs take precedence over LLM opinions when they disagree.** A passing test beats a confident claim.

## What "done" looks like for this project

1. The PRD (this document) is reviewed, revised, approved. ← *Round 1 end-state.*
2. Protocol schemas are versioned and committed. Reference scaffolding exists. Eval-harness prototype runs locally. ← *Round 2 end-state.*
3. One full campaign runs end-to-end on each of three harnesses (CC/Codex/Cursor) against a held-out task set, with metrics matching or beating the targets above. ← *Round 3 end-state.*
4. The author's rental toolkit is re-implemented on top of this scaffolding; the new version matches or improves on the current one's task-completion performance. ← *Round 3 confirmation.*

## Decision framework when something isn't specified

Applies to both the human reading this and any agent operating under it:

1. **Does the choice advance the goal?** If no, don't.
2. **Does it violate a hard constraint?** If yes, don't.
3. **Does it trade the goal for a non-goal?** If yes, flag it; don't silently take it.
4. **Is it reversible?** Prefer reversible. Irreversible changes to INTENT, to approved roadmap items, or to campaign artifacts need explicit re-approval.
5. **What would a 30-day retrospective write?** If the retrospective would call it a mistake, reconsider now.

## What changes this file

Only the human principal changes this file. Proposed changes land as a pending diff in `HANDOFF.md` (or its generalized equivalent) for explicit ratification. Agents do not silently mutate intent.
