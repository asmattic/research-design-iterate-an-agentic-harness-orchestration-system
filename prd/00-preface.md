# 00 · Preface

## What this document is

A Product Requirements Document for a **generalized agentic harness orchestration system** — a framework for running long-horizon, multi-agent AI workflows that stay anchored to intent, produce high-signal outputs, and remain auditable, verifiable, and maintainable.

The PRD specifies:

1. A **harness-agnostic protocol** (agent contracts, event envelopes, consensus packets, orchestrator state, memory index) that can be implemented on top of Claude Code, Codex CLI, Cursor, or any future agent runtime.
2. A **reference architecture** — primary orchestrator, orchestrator system (BS-detector / validator / signal-attributor / weight-tweaker / drift-detector), cohort sub-orchestrators, expert agents, expert swarms with Mixture-of-Experts semantics, a tiered memory substrate, and a deterministic verifier layer.
3. A **research plan and phased roadmap** for implementation, evaluation, and iteration.
4. Three **worked examples** that prove generality: rental-acquisition (financial / legal / ops), open-source code architecture (MetaGPT and ChatDev as instructive cases and their flaws), and AI agentic-harness research itself (Anthropic's multi-agent research system deconstructed).

## What this document is not

- It is not a working implementation. Round 2 delivers reference scaffolding and an eval-harness prototype; this Round 1 PRD specifies what those must do.
- It is not a research survey. Citations are load-bearing — each one justifies a specific design decision. For a broader literature review, see Appendix C.
- It is not locked to a single vendor's runtime. The entire point of §16 is that the same protocol can be adapted to Claude Code, Codex, Cursor, or whatever comes next.

## Relationship to the prior-art rental toolkit

The author's Tampa rental-acquisition toolkit (included in the project as `.projects/…`) is treated here as a **working proof-of-concept** of many of the patterns this PRD generalizes: `INTENT.md` as immutable root of goal, `drift_check.py` as a continuous consistency guard, per-agent learnings sections that retrospectives append to, structured-JSON inter-agent contracts, parallel vetter fan-out with internal concurrency, serialization at the human-approval boundary, and event-logged campaign history.

Where this PRD goes beyond that toolkit:

| Rental toolkit (current) | This PRD (generalized) |
|---|---|
| Single specialist agents (`vetter`, `legal`, `budget`) | Expert **swarms** with confidence-interval consensus |
| Orchestrator dispatches; implicit BS-checking | Explicit **Orchestrator System** (BS detector, signal/noise attributor, weight-tweaker, drift detector) |
| Flat agent roster (one cohort) | **Cohort** hierarchy (domain → sub-orchestrator → swarm) |
| Rental-only (Florida Ch. 83, HCPA/Clerk lookups) | Domain-agnostic with rental as one worked example |
| One runtime (Claude Code) | Three runtimes (Claude Code / Codex / Cursor) via adapter layer |
| Single-run eval (did the lease get signed?) | Per-turn, per-task, and per-campaign eval cadences; calibration scoring |
| Memory = markdown files + XLSX | **Tiered memory**: working / hot / indexed / cold archive |

## How we chose what to include

Every concept in this PRD earns its place by being either (a) explicitly named in the original request, (b) load-bearing for a design decision this PRD has to make, or (c) directly supported by published research whose conclusion justifies a specific architectural choice. See §04 for the ~15-paper grounding; each paper cited is one design decision defended.

## Versioning

- **0.1 — 2026-04-18** — initial draft, Round 1. Architecture, research plan, three worked examples, diagrams, schemas skeleton, roadmap.
- **Planned 0.2 — Round 2** — schemas finalized, reference scaffolding built, Claude Code adapter working, eval harness prototype runs.
- **Planned 1.0** — after Phase-3 roadmap items land and the system has run a full campaign end-to-end on a real task.
