# Appendix B · Glossary

Terms are listed alphabetically. Definitions are scoped to this PRD's usage.

**Adapter** — A thin translation layer that maps the harness-agnostic protocol (§15) to a specific runtime's primitives (Claude Code, Codex CLI, Cursor). Lives in `adapters/<name>/`.

**Agent Contract** — A JSON-Schema document specifying one specialist agent's role, model, toolset, input schema, output schema, calibration, and guardrails. Schema 1 of 5.

**BS Detector** — Sub-responsibility of the Orchestrator System that flags hallucinations, over-confidence, unsupported claims, and obvious fabrications before they propagate.

**Brier score** — A proper scoring rule for probability calibration. `mean((predicted_prob − actual_outcome)^2)`. Lower is better. Target ≤ 0.15.

**Caucus** — A bounded peer-visibility pattern within a cohort (§07). Up to N turns, capped tokens, capped wall-clock. Transcripts are summarized at the cohort boundary.

**Campaign** — One end-to-end run of the harness against a single `INTENT.md`. Has a `campaign_id`; produces an event log, packets, and a final report.

**Clean context** — The primary orchestrator's context budget discipline: only INTENT, plan, packets, drift/budget status. No raw agent transcripts.

**Cohort** — A domain-scoped group of experts managed by a Sub-Orchestrator. Examples: finance, legal, research.

**Cohort Sub-Orchestrator** — The manager LLM for a cohort. Receives tasks from the primary orchestrator; dispatches to experts / swarms; aggregates; emits packets.

**Confidence Interval Consensus** — The swarm-output format: a headline value plus an interval plus a stated confidence plus preserved dissent.

**Consensus Packet** — The output of a cohort to the primary orchestrator. Schema 3 of 5. Contains outcome_type (strengthened/revised/unchanged), consensus (value + interval + confidence), dissent, contributing agents, verifier results, cost.

**Constitutional AI** — Training / prompting pattern in which a model is given a written constitution and critiques its own outputs against it *(Bai et al., 2022)*. Used at §12 guardrails.

**Context rot** — Degradation of LLM attention across long prompts; the middle gets under-weighted *(Liu et al., 2023, "Lost in the Middle")*. Mitigated by tiered memory and clean-context primary orchestrator.

**Deterministic verifier** — A code-based arbitrator that runs tests, schema checks, URL checks, numeric bound checks. Its output takes precedence over LLM opinions (§02 hard constraint).

**Drift** — Semantic distance between current orchestrator state and INTENT. Measured continuously as a composite of cosine distance and LLM-judge rubric score (§11).

**ECE (Expected Calibration Error)** — Measures how well reported confidences match empirical accuracy across buckets. Target ≤ 0.10.

**Event Envelope** — The wrapper around every log entry. Schema 2 of 5. Contains timestamps, IDs, emitter info, kind, payload, refs, cost, flags.

**Event log (L3)** — Append-only JSONL record of every emission, tool call, orchestrator decision, verifier result, drift check. The ground truth for retrospectives and audits.

**Expert** — A specialist agent with a focused role and constrained I/O. Single-agent or part of a swarm.

**Expert Swarm** — N experts of the same specialty with deliberately varied prompts, models, or retrieval views, producing a confidence-interval consensus via the aggregator. Mixture-of-Agents pattern.

**F1–F8** — The eight named failure modes in §03 that the architecture is designed against: intent drift, context rot, compounding error, echo chamber, unverifiable stochastic claims, runaway cost, prompt injection, silent irreversible actions.

**Guardrail** — Policy/safety/quality/privacy check enforced at agent → orchestrator boundaries (§12).

**Hub topology** — Default inter-agent communication pattern: all traffic routes through the Orchestrator System (§07). Redux/Zustand analogue.

**INTENT.md** — The immutable campaign anchor. Only the human changes it. Every decision maps to it; drift is measured against it (§02, §11).

**L0 / L1 / L2 / L3** — Memory tiers: working (in-context) / hot (KV) / indexed (vector + SQL) / cold (archive) (§10).

**LLM-as-Judge** — Using an LLM to score another LLM's output against a rubric. Calibrated against human labels *(Zheng et al., 2024)*.

**Memory Index** — Structured metadata about a memory entry (sensitivity, freshness, confidence, source, supersedes). Schema 5 of 5. Queried by semantic + structured filters.

**Mesh topology** — Peer-to-peer inter-agent communication. Explicitly not the default in this PRD (§07). Bounded exceptions in caucus.

**Mixture-of-Agents (MoA)** — Pattern where N agents each produce a response and an aggregator combines *(Wang et al., Together AI, 2024)*. Used for cohort swarms (§6.6, §9.2).

**Orchestrator State** — The campaign-level state snapshot, read by the primary orchestrator each turn. Schema 4 of 5.

**Orchestrator System** — The middleware between Primary Orchestrator and cohort layer. Six sub-responsibilities: context manager, BS detector, validator, signal/noise attributor, weight tweaker, drift detector (§6.4).

**Packet** — Shorthand for Consensus Packet.

**Primary Orchestrator** — The strategic, thin, clean-context layer that interacts with the human and delegates domain work (§6.3).

**Prompt injection** — Adversarial input that causes an agent to pivot from its instructions. Failure mode F7. Mitigated by guardrails + data/instruction separation (§12).

**Reflexion** — Per-turn verbal self-critique appended to an agent's episodic memory *(Shinn et al., 2023)*. Cadence 1 of 3 feedback loops (§13).

**Retrospective** — Per-task review that proposes agent-prompt diffs, memory entries, and weight adjustments. Cadence 2 of 3 (§13.2).

**Self-Consistency** — Sampling the same CoT query multiple times and taking the majority *(Wang et al., 2023)*. Principle extended to swarm aggregation.

**Signal/Noise Attributor** — Sub-responsibility of the Orchestrator System that weights incoming claims by source calibration, verifier result, agreement, and BS flags (§6.4.4).

**Strengthened / Revised / Unchanged-but-calibrated** — The three-valued outcome type for a re-examination pass (§9.3). Always one of these three, never silent overwrite.

**Swarm** — See Expert Swarm.

**Verifier** — See Deterministic verifier.

**Weight Tweaker** — Sub-responsibility of the Orchestrator System that updates per-agent and per-tool trust weights over time based on retrospective outcomes (§6.4.5).
