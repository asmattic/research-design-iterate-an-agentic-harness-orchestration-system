_Definition of one cohort — a domain-scoped group of experts managed by a sub-orchestrator (PRD §6.5). Written by the campaign author, one copy per cohort. The primary orchestrator delegates domains, not tasks; this file tells the cohort how to decompose and what it owes back._

# Cohort: <cohort name, e.g. finance>

## Domain

<one paragraph: the domain this cohort owns, and its edges — what belongs to a neighboring cohort instead>

## Tools

- <tool 1: e.g. a specific API, database, or search surface — least privilege>
- <tool 2>

## Ground-truth sources

Where this domain's claims get checked before an LLM opinion is trusted.

- <source 1: e.g. county records API, test suite, ledger export>
- <source 2>

## Quality bar

- <what a resolution must include to be acceptable in this domain, e.g. "every figure cites its source row">
- <domain-specific rejection criteria>

## Experts

Members are defined in AGENTS.md; list them here by agent_id.

- <agent_id 1> — <one line on when this cohort dispatches to them>
- <agent_id 2>

## SLAs

- Latency bound: <max wall-clock per task, e.g. 10 min>
- Cost bound: <max tokens or dollars per task>
- On breach: <abort and report / degrade to single expert / escalate>

## Single expert vs swarm (decision rule, PRD §6.6)

- **Single expert** if the task is narrowly scoped and verifier-testable, or cost-sensitive. <cohort examples>
- **Swarm** if the task benefits from perspective diversity, involves subjective judgment, or is high-stakes. <cohort examples> Swarm composition per SWARM.md.

## Packet obligations

Every task returns exactly one packet to the primary orchestrator, containing:

- Consensus answer (headline value)
- Confidence interval + stated confidence
- Dissenting views, preserved verbatim in gist form (never silently dropped)
- Verifier results for every testable claim (untestable claims marked as such)
- Cost and latency telemetry

## Caucus bounds (only if peer visibility is granted)

Within-cohort only; cross-cohort caucus is forbidden. If this cohort grants scoped peer visibility for a task:

- Experts: <cap, default 4>
- Turns: <cap, default 6 each>
- Tokens: <cap, default 20K total>
- Wall-clock: <cap, default 10 min>
- The caucus transcript is summarized by this cohort's sub-orchestrator into the packet; the primary orchestrator never sees raw caucus transcripts.

_Template: harness-reference v0.2.0 · see prd/ and WAYFINDER-DESIGN.md for rationale_
