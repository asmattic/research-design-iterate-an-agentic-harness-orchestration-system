# 19 · Worked Example — AI Research (Anthropic's Multi-Agent Research System, Deconstructed)

## Why this case study

The single most-cited data point in favor of this PRD's entire architectural thesis is Anthropic's own published retrospective: *How we built our multi-agent research system* (2025). Their system demonstrated a **+90.2%** improvement over single-agent Opus 4 on internal research evaluations, at ~15× the token cost. The post is unusually candid about both the wins and the hard-won lessons.

Using Anthropic's system as a worked example does three things:
1. Grounds this PRD in a real, documented, production-validated precedent.
2. Shows where our PRD agrees with them (most places) and where it extends (specific additions around drift, calibration, protocol portability).
3. Gives a concrete benchmark-set shape that any reader can adapt.

## 19.1 Anthropic's MARS — the architecture as published

**Shape.**
- **Lead researcher** (Opus 4 class) — the strategic orchestrator.
- **Subagent researchers** (Sonnet 4 class) — parallel specialists dispatched by the lead.
- **Tools**: web search, file retrieval, internal doc access.
- Parallel tool use by a *single* agent accelerates by ~90% (per the post). Parallel subagents dramatically speed breadth-first research.

**What they report works.**
- Clear task decomposition by the lead researcher ("research this question from these five angles in parallel").
- Explicit subagent prompts with constraints ("do not follow tangents", "summarize in ≤ 500 tokens").
- Defensive handling of subagent failures (the lead tolerates a few failed subagents and proceeds).
- Heavy use of **prompt engineering discipline** on the lead researcher to avoid over-spawning subagents (a known failure mode).

**What they report is hard.**
- **Token cost.** 15× a standard chat; 4× a single-agent task.
- **Coordination overhead.** Lead researcher's context fills up with subagent results.
- **Debugging.** Non-determinism compounds; a broken campaign is hard to root-cause.
- **Eval discipline.** Research-task evals are expensive to build and run.
- **Coordination beats model quality for this task shape.** A better model helps; better orchestration helps more.

## 19.2 What this PRD agrees with

- **Orchestrator-subagent pattern is correct.** (§§05, 06)
- **Parallel specialists are a net win when the task is breadth-first.** (§08)
- **Subagent prompts must constrain scope.** (§06 expert agent contracts)
- **Cost is real; budget continuously.** (§§08, 14)
- **Coordination > model quality for this task shape.** This justifies the Orchestrator System investment.

## 19.3 Where this PRD extends

### Explicit Orchestrator System layer
Anthropic's post does not describe a BS-detector / validator / drift-detector layer as a separate component (though elements of it exist inside the lead researcher's prompt). This PRD breaks it out as its own named layer with six sub-responsibilities (§6.4), because:
- It is testable in isolation.
- It is replaceable as models improve.
- It is the single most consequential architectural addition beyond the orchestrator pattern.

### Confidence intervals as first-class output
Anthropic's post focuses on ground-truthed answers. When ground truth is not available, calibrated confidence is. This PRD makes the Consensus Packet with interval + dissent a schema (§9, §15), not a nice-to-have.

### Continuous drift control against an INTENT anchor
The MARS post describes defenses against scope creep within the lead researcher's prompt. This PRD formalizes it as a continuous measurement (§11) with quantitative and qualitative signals and automatic pause-on-threshold.

### Harness portability
MARS runs on Anthropic's internal stack. This PRD specifies a protocol + adapters (§15, §16) so the same orchestration ports across Claude Code, Codex, Cursor. The cost is a small adapter layer; the payoff is no vendor lock.

### Deterministic verifier arbitration
MARS defers to the lead researcher's judgment on conflicting subagent outputs. This PRD mandates a deterministic verifier for any testable claim, with the verifier's output taking precedence (§6.7, §02 hard constraint).

## 19.4 A research campaign, redesigned on this harness

**Task.** "Produce a structured, cited report on the state-of-the-art in agentic harness design, covering orchestration patterns, signal-weighting techniques, and failure modes, suitable for a PRD-style design document."

(This is, recursively, roughly the task this PRD itself addresses — a useful validation signal.)

**INTENT.md (excerpt).**
```
# Goal
Produce a cited, structured research report on agentic harness architectures as of April 2026.

# Success criteria
- Every claim with an author or date is cited to a retrievable source.
- At least 3 orthogonal sources per architectural position.
- Report explicitly names the failure modes covered (F1–F8 schema).
- Contrasts at least 2 industry positions (e.g., Anthropic vs Cognition) with attribution.

# Non-goals
- A new proposed framework.
- Opinions presented without attribution.

# Hard constraints
- No fabricated citations.
- No paraphrase-passing-as-paraphrase; quote + cite or summarize + cite.
```

