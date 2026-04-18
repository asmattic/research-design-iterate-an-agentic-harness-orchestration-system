# 10 · Memory Architecture

## The problem

Long-horizon campaigns produce volumes of state that can neither fit in a single LLM context nor be thrown away. The wrong answer is to either (a) stuff everything into every call (context rot, cost explosion) or (b) rely on the LLM to remember across calls (it won't).

The right answer is a **tiered, explicitly-loaded, policy-tagged memory substrate** with a thin memory index that the orchestrator consults to decide what to load.

## 10.1 The four tiers

| Tier | Medium | Lifespan | Latency | Purpose | Typical size |
|---|---|---|---|---|---|
| **L0 Working** | Agent's own prompt | Single turn | 0ms (in-context) | Immediate scratchpad | ≤ 8K tokens |
| **L1 Hot** | In-memory KV + small SQLite | Campaign | ~10ms | Last N turns, active plan, packet stream | ≤ 100MB |
| **L2 Indexed** | Vector DB + SQL + filesystem | Months–years | ~50–200ms | Cross-campaign memory, retrospective-sourced learnings, citation cache | GB scale |
| **L3 Cold** | Filesystem archive, event log | Indefinite | seconds | Full raw history, audit trail | Unbounded |

**Why four, not three.** L0 and L1 are distinct because L0 is the agent's own prompt and L1 is shared across agents. L2 and L3 are distinct because L2 is query-indexed (you can ask for relevant content) and L3 is archive (you need to know what you're looking for).

## 10.2 The memory index

Memory is loaded through an **index**, not by globbing the filesystem. The index is itself a structured document (markdown + JSON front-matter):

```yaml
---
memory_id: mem_20260401_rental_tampa_zoning
tier: L2
scope: campaign
domain: legal / zoning
sensitivity: public        # public | internal | pii | secret
freshness: 2026-04-01
confidence: 0.85
source: florida-zoning-board-pdf-2025
contributing_agents: [legal_zoning_expert, legal_adversary]
supersedes: mem_20251015_rental_tampa_zoning
---

## Summary
Hillsborough County zoning ordinance 2.5.3 permits short-term rentals in R-1 residential zones with…
```

Agents query the index with semantic queries + structured filters (`scope=campaign`, `sensitivity≤internal`). The index returns a handful of top-K candidates; the agent (or context manager) decides which to load.

## 10.3 Retrieval patterns

### Pattern A: Primary orchestrator wants campaign status
- Query: "latest packets, drift status, budget" from L1.
- No semantic search; direct KV read.

### Pattern B: Cohort needs prior learnings for a task
- Query: L2 semantic search scoped to the cohort's domain.
- Filter by `freshness > campaign_start - 180d` unless no recent hit.

### Pattern C: Retrospective wants the raw history
- L3 event-log scan, by campaign_id.
- Streaming read — never loaded into any agent's context, only into the retrospective pipeline.

### Pattern D: Audit or replay
- L3 event log by campaign_id + timestamp range.
- Read-only; never mutated.

## 10.4 Write patterns

Each tier has explicit write rules:

**L0** — written by the agent at emission time, discarded at end of turn.

**L1** — written by the Orchestrator System (not directly by experts). Cohort sub-orchestrators emit packets; the OS writes them to L1.

**L2** — written by:
- Retrospective agent (per-task): promotes campaign learnings to cross-campaign L2 with `confidence`, `supersedes`.
- Context manager: caches expensive retrieval results (citations, primary sources) into L2 for reuse.

**L3** — written by the event log. Every agent emission, every tool call, every orchestrator decision, every verifier result is appended. Never mutated. Never deleted (subject to retention policy).

## 10.5 Privacy and sensitivity tagging

Every memory entry has a `sensitivity` tag:

| Tag | Meaning | Behavior |
|---|---|---|
| `public` | Widely known, no concern | Loadable by any agent |
| `internal` | Organization-private | Loadable only within campaign |
| `pii` | Contains personal data | Loadable only with explicit campaign permission; redacted in summaries to primary orchestrator unless exception granted |
| `secret` | Credentials, tokens, financial account identifiers | Never loaded into any LLM context; only referenced by ID; materialized only in verifier/tool calls that need them |

The Context Manager (§6.4.1) enforces these rules at load time.

**Mitigates.** F7 (prompt-injection-driven credential leak).

## 10.6 Eviction and retention

- **L0** — turn boundary.
- **L1** — campaign end (moved to L3 archive).
- **L2** — never evicted, but entries can be *superseded*. Superseded entries remain retrievable but are ranked below current entries. This is critical for retrospectives ("what did we believe last quarter?").
- **L3** — retention policy configured per-deployment (default: 2 years). Never auto-deleted mid-retention.

## 10.7 The "memory index as first-class document" pattern

The rental toolkit's innovation — markdown files as both memory and as prompts — generalizes here. The memory index:

- Is human-readable. A principal can open it and understand what the system "knows."
- Is agent-readable. It's queryable by semantic + structured filters.
- Is version-controlled. Git is the natural substrate; writes go through commits.
- Is diff-able. Retrospective changes appear as diffs, which the human ratifies.

This is the same discipline as §02 INTENT — immutable unless explicitly ratified — but applied to accumulated knowledge rather than campaign goal.

## 10.8 Minimum viable implementation (Round 2)

To keep the bar low for bootstrap:

- **L0**: inherent in the LLM call.
- **L1**: SQLite + a `packets/` directory in the campaign folder.
- **L2**: SQLite with FTS5 for text, optional Chroma/LanceDB for vectors. Markdown files for the index itself.
- **L3**: JSONL event log on disk; one file per campaign.

No Weaviate, no Pinecone, no Redis cluster required. The protocol allows those; Round 2 does not require them.

## 10.9 Scaling path (Round 3+)

If L2 volume or query load grows:

- Swap SQLite-FTS5 for a managed vector DB (Chroma → Qdrant → Pinecone).
- Swap local KV for Redis.
- Keep the index schema; swap only the storage.

The point of the index is that its schema decouples the agent layer from the storage layer. Storage evolves; agents don't care.

## Diagram reference

- **D07 (Memory tiers)** — the four-tier stack with read/write arrows.

## One-line summary

> Four tiers (L0 working / L1 hot / L2 indexed / L3 cold), all loaded via a single structured memory index with explicit privacy tagging and supersession, so the primary orchestrator always sees the right slice and never the whole pile.
