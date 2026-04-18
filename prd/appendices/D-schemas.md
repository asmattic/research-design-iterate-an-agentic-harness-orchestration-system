# Appendix D · Protocol Schemas (JSON-Schema skeleton)

Schemas are at **v0.1.0**. Round 2 finalizes to **v0.2.0**. Backwards-incompatible changes require a major bump.

All schemas use JSON-Schema Draft 2020-12. Referenced as `$ref: "https://harness.example/schemas/<name>.schema.json#"`.

---

## D.1 Agent Contract — `agent-contract.schema.json`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://harness.example/schemas/agent-contract.schema.json",
  "title": "Agent Contract",
  "type": "object",
  "required": ["agent_id", "version", "role", "cohort", "model_family", "system_prompt_ref", "input_schema", "output_schema"],
  "properties": {
    "agent_id": { "type": "string", "pattern": "^[a-z0-9_]+$" },
    "version": { "type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$" },
    "role": { "type": "string" },
    "cohort": { "type": "string" },
    "model_family": { "type": "string", "enum": ["claude-opus-class", "claude-sonnet-class", "claude-haiku-class", "gpt-4-class", "gpt-5-class", "gemini-2.5-class", "open-source", "other"] },
    "temperature": { "type": "number", "minimum": 0, "maximum": 2 },
    "max_tokens_out": { "type": "integer", "minimum": 1 },
    "system_prompt_ref": { "type": "string", "description": "Path or URI to the system prompt file" },
    "tools": { "type": "array", "items": { "type": "string" } },
    "input_schema": { "oneOf": [{ "type": "object" }, { "type": "string", "format": "uri-reference" }] },
    "output_schema": { "oneOf": [{ "type": "object" }, { "type": "string", "format": "uri-reference" }] },
    "calibration": {
      "type": "object",
      "properties": {
        "brier_rolling": { "type": "number", "minimum": 0, "maximum": 1 },
        "ece_rolling": { "type": "number", "minimum": 0, "maximum": 1 },
        "brier_sample_size": { "type": "integer" },
        "last_updated": { "type": "string", "format": "date-time" }
      }
    },
    "guardrails": { "type": "array", "items": { "type": "string" } },
    "constitution_ref": { "type": "string" }
  }
}
```

---

## D.2 Event Envelope — `event-envelope.schema.json`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://harness.example/schemas/event-envelope.schema.json",
  "title": "Event Envelope",
  "type": "object",
  "required": ["event_id", "campaign_id", "t", "emitter", "kind", "payload"],
  "properties": {
    "event_id": { "type": "string" },
    "campaign_id": { "type": "string" },
    "task_id": { "type": "string" },
    "parent_event_id": { "type": ["string", "null"] },
    "t": { "type": "string", "format": "date-time" },
    "emitter": {
      "type": "object",
      "required": ["kind", "id"],
      "properties": {
        "kind": { "type": "string", "enum": ["agent", "tool", "orchestrator", "verifier", "guardrail", "human", "memory", "drift"] },
        "id": { "type": "string" },
        "adapter": { "type": "string" }
      }
    },
    "kind": { "type": "string", "enum": ["emission", "tool_call", "tool_result", "decision", "verifier_result", "drift_check", "approval_request", "approval_decision", "guardrail_event", "memory_load", "memory_write", "error"] },
    "payload": { "type": "object" },
    "refs": {
      "type": "object",
      "properties": {
        "memory_refs": { "type": "array", "items": { "type": "string" } },
        "contract_ref": { "type": "string" },
        "prior_packet_ref": { "type": ["string", "null"] }
      }
    },
    "cost": {
      "type": "object",
      "properties": {
        "tokens_in": { "type": "integer" },
        "tokens_out": { "type": "integer" },
        "wall_clock_ms": { "type": "integer" },
        "usd": { "type": "number" }
      }
    },
    "flags": { "type": "array", "items": { "type": "string" } }
  }
}
```

---