**Cohort dispatch.**

| Cohort | Responsibility | Experts |
|---|---|---|
| **Literature** | Academic & industry paper search | literature_scanner (×3: Scholar, Semantic Scholar, Anthropic/OpenAI blog) |
| **Synthesis** | Cluster findings, identify positions | synthesizer, structured_summarizer |
| **Adversarial** | Stress-test claims, spot fabrications | citation_verifier (deterministic), skeptic_judge, bias_detector |
| **Composition** | Write the report | section_drafter (×N, one per section) + style_editor |

**Deterministic verifier tools.**
- `citation_resolve(title, author, year)` — returns URL/DOI or fails.
- `quote_verify(claim, source)` — fuzzy match against fetched document.
- `author_disambiguator` — prevents conflating authors.
- `year_sanity` — prevents citing a paper before it was published.

**End-to-end flow.**
1. Primary orchestrator dispatches Literature: "Retrieve top-20 recent and top-20 seminal papers across eight topic axes."
2. Literature swarm fans out with 3 different retrieval views. Verifier resolves every citation. Unresolvable citations (hallucinations) rejected. Emits packet: ~200 verified sources.
3. Synthesis cohort clusters sources into positions. Output: ~15 positions with attribution.
4. Adversarial cohort reviews. Skeptic tests claims; citation_verifier confirms every quote. Flags 3 suspected overreaches; routes back to Synthesis for tightening.
5. Composition cohort drafts sections in parallel (one expert per section). Style editor harmonizes. Verifier re-runs citation resolution on the final draft.
6. Primary orchestrator assembles. Final drift check against INTENT (every claim still cited?). Final report emits.
7. No irreversible action; the report is the output. Human review closes the campaign.

**Why this beats a single-agent approach.**
- One agent cannot hold 200 sources + 8 topic axes + 15 positions in context. Multi-cohort decomposes.
- Deterministic citation verifier catches fabrications at emission time, not after publication.
- Adversarial cohort is explicit and budgeted; "skeptic role" is not a vibe in the prompt but a separate cohort with its own KPI (fabrications-caught).
- Drift control keeps the report on the assigned scope.

## 19.5 Benchmark anchor — GAIA and BrowseComp

**GAIA** *(Mialon et al., 2023)* is a 466-question general-AI-assistant benchmark with complex, multi-tool research tasks.

**BrowseComp** *(OpenAI, 2025)* tests browse-and-synthesize capability.

This harness's research adapter should score competitively on both. Published 2025 baselines:
- GAIA (L1-L3): top agents ~70% on L1, ~50% on L2, ~30% on L3.
- BrowseComp: top agents ~50% pass.

Round-3 target: L2 and L3 uplift ≥ 10 percentage points over single-agent Opus 4 baseline when running this harness on the same task set. Specific ablations validate the drift-control and verifier contributions.

## 19.6 Explicitly where this example is self-referential

This PRD itself was produced by a multi-step research-style workflow that loosely prefigures the harness we're specifying: parallel document reads, structured synthesis, iterative refinement, explicit citation discipline. The campaign that generated this PRD would — in Round 3 — itself be an eval target. If the harness can reproduce or improve on this PRD under the same INTENT, that is strong validation.

## 19.7 Mitigates, mapped

| Failure | Mitigation in this example |
|---|---|
| F1 intent drift | Continuous drift check; INTENT requires citations per claim |
| F2 context rot | Primary orchestrator sees synthesis packets, not the 200-source library |
| F3 compounding error | Adversarial cohort catches propagation of faulty summaries |
| F4 echo chamber | Literature swarm deliberately diverse retrieval; synthesis cohort gets multi-source ground |
| F5 unverifiable | `citation_resolve` and `quote_verify` arbitrate; fabrications rejected |
| F6 runaway cost | Per-cohort budget; orchestrator pauses on excess |
| F7 prompt injection | Retrieved documents are framed as data, not instructions |
| F8 silent irreversible | N/A (no irreversible actions for a research task) |

## One-line summary

> Anthropic's MARS is the single best public precedent for this PRD's architecture. We agree on pattern, extend on layers (Orchestrator System, drift, calibration, protocol portability). A research campaign on this harness adds deterministic citation verification and adversarial arbitration to the MARS playbook.
