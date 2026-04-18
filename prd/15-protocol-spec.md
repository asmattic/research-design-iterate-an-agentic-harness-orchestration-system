# 15 · Harness-Agnostic Protocol Spec

## Why a protocol

Three runtimes (Claude Code, Codex CLI, Cursor) and more coming. A harness-specific design locks in a vendor; a protocol + adapters does not. The protocol cost is roughly 10% of the total code surface vs 70% for a port later (§03).

The protocol specifies **five schemas** and **one event type**. The adapter layer (§16) maps each to runtime primitives.

## 15.1 The five schemas, at a glance

| # | Schema | Purpose | Written by | Read by |
|---|---|---|---|---|
| 1 | **Agent Contract** | Defines a specialist agent's inputs/outputs | Prompt author | Cohort sub-orchestrator, adapter |
| 2 | **Event Envelope** | Wraps every log entry | All emitters | Event log, retrospective, audit |
| 3 | **Consensus Packet** | Swarm output | Cohort aggregator | Orchestrator System, primary orchestrator |
| 4 | **Orchestrator State** | Campaign-level state snapshot | Primary orchestrator | Checkpointing, replay, human |
| 5 | **Memory Index** | Memory row metadata | Retrospective, cache | Context manager, any agent |

All five live as JSON-Schema in Appendix D. Their shapes are sketched here.

## 15.2 Agent Contract

```json
{
  "agent_id": "finance_budget_conservative_v2",
  "version": "2.1.0",
  "role": "budget analyst, conservative bias",
  "cohort": "finance",
  "model_family": "claude-opus-class",
  "temperature": 0.2,
  "system_prompt_ref": "prompts/finance/budget_conservative.md",
  "tools": ["calculator", "mortgage_amortizer", "comps_lookup"],
  "input_schema": { "$ref": "#/schemas/FinanceBudgetInput" },
  "output_schema": { "$ref": "#/schemas/FinanceBudgetOutput" },
  "calibration": {
    "brier_rolling": 0.11,
    "brier_sample_size": 87,
    "last_updated": "2026-04-10T12:00:00Z"
  },
  "guardrails": ["numeric_bounds", "citation_required"],
  "constitution_ref": "constitutions/finance.md"
}
```

**Input schema** declares what the cohort passes to this expert. **Output schema** declares what the expert returns (headline values, confidence, sources, notes). Both are JSON-Schema — structured for machine consumption, typed for validation.

**Mitigates.** F3 (compounding error — contract catches malformed emissions), F5 (unverifiable claims — schema requires confidence + sources fields).

## 15.3 Event Envelope

Every emission (agent output, tool call, orchestrator decision, verifier result, drift check, human approval) wraps in this envelope:

```json
{
  "event_id": "evt_01JG…",
  "campaign_id": "camp_2026_04_tampa",
  "task_id": "task_underwriting_01",
  "parent_event_id": "evt_01JG…",
  "t": "2026-04-18T09:42:17.123Z",
  "emitter": {
    "kind": "agent | tool | orchestrator | verifier | guardrail | human",
    "id": "finance_budget_conservative_v2",
    "adapter": "claude_code"
  },
  "kind": "emission | tool_call | tool_result | decision | verifier_result | drift_check | approval_request | approval_decision",
  "payload": { "...": "..." },
  "refs": {
    "memory_refs": ["mem_..."],
    "contract_ref": "agents/finance/budget_conservative.json",
    "prior_packet_ref": null
  },
  "cost": { "tokens_in": 1023, "tokens_out": 486, "wall_clock_ms": 1842 },
  "flags": ["bs_clean", "verifier_abstain", "guardrail_pass"]
}
```

The event log is **append-only**. No mutation. No deletion (retention policy aside). Replay of the log reconstructs the campaign state exactly.

## 15.4 Consensus Packet

Shape sketched in §9.6. Full schema in Appendix D. The three critical fields:
- `outcome_type` enum: `strengthened | revised | unchanged_but_calibrated`.
- `consensus` with interval and confidence.
- `dissent[]` preserving minority positions with weight share ≥ 15%.

## 15.5 Orchestrator State

