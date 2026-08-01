_Composition sheet for one expert swarm (PRD §6.6). Written by the campaign author or cohort owner, one copy per swarm. A swarm is N experts of one specialty with deliberately varied prompts, models, or retrieval views — designed diversity is the whole point._

# Swarm: <swarm name, e.g. zoning_evaluation>

- Cohort: <owning cohort>
- Specialty: <the question class this swarm answers>
- Size: <N, typically 3–5>
- Members: <agent_ids from AGENTS.md>

## Anti-pattern warning

Five copies of one prompt is not a swarm — it is one opinion sampled five times, and it will echo its own premises (failure mode F4). Every member must differ on at least one axis below; a well-built swarm covers most of them.

## The five deliberate-diversity axes (checklist)

- [ ] **Adversarial role** — <which member is explicitly instructed to argue against the leading hypothesis>
- [ ] **Literature-first vs data-first** — <which member grounds in static knowledge; which grounds in live retrieval>
- [ ] **Model families** — <which model families are mixed, where cost allows — e.g. one claude-class, one gpt-class, for epistemic diversity>
- [ ] **Retrieval views** — <how retrieval differs per member: top-k values, rerankers, query rewrites>
- [ ] **Temperatures** — <the spread: low for factual members, higher for creative/exploration members>

<for each axis left unchecked, one line on why the diversity it buys is not needed here>

## Aggregation contract

The swarm's output is a single Consensus Packet (schema: `consensus-packet.schema.json`), aggregated by the cohort sub-orchestrator:

- **Confidence-interval consensus** — a headline value plus an interval plus a stated confidence, never a bare point verdict.
- **Three-valued outcome** — every re-examination pass reports exactly one of *strengthened / revised / unchanged-but-calibrated*. Silent overwrite is forbidden.
- **Dissent preserved** — any position held by ≥ 15% of members (weighted) is carried in the packet's dissent field, in gist form with a pointer to the full argument. Dissent is signal, not noise to be averaged away.
- Verifier results attach per claim before aggregation; a verifier verdict outweighs any member's opinion.

## Dispatch criteria

Use this swarm (rather than a single expert) when: <the cohort's swarm criteria for this specialty — subjective judgment, high stakes, contested evidence>

Cost note: this swarm costs roughly <N>x a single expert call. <when to degrade to the single-expert path>

_Template: harness-reference v0.2.0 · see prd/ and WAYFINDER-DESIGN.md for rationale_
