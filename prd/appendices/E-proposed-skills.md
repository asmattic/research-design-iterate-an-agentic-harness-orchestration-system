# Appendix E · Proposed Skills for Round 2 `skill-creator`

Round 2 uses Claude Code's `/skill-creator` to implement the Orchestrator System's six sub-responsibilities as Skills plus a small cohort-runner Skill set. Each entry below is a Round 2 skill spec: name, trigger phrases, responsibilities, inputs, outputs, and non-goals.

---

## Skill: `harness-bs-detector`

**Description.** Runs the BS Detector (§6.4.2) on an agent emission.

**Triggers:** "flag hallucinations in", "check for over-confidence", "BS-check this emission", "validate agent output quality".

**Inputs:**
- Agent emission (structured, via Agent Contract output schema).
- Rubric file path.

**Outputs:**
- JSON with flags: `hallucinated` / `over_confident` / `unsupported` / `clean`.
- Reasoning trace (≤ 500 tokens).

**Non-goals:**
- Not a deterministic verifier — only LLM-judge with rubric.
- Not a guardrail enforcer — produces flags, does not reject.

---

## Skill: `harness-drift-detector`

**Description.** Runs the drift detector (§11). Called automatically by a PostToolUse hook after orchestrator turns.

**Triggers:** "check drift against INTENT", "run drift check", "measure intent alignment".

**Inputs:**
- INTENT.md path.
- Orchestrator state snapshot (Orchestrator State schema).
- Thresholds config.

**Outputs:**
- JSON with signal_a (cosine), signal_b (rubric score), recommended action (proceed / warn / pause / halt).
- Reasoning.

**Non-goals:**
- Does not pause the campaign itself — the primary orchestrator reads the output and decides.
- Does not modify INTENT.

---

## Skill: `harness-signal-attributor`

**Description.** Runs the Signal/Noise Attributor (§6.4.4).

**Triggers:** "weight these agent outputs", "attribute signal in this packet", "compute per-agent trust weights".

**Inputs:**
- Array of agent emissions with metadata (agent_id, verifier_results, BS flags).
- Per-agent calibration cache (from memory).

**Outputs:**
- Per-emission weight (0–1).
- Aggregate cohort confidence.

---

## Skill: `harness-validator`

**Description.** Bridges to the deterministic verifier (§6.4.3). Runs verifier-testable claims through the verifier MCP tools and returns structured results.

**Triggers:** "verify this claim", "run deterministic checks", "test these numeric claims".

**Inputs:**
- Claims to test (schema + expected type).
- Verifier tool allowlist.

**Outputs:**
- Per-claim pass/fail/abstain with evidence.

---

## Skill: `harness-context-manager`

**Description.** Loads the right slice of memory for a given orchestrator turn (§6.4.1). Enforces budget and summarizes where needed.

**Triggers:** "load context for this turn", "prepare orchestrator context", "budget-aware summarize this packet".

**Inputs:**
- Memory Index reference.
- Context budget (tokens).
- Current orchestrator state.

**Outputs:**
- Selected memory entries.
- Summaries where needed.
- Audit log of loads and summarizations.

---

## Skill: `harness-retrospective`

**Description.** Post-task retrospective (§13.2). Reviews the event log and proposes diffs.

**Triggers:** "run retrospective on campaign", "propose improvements from this campaign", "what should we update after this task".

**Inputs:**
- Event log path.
- INTENT.md path.
- Current agent prompt set.

**Outputs:**
- Proposed agent-prompt diffs (as `.diff` files).
- Proposed L2 memory entries.
- Proposed weight adjustments.
- Retrospective narrative (≤ 2K tokens).

**Non-goals:**
- Does not apply diffs — human ratifies.
- Does not modify INTENT.

---

## Skill: `harness-orchestrator-plan`

**Description.** Helps the primary orchestrator produce or revise a campaign plan rooted in INTENT.

**Triggers:** "plan this campaign", "revise plan given new packets", "decompose INTENT into cohort tasks".

**Inputs:**
- INTENT.md.
- Current Orchestrator State.
- Latest packets.

**Outputs:**
- Updated plan (array of steps, each assigned to a cohort).
- Justification tied to INTENT criteria.

---

## Skill: `harness-cohort-dispatch`

**Description.** Spawns a cohort sub-orchestrator for a given task. Provides the task spec and returns a Consensus Packet.

**Triggers:** "dispatch to finance cohort", "run legal cohort task", "cohort-dispatch this work".

**Inputs:**
- Task spec.
- Cohort ID.
- Budget allocation.

**Outputs:**
- Consensus Packet.
- Event log entries.

---

## Skill: `harness-swarm-run`

**Description.** Inside a cohort, runs an N-agent swarm with a given composition and aggregates to a Consensus Packet.

**Triggers:** "run swarm on this question", "MoA aggregate this", "5-agent consensus on X".

**Inputs:**
- Task spec.
- Swarm composition (N agents + specialization axes).
- Aggregator config.

**Outputs:**
- Per-agent emissions (referenced in the packet).
- Consensus Packet with intervals + dissent.

---

## Skill: `harness-eval-run`

**Description.** Runs the eval harness against a benchmark set (§14.7).

**Triggers:** "eval this config", "run benchmark", "eval harness run".

**Inputs:**
- Benchmark name.
- Config path.
- Output directory.

**Outputs:**
- Scores per dimension.
- Regression gate result.
- `report.md`.

---

## Naming convention

All harness Skills use the `harness-<function>` prefix to group them in Skill listings and to allow a single `/plugins remove harness-*` rollback.

## Versioning

Each Skill's `SKILL.md` frontmatter carries a `harness_version` field aligned to the protocol version. Round 2 ships with `harness_version: 0.2.0`.

## Deferred to Round 3 / later

- `harness-adversarial-eval` — adversarial-set runner (Round 3).
- `harness-compliance-trace` — mapping of events to compliance controls (Round 5+).
- `harness-cost-optimizer` — proposes cohort / swarm-size tuning based on cost/quality curves (Round 3+).
