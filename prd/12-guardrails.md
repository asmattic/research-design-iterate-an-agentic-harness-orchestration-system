# 12 · Guardrails

## The four classes of guardrail

1. **Policy** — non-negotiable behavioral rules (constitution-level). Never cross.
2. **Safety** — prompt-injection resistance, jailbreak detection, harmful-content filters.
3. **Quality** — output format validation, citation requirements, confidence bounds.
4. **Privacy** — PII / secret handling, data-vs-instruction segregation.

Each class operates at every agent → orchestrator boundary. Each class can reject, degrade (lower signal weight), or escalate (surface to human).

## 12.1 Policy guardrails (Constitutional)

**Source.** A written `CONSTITUTION.md` (per-deployment, per-cohort where finer grain is useful) listing rules the system will not violate regardless of user instruction or tool output.

**Example constitutional rules (generic):**
- No irreversible side-effects without explicit human approval.
- No fabrication of citations (every cited source must resolve).
- No legal / medical / financial advice presented as authoritative (always paired with "consult professional" where INTENT flags the domain).
- No bypassing the verifier on testable claims.

**Mechanism.** Constitutional AI *(Bai et al., 2022)*. Each agent is provided the constitution in its system prompt. A separate "constitutional judge" LLM call reviews output against the constitution before emission is accepted. Violations route back to the agent with a correction requirement.

**Mitigates.** F7 (prompt injection → goal substitution), F8 (silent irreversible actions), reputation/legal risk broadly.

## 12.2 Safety guardrails

### Prompt-injection detection
- Input scans (user prompts, tool outputs) for known injection patterns ("ignore previous instructions", meta-command prefixes, hidden markdown).
- Strict separation of "data" channels from "instruction" channels in agent context. Tool outputs are always framed as data, never as directives.
- Adversarial eval (§14) runs injection payloads as a test suite; the eval score gates releases.

**Tool choices (adapter-level):**
- **NeMo Guardrails** — declarative, Python, good for programmable flows.
- **Llama Guard 3** — classifier model, good for quick screening.
- **Bespoke regex + LLM-judge** — fast, explicit, maintainable for small guardrail sets.

The harness doesn't mandate one; the adapter layer plugs in whichever the runtime supports.

### Jailbreak detection
- Patterns like roleplay prompts ("pretend you are…"), DAN prompts, character injection.
- Policy response: reject, log, optionally trigger adversarial-eval update.

### Harmful-content filters
- Input and output scans via Llama Guard or equivalent.
- Policy: reject on flagged categories; never soft-warn on high-severity.

## 12.3 Quality guardrails

### Structured-output validation
- Every agent emission is JSON-validated against its contract schema (§15 Agent Contract).
- Invalid emissions are rejected with a schema-diff fed back to the agent.

### Citation requirement
- Cohorts can require sources for specified claim types (legal claims, empirical claims).
- Agents that emit claims without sources are flagged `unsupported` by the BS Detector (§6.4.2).

### Confidence bound check
- An agent reporting confidence > 0.95 on a non-verifier-testable claim is flagged `over-confident`.
- An agent reporting confidence < 0.5 but still asserting a position without caveats is flagged `mis-calibrated`.

### Numeric sanity bounds
- Per-cohort numeric bounds ("DSCR between 0.3 and 4.0", "cap rate between 2% and 20%"). Values outside bounds auto-flag.

## 12.4 Privacy guardrails

### Data classification
- See §10.5 memory sensitivity tags: public / internal / pii / secret.

### Redaction at load
- When the Context Manager (§6.4.1) loads memory for the primary orchestrator, PII is redacted to placeholders unless the campaign's INTENT explicitly permits PII in orchestrator context.
- Secrets are *never* loaded into any LLM context. They are referenced by ID; the verifier or tool call materializes them directly via secure storage.

### Tool-call hygiene
- Outbound tool calls are inspected for accidental PII leakage (e.g., a URL that embeds a user's SSN).
- The guardrail layer can rewrite or block tool calls before they execute.

### Output scrubbing
- Final outputs to the human are scrubbed for inadvertent credential/PII leakage (tokens, access keys, session IDs, etc.).

## 12.5 Where guardrails live

Three placement options, chosen per adapter:

| Placement | Pro | Con | Recommended for |
|---|---|---|---|
| Inline in agent prompt (instructions + refusals) | Simple, no infra | Bypassable under adversarial pressure | Quality rules |
| As a separate LLM call on each emission | More robust | Latency + cost | Policy + safety |
| As a non-LLM classifier / regex / schema check | Fast, deterministic | Limited coverage | Privacy + quality |

Production deployments combine all three: schema validation (fast, deterministic) + a policy-judge LLM call (robust) + prompt-level instructions (cheap backup).

## 12.6 Guardrail metrics (feed the eval harness)

- **False reject rate** — how often guardrails block legitimate work. Target ≤ 2%.
- **False allow rate** — how often guardrails miss a violation. Target ≤ 0.1% (and 0 on constitutional violations).
- **Latency overhead** — target ≤ 20% of total orchestration latency.
- **Cost overhead** — target ≤ 10% of campaign token budget.

Tracked per-campaign by the eval harness (§14).

## 12.7 Guardrail updates

Constitutional rules change only via human ratification (analogous to INTENT updates). Safety patterns update from a continuously-maintained adversarial test set. Quality rules are cohort-scoped and can be updated by the cohort owner between campaigns. Privacy rules change only via a formal deployment-config change.

## 12.8 What guardrails are *not*

- Not a replacement for deterministic verification (§6.7). A guardrail rejects bad output; the verifier determines *which* output is correct.
- Not a replacement for the human approval gate (§6.1). Guardrails reduce the rate of gate-arrivals; they do not bypass the gate.
- Not a replacement for drift control (§11). A drift-ok output can still violate a guardrail; a guardrail-ok output can still drift.

## Diagram reference

- **D09 (Guardrail stack)** — layered filters at agent-emission boundary.

## One-line summary

> Four classes (policy / safety / quality / privacy), layered at every boundary, implemented as composable checks (schema + classifier + LLM-judge), with metrics feeding the eval harness. Constitutional rules are not negotiable; everything else tunes.
