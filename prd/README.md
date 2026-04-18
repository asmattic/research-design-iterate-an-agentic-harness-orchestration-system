# PRD — Agentic Harness Orchestration System

**Version:** 0.1 (Round 1 — design foundation)
**Date:** 2026-04-18
**Status:** Draft for review
**Audience:** engineer-principals, systems architects, ML/AI infra leads

---

## Navigation

### Part I — Framing
- [00 · Preface](./00-preface.md)
- [01 · Executive Summary](./01-executive-summary.md)
- [02 · Intent, Goals, Non-Goals](./02-intent-goals.md)
- [03 · Problem Statement](./03-problem-statement.md)

### Part II — Theory & Research Foundations
- [04 · Conceptual Foundations](./04-conceptual-foundations.md)

### Part III — Architecture
- [05 · Architecture Overview](./05-architecture-overview.md)
- [06 · Core Components](./06-core-components.md)
- [07 · Communication Topology (Hub vs Mesh)](./07-communication-topology.md)
- [08 · Parallel vs Serial Decision Tree](./08-parallel-vs-serial.md)

### Part IV — Signal, Consensus, Verification
- [09 · Signal Weighting & Consensus](./09-signal-consensus.md)
- [10 · Memory Architecture](./10-memory-architecture.md)
- [11 · Drift Control & Intent Preservation](./11-drift-control.md)
- [12 · Guardrails](./12-guardrails.md)
- [13 · Feedback Loops](./13-feedback-loops.md)

### Part V — Evaluation
- [14 · Evaluation Framework](./14-evaluation.md)

### Part VI — Protocol & Adapters
- [15 · Harness-Agnostic Protocol Spec](./15-protocol-spec.md)
- [16 · Adapters — Claude Code, Codex, Cursor](./16-adapters.md)

### Part VII — Worked Examples
- [17 · Rental Acquisition (financial planning / legal / ops)](./17-worked-example-rental.md)
- [18 · Code Architecture (MetaGPT / ChatDev critique + redesign)](./18-worked-example-code-architecture.md)
- [19 · AI Research (Anthropic multi-agent system analysis)](./19-worked-example-ai-research.md)

### Part VIII — Risk & Roadmap
- [20 · Risks, Failure Modes, Mitigations](./20-risks-and-mitigations.md)
- [21 · Phased Roadmap](./21-roadmap.md)
- [22 · Open Questions](./22-open-questions.md)
- [23 · Next Report — Round 2 Spec](./23-next-report.md)

### Part IX — Appendices
- [A · Diagram Index](./appendices/A-diagram-index.md)
- [B · Glossary](./appendices/B-glossary.md)
- [C · Annotated Bibliography](./appendices/C-bibliography.md)
- [D · Protocol Schemas (JSON-Schema)](./appendices/D-schemas.md)
- [E · Proposed Skills (for Round 2 `/skill-creator`)](./appendices/E-proposed-skills.md)

---

## How to read this PRD

- **If you want the TL;DR** — read 01 and 05, skim the diagrams in `/diagrams/`.
- **If you're about to implement** — read 06, 07, 09, 15, 16, and 21 in order.
- **If you want the theoretical grounding** — read 03, 04, Appendix C.
- **If you want to port this to your own domain** — read 17–19, then write your own `INTENT.md` patterned on 02.

## Diagram bundle

11 Mermaid diagrams live at `/diagrams/`. Each one answers a single architectural question; see Appendix A for the question-to-diagram index.