## D.3 Consensus Packet — `consensus-packet.schema.json`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://harness.example/schemas/consensus-packet.schema.json",
  "title": "Consensus Packet",
  "type": "object",
  "required": ["campaign_id", "cohort", "task_id", "outcome_type", "consensus", "contributing_agents"],
  "properties": {
    "campaign_id": { "type": "string" },
    "cohort": { "type": "string" },
    "task_id": { "type": "string" },
    "outcome_type": { "type": "string", "enum": ["strengthened", "revised", "unchanged_but_calibrated"] },
    "consensus": {
      "type": "object",
      "required": ["value", "value_type", "confidence"],
      "properties": {
        "value": {},
        "value_type": { "type": "string", "enum": ["numeric", "categorical", "structured", "prose", "boolean"] },
        "interval": {
          "type": "object",
          "properties": {
            "low": {},
            "high": {},
            "units": { "type": "string" }
          }
        },
        "confidence": { "type": "number", "minimum": 0, "maximum": 1 }
      }
    },
    "dissent": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["position", "agents", "weight_share"],
        "properties": {
          "position": {},
          "agents": { "type": "array", "items": { "type": "string" } },
          "reasoning": { "type": "string" },
          "weight_share": { "type": "number", "minimum": 0, "maximum": 1 }
        }
      }
    },
    "contributing_agents": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["agent_id", "weight"],
        "properties": {
          "agent_id": { "type": "string" },
          "emission_ref": { "type": "string" },
          "weight": { "type": "number", "minimum": 0 }
        }
      }
    },
    "verifier_results": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "verifier_id": { "type": "string" },
          "result": { "type": "string", "enum": ["pass", "fail", "abstain"] },
          "evidence_ref": { "type": "string" }
        }
      }
    },
    "bs_flags": {
      "type": "object",
      "properties": {
        "hallucinated": { "type": "integer" },
        "over_confident": { "type": "integer" },
        "unsupported": { "type": "integer" },
        "clean": { "type": "integer" }
      }
    },
    "context_used": {
      "type": "object",
      "properties": {
        "memory_refs": { "type": "array", "items": { "type": "string" } },
        "tools_called": { "type": "array", "items": { "type": "string" } }
      }
    },
    "cost": {
      "type": "object",
      "properties": {
        "tokens": { "type": "integer" },
        "wall_clock_ms": { "type": "integer" },
        "usd": { "type": "number" }
      }
    }
  }
}
```

---

## D.4 Orchestrator State — `orchestrator-state.schema.json`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://harness.example/schemas/orchestrator-state.schema.json",
  "title": "Orchestrator State",
  "type": "object",
  "required": ["campaign_id", "started_at", "intent_ref", "intent_hash", "plan"],
  "properties": {
    "campaign_id": { "type": "string" },
    "started_at": { "type": "string", "format": "date-time" },
    "intent_ref": { "type": "string" },
    "intent_hash": { "type": "string" },
    "plan": {
      "type": "object",
      "properties": {
        "steps": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "step_id": { "type": "string" },
              "description": { "type": "string" },
              "cohort": { "type": "string" },
              "status": { "type": "string", "enum": ["pending", "in_progress", "done", "blocked"] }
            }
          }
        },
        "current_step": { "type": "integer" }
      }
    },
    "active_cohorts": { "type": "array", "items": { "type": "string" } },
    "budget": {
      "type": "object",
      "properties": {
        "tokens_used": { "type": "integer" },
        "tokens_budget": { "type": "integer" },
        "usd_used": { "type": "number" },
        "usd_budget": { "type": "number" },
        "wall_clock_ms_used": { "type": "integer" },
        "wall_clock_ms_budget": { "type": "integer" }
      }
    },
    "drift": {
      "type": "object",
      "properties": {
        "signal_a": { "type": "number" },
        "signal_b": { "type": "number" },
        "last_checked": { "type": "string", "format": "date-time" },
        "status": { "type": "string", "enum": ["ok", "warn", "pause", "halt"] }
      }
    },
    "pending_approvals": {
      "type": "array",
      "items": { "type": "object" }
    },
    "recent_packets": { "type": "array", "items": { "type": "string" } },
    "memory_load_refs": { "type": "array", "items": { "type": "string" } }
  }
}
```

---

## D.5 Memory Index entry — `memory-index.schema.json`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://harness.example/schemas/memory-index.schema.json",
  "title": "Memory Index Entry",
  "type": "object",
  "required": ["memory_id", "tier", "scope", "sensitivity", "freshness"],
  "properties": {
    "memory_id": { "type": "string" },
    "tier": { "type": "string", "enum": ["L0", "L1", "L2", "L3"] },
    "scope": { "type": "string", "enum": ["campaign", "cross_campaign", "organization"] },
    "domain": { "type": "string" },
    "subdomain": { "type": "string" },
    "sensitivity": { "type": "string", "enum": ["public", "internal", "pii", "secret"] },
    "freshness": { "type": "string", "format": "date" },
    "expires": { "type": ["string", "null"], "format": "date" },
    "confidence": { "type": "number", "minimum": 0, "maximum": 1 },
    "source": { "type": "string" },
    "contributing_agents": { "type": "array", "items": { "type": "string" } },
    "supersedes": { "type": ["string", "null"] },
    "tags": { "type": "array", "items": { "type": "string" } },
    "body_ref": { "type": "string" }
  }
}
```

---

## D.6 Versioning policy

- Schema files carry an `$id` with a version path (`/v0.1/...`). v0.2 lives at a parallel path.
- Additive changes (new optional fields) are minor bumps.
- Breaking changes (removed fields, type changes, renames) are major bumps.
- Event-log readers tolerate forward-compatible additions; they warn but do not fail on unrecognized fields.

## D.7 Where these live in the repo (Round 2)

- `packages/harness-protocol/schemas/` — JSON-Schema files.
- `packages/harness-protocol/src/` — TypeScript type exports generated from schemas via `json-schema-to-typescript`.
- `packages/harness-protocol-py/` — Python dataclasses generated from schemas via `datamodel-code-generator`.

## D.8 What is intentionally *not* a schema

- Tool-call signatures (those are per-tool; each tool owns its schema).
- Retrospective proposal format (defined by the retrospective package; not protocol-level).
- Human approval UI (adapter-specific).

These remain adapter/module concerns; the protocol does not constrain them.
