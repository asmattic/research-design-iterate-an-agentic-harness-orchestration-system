# 05 · Architecture Overview

## The one-sentence version

**A clean-context Primary Orchestrator reads only pre-weighted, verified, drift-checked signals from an Orchestrator System, which sits between it and a tiered fleet of Cohort Sub-Orchestrators, each of which dispatches work to Expert Agents or Expert Swarms that produce confidence-interval outputs.**

## The layered picture

```
                          ┌──────────────────────┐
                          │   HUMAN PRINCIPAL    │
                          │  (intent owner,      │
                          │   approver of        │
                          │   irreversible acts) │
                          └──────────┬───────────┘
                                     │
                                     ▼
                          ┌──────────────────────┐
                          │   INTENT (immutable) │
                          │   anchor document    │
                          └──────────┬───────────┘
                                     │  continuous drift check
                                     ▼
                     ┌───────────────────────────────┐
                     │   PRIMARY ORCHESTRATOR        │
                     │   (clean context, thin,       │
                     │    strategic, intent-aligned) │
                     └───────────────┬───────────────┘
                                     │ reads packets from
                                     ▼
       ┌────────────────────────────────────────────────────────┐
       │             ORCHESTRATOR SYSTEM                        │
       │  ┌───────────┐  ┌────────────┐  ┌─────────────┐        │
       │  │  Context  │  │  BS        │  │  Validator  │        │
       │  │  Manager  │  │  Detector  │  │  / Verifier │        │
       │  └───────────┘  └────────────┘  └─────────────┘        │
       │  ┌────────────┐ ┌────────────┐  ┌─────────────┐        │
       │  │  Signal /  │ │   Weight   │  │  Drift      │        │
       │  │  Noise     │ │   Tweaker  │  │  Detector   │        │
       │  └────────────┘ └────────────┘  └─────────────┘        │
       └────────────────────────┬───────────────────────────────┘
                                │  routes validated tasks to
              ┌─────────────────┼─────────────────┬──────────────┐
              ▼                 ▼                 ▼              ▼
      ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────┐
      │  Cohort:     │  │  Cohort:     │  │  Cohort:     │  │ ... │
      │  Finance     │  │  Legal       │  │  Research    │  │     │
      │  sub-orch.   │  │  sub-orch.   │  │  sub-orch.   │  │     │
      └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └─────┘
             │                 │                 │
             ▼                 ▼                 ▼
     ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
     │  Experts /    │ │  Experts /    │ │  Experts /    │
     │  Swarms       │ │  Swarms       │ │  Swarms       │
     │  (MoA)        │ │  (MoA)        │ │  (MoA)        │
     └───────┬───────┘ └───────┬───────┘ └───────┬───────┘
             │                 │                 │
             ▼                 ▼                 ▼
       ┌─────────────────────────────────────────┐
       │         DETERMINISTIC VERIFIER          │
       │     (tests, type checks, lookups)       │
       └─────────────────────────────────────────┘
             ▲                                      ▲
             │                                      │
             │        ┌──────────────────┐          │
             └────────┤  TIERED MEMORY   ├──────────┘
                      │  L0 working      │
                      │  L1 hot (KV)     │
                      │  L2 indexed      │
                      │  L3 cold archive │
                      └──────────────────┘
```

The corresponding Mermaid version is **D01 (System Layers)** in `/diagrams/`.

## The five roles, in one paragraph each

**Primary Orchestrator.** The thin, strategic layer that the human talks to and that executes against INTENT. Its context contains only INTENT, the campaign plan, and packets produced by the Orchestrator System. It does not hold raw expert transcripts, tool-call logs, or prior reasoning chains; those live one tier down. When the human asks "where are we?", this is who answers.

**Orchestrator System.** The middleware between the Primary Orchestrator and the cohort layer. It is a *system*, not one agent: six sub-responsibilities run in parallel (context manager, BS detector, validator/verifier, signal/noise attributor, weight tweaker, drift detector). It turns noisy multi-agent output into digestible packets and prevents garbage from propagating up. This is the layer most multi-agent frameworks lack, and it is the most novel contribution of this PRD.

**Cohort Sub-Orchestrators.** Domain-scoped managers. A finance cohort runs budget/underwriting/tax experts; a legal cohort runs contract/zoning/compliance experts; a research cohort runs literature/empirical/adversarial experts. Each cohort knows its domain's tools, its domain's ground-truth sources, and its domain's quality bar. The primary orchestrator delegates *domains*, not *tasks*, and the cohort decomposes.

**Expert Agents / Swarms.** The specialists that actually do the work. An expert can be a single agent (Vetter, Budget Analyst, Contract Reviewer) or a *swarm* — N agents of the same specialty with deliberately varied prompts, models, or retrieval views. Swarms emit confidence-interval consensus, not single-point verdicts.

**Deterministic Verifier.** A code-based arbitrator. Unit tests for code claims, type checks for schema claims, database lookups for factual claims, linters for style claims. Where a claim is testable, the verifier beats any LLM opinion. Where a claim isn't testable, the verifier abstains and the LLM-as-judge takes over (§09).

## The supporting substrates

- **Tiered Memory (§10)** — L0 working (ephemeral), L1 hot (KV/SQLite, last N turns of this campaign), L2 indexed (vector + SQL, cross-campaign), L3 cold (filesystem archive, event log).
- **Event Log (§15)** — append-only record of every agent emission, tool call, orchestrator decision, verifier result, drift check. The ground truth for retrospectives and audits.
- **Guardrails (§12)** — layered policy / safety / quality / privacy checks at every boundary.
- **Feedback Loops (§13)** — Reflexion per-turn, retrospective per-task, eval-harness per-campaign.
- **Eval Harness (§14)** — drift, calibration, cost, latency, completion, safety — computed continuously and summarized per campaign.

## What is novel vs what is borrowed

**Borrowed from published work:**
- Orchestrator-subagent pattern: Anthropic MARS, AutoGen, MetaGPT.
- Confidence aggregation over multiple samples: Self-Consistency, MoA.
- Reflection-as-memory: Reflexion, Self-Refine.
- Process supervision: Lightman et al.
- Context curation: Anthropic context-engineering posts, Liu et al.

**Novel emphasis in this PRD (not novel in isolation — novel in combination):**
- The **Orchestrator System** as its own named layer with six explicit sub-responsibilities (§06).
- The **three-valued consensus output** — *strengthened / revised / unchanged-but-calibrated* — as an output contract, not a UI concept (§09).
- **Drift as a first-class continuously-measured metric**, not a retrospective observation (§11).
- **Harness-agnostic protocol with thin adapters** for Claude Code / Codex / Cursor (§15, §16).
- **INTENT.md as an immutable campaign anchor** that every agent is checked against (§02, §11). This is generalized from the rental toolkit's pattern.

## How to read the rest of Part III

- **§06** — details each component, especially the Orchestrator System's six sub-responsibilities.
- **§07** — answers the hub vs mesh question explicitly, with a Redux/Zustand analogue the engineer-principal will recognize.
- **§08** — the decision tree for when to go parallel, when to go serial, when to go single-agent.
- **§09** — signal weighting, consensus aggregation, the three-valued output, Brier/ECE calibration.