```json
{
  "campaign_id": "camp_2026_04_tampa",
  "started_at": "2026-04-15T14:00:00Z",
  "intent_ref": "campaigns/tampa/INTENT.md",
  "intent_hash": "sha256:...",
  "plan": { "steps": [ ... ], "current_step": 4 },
  "active_cohorts": ["finance", "legal"],
  "budget": { "tokens_used": 847000, "tokens_budget": 2000000, "usd_used": 8.40 },
  "drift": { "signal_a": 0.04, "signal_b": 92, "last_checked": "…" },
  "pending_approvals": [ ... ],
  "recent_packets": [ ... ],
  "memory_load_refs": [ "mem_…", "mem_…" ]
}
```

The state is snapshotted at every primary-orchestrator turn. The latest snapshot is what the primary orchestrator actually reads as its context (§6.3) — it *is* the primary orchestrator's memory.

## 15.6 Memory Index entry

```yaml
---
memory_id: mem_20260401_rental_tampa_zoning
tier: L2
scope: campaign | cross_campaign | organization
domain: legal
subdomain: zoning
sensitivity: public | internal | pii | secret
freshness: 2026-04-01
expires: null | 2026-12-31
confidence: 0.85
source: florida-zoning-board-pdf-2025
contributing_agents: [legal_zoning_expert]
supersedes: mem_20251015_rental_tampa_zoning
tags: [tampa, short-term-rental, r1-zoning]
---

## Summary
<prose>

## Key points
- <bullet>
- <bullet>

## Sources
- <citation with URL>
```

Markdown body is human-readable and agent-readable. YAML front-matter is the index row.

## 15.7 The one event type versus many event *kinds*

Design decision: **one envelope, many kinds.** Alternative was one schema per event kind. We chose one envelope because:
- Simpler event log (single append target, single query pattern).
- Easier replay tooling.
- Retrospectives can stream and filter by `kind` with one parse.

The `payload` field is polymorphic by `kind`. Each `kind` has its own `payload` schema (sub-schemas in Appendix D).

## 15.8 Versioning

Every schema carries a `version` field. The adapter layer is responsible for version translation (old envelopes loaded into a newer adapter remain readable). Breaking changes require a version bump; additive changes don't.

This matters because L3 event logs are retained for years. A new adapter must read old logs to run retrospective comparisons across versions.

## 15.9 Serialization

All schemas serialize as JSON, with YAML allowed for human-authored files (memory index entries, contracts) and round-tripped to JSON for agent I/O. No custom binary formats. The event log is JSONL.

## 15.10 Error model

Every adapter must emit a structured error in the Event Envelope when an expected emission fails:

```json
{
  "kind": "emission",
  "payload": {
    "status": "error",
    "error_class": "schema_validation | timeout | tool_failure | guardrail_reject | budget_exceeded",
    "message": "...",
    "retriable": true
  }
}
```

The Orchestrator System reacts to errors by class — schema errors retry with schema diff; timeout errors escalate to the cohort; guardrail rejects require a corrective instruction to the agent; budget-exceeded pauses the campaign.

## 15.11 Compatibility check between adapters

A set of protocol conformance tests (part of the eval harness, §14.7) runs every adapter against:
- Emit and read back every schema.
- Replay a reference event log on every adapter.
- Match consensus packet output bit-for-bit given identical swarm inputs.

Conformance tests are the single gate for accepting a new adapter.

## 15.12 What the protocol deliberately does not specify

- **Transport.** Adapters choose (stdout/stdin, JSON-RPC, in-process, MCP, custom).
- **Runtime.** Python, Node, shell — adapter's choice.
- **Model family.** Each Agent Contract declares its own; the protocol doesn't mandate one.
- **Prompting style.** Agents are free to use CoT, ReAct, ToT, etc.; the contract constrains only the I/O.

The protocol is the narrow waist that makes portability cheap.

## Diagram reference

- **D03 (Hub topology)** already shows the protocol flow; additional detail lives in Appendix D schemas.

## One-line summary

> Five schemas (Agent Contract, Event Envelope, Consensus Packet, Orchestrator State, Memory Index) in JSON-Schema, with a versioned append-only event log as the ground truth. Adapters map protocol to runtime; conformance tests gate adapter acceptance.
