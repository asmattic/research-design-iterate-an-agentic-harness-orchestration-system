_The campaign's agent roster. Written by the campaign author; read by cohort sub-orchestrators at dispatch time. Every entry maps 1:1 to the Agent Contract schema and MUST validate against `packages/harness-protocol/schemas/agent-contract.schema.json` — the machine-readable contract JSON is authoritative; this file is its human-readable index._

# Roster

One entry per agent. Fields mirror the agent-contract schema.

## <agent_id: lowercase snake_case, e.g. budget_analyst>

| Field | Value |
|---|---|
| agent_id | <lowercase snake_case identifier, pattern `^[a-z0-9_]+$`> |
| version | <semver, e.g. 0.1.0> |
| role | <one line: what this specialist does and does not do> |
| cohort | <the cohort this agent belongs to, e.g. finance> |
| model_family | <one of: claude-opus-class, claude-sonnet-class, claude-haiku-class, gpt-4-class, gpt-5-class, gemini-2.5-class, open-source, other> |
| temperature | <0 to 2 — low for factual/extraction agents, higher for creative/exploration agents> |
| system_prompt_ref | <path or URI to the versioned system prompt file, e.g. prompts/budget_analyst.md> |
| tools | <comma-separated tool names this agent may call — least privilege> |
| guardrails | <guardrail rule ids applied at this agent's boundary, e.g. privacy_pii, quality_citation> |
| constitution_ref | <path to the campaign CONSTITUTION.md this agent is bound by> |

Contract JSON: <path to this agent's agent-contract .json file>

## <next_agent_id>

<repeat the table above for every agent in the roster>

# Notes

- An agent not listed here (and without a validating contract) must not be dispatched.
- `input_schema` and `output_schema` are required by the contract schema; they live in the contract JSON, referenced here only by the contract path.
- Calibration fields (rolling Brier / ECE) are maintained by the weight tweaker, not hand-edited here.
- Swarm membership is declared in SWARM.md; this file lists the individuals.

_Template: harness-reference v0.2.0 · see prd/ and WAYFINDER-DESIGN.md for rationale_
