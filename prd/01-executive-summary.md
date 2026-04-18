# 01 · Executive Summary

## The problem

Naïve multi-agent AI systems fail at long-horizon tasks. They drift from their original goal, compound errors across hops, produce unverified stochastic outputs, mistake local agreement for global correctness, and grow unboundedly expensive in context and tokens. Single-agent systems hit context-window ceilings and lack specialist depth. The industry is rapidly converging on multi-agent designs — Anthropic's multi-agent research system outperforms its single-agent baseline by **+90.2%** on internal research evals — but the design space is wide open and the failure modes are real.

## The thesis

A well-designed orchestration harness is one that treats **intent preservation**, **signal weighting**, and **deterministic verification** as first-class concerns alongside the specialist-LLM work. The architecture is a **state-tree** (hub), not a mesh: agents report through mediated channels; unmediated peer chat compounds drift and error. Specialists run in **swarms** of similar persuasion (Mixture-of-Experts style) to produce confidence-interval consensus, not single-point verdicts. A **thin, clean-context primary orchestrator** reads only pre-weighted, pre-verified, drift-checked signals from an **Orchestrator System** that sits between it and the expert layer.

## The design, one paragraph

A **primary orchestrator** holds only the highest-signal context strictly related to the campaign's purpose. Below it, an **Orchestrator System** does the dirty work — context management, BS detection, validation, signal/noise attribution, weight tweaking based on historical calibration, and drift detection against the INTENT anchor. Below that, **cohort sub-orchestrators** route domain-scoped work (legal cohort, finance cohort, security cohort, …) to **expert agents** — individuals or same-specialty **swarms** that produce confidence-interval outputs. A **deterministic verifier** arbitrates code-testable claims. A **tiered memory substrate** (working / hot / indexed / cold) keeps long-horizon state retrievable without bloating primary-orchestrator context. Feedback loops operate on three cadences: per-turn (Reflexion), per-task (retrospective → agent-prompt updates), per-campaign (eval harness → whole-run iteration). Guardrails enforce policy, safety, quality, and privacy at every layer. Human approval is the mandatory serialization point for irreversible actions.

## The five non-negotiables

1. **INTENT is immutable during a campaign.** Only the human principal mutates it. Every action must map to it. Drift against it is measured continuously.
2. **The primary orchestrator's context is protected.** Only indexed, weighted, verified, drift-checked signals reach it. No raw expert-agent transcripts.
3. **Stochastic outputs are paired with deterministic checks wherever possible.** Code-testable claims go to the verifier before they count.
4. **Confidence intervals, not single verdicts.** Swarms report a distribution; dissent is preserved; the orchestrator sees both consensus and minority voice.
5. **Feedback can strengthen a conclusion, not only change it.** A three-valued consensus outcome — *strengthened*, *revised*, *unchanged-but-calibrated* — is the output contract.

## The five portability commitments

1. The protocol (contracts + schemas) is independent of any runtime.
2. A thin adapter maps protocol → runtime primitives for each of Claude Code, Codex CLI, and Cursor.
3. Memory, event log, and eval harness run as standalone services or filesystem artifacts — not baked into any one runtime.
4. Agent prompts are plain markdown with structured I/O contracts; they port by copy.
5. Deterministic verifier tools are ordinary code invoked over stdin/stdout or JSON-RPC — runnable anywhere.

## What ships in Round 1 (this doc)

- Full PRD (this repository of markdown files)
- 11 Mermaid diagrams covering the full architecture
- Annotated research bibliography (~15 sources, each justifying a design choice)
- Protocol schema skeleton (JSON-Schema)
- Three worked examples
- Phased implementation roadmap
- Explicit spec for Round 2's deliverables

## What ships in Round 2 (next report)

- Protocol schemas finalized (versioned)
- Reference scaffolding (`INTENT.md`, `ORCHESTRATOR.md`, `AGENTS.md`, `COHORT.md`, `SWARM.md` templates + `drift_check.py` generalized)
- Eval-harness prototype (Python): deterministic-gate runner, consensus aggregator with confidence intervals, Brier/ECE calibrator, drift detector
- Claude Code adapter as reference implementation
- Rental-toolkit ported onto the new scaffolding

## The measurable promise

By Round 3, a task that currently takes 40 hours of focused human-in-the-loop direction with a single-agent harness will complete in under 4 hours of bounded human attention with this harness, with:

- **≥90%** intent-alignment at campaign end (measured by retrospective rubric)
- **≤5%** drift in orchestrator context relative to INTENT (measured by semantic distance)
- **Calibrated confidences** (Brier score ≤ 0.15) on every claim the verifier can test
- **100%** of irreversible actions gated by human approval
- **Zero** prompt-injection-driven goal substitutions (measured by adversarial eval)

These are the targets the eval harness is built to measure against.
