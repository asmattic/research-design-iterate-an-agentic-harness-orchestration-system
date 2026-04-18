---
name: Agentic Harness Orchestration System — long-term project
description: Multi-round design effort. Round 1 (PRD v0.1.0) complete; Round 2 is reference scaffolding + eval harness prototype. Architecture decisions and terminology are load-bearing across rounds.
type: project
originSessionId: dee45bae-57e2-4eaf-80fe-fea93aa03fed
---
**Status (as of 2026-04-18):** Round 1 complete. PRD v0.1.0 shipped — 25 chapters + 5 appendices + 11 Mermaid diagrams + Next.js 16 docs site. Harness protocol version 0.1.0.

**Round 2 scope (deferred, per §23 of the PRD):** Reference scaffolding (templates + drift_check.py + retrospective.py + consensus.py + memory_index.py + event_log.py), Orchestrator System Python package, deterministic verifier, eval harness prototype, Claude Code adapter, partial rental-toolkit port. Schemas finalize from v0.1.0 → v0.2.0 in this round. Target: 3–5 weeks.

**Round 3+:** multi-adapter (Codex CLI, Cursor) + benchmark integration (SWE-bench Verified, GAIA, BrowseComp, MINT). 6–10 weeks.

**Why this matters — load-bearing decisions:**
- *INTENT.md is immutable.* Only the human mutates it. Every feedback loop can propose diffs against prompts/weights/memory but never against INTENT. Do not propose designs that have the harness self-modify its goal.
- *Hub topology is the default*, mesh is bounded via caucus only. The Redux/Zustand analogy in §07 is the framing. Don't propose peer-chat as a first-class pattern.
- *Deterministic verifier takes precedence over any LLM opinion.* This is a hard constraint in §02, not a preference.
- *Three-valued consensus outcome:* strengthened / revised / unchanged-but-calibrated. Never a silent overwrite. Threaded through §9, §13, §15 schemas.
- *Eight failure modes F1–F8* are the design spine. New features should map to which F* they mitigate.
- *15–20× cost ceiling* is an explicitly accepted trade-off vs single-agent (Anthropic MARS precedent: +90.2% quality at ~15× cost).

**How to apply:** When the user asks for Round 2 work (scaffolding, eval harness, adapter code) or revisions to the PRD, treat the above as settled. Terminology in Appendix B is canonical — use those exact terms (packet, caucus, cohort, orchestrator system, drift, etc.). Before recommending a file or function name, verify it exists — repo state may have advanced.
