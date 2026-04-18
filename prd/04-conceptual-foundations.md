# 04 · Conceptual Foundations

This chapter grounds every architectural choice in §§05–13 against published work. The goal is not a literature survey — it is a load-bearing bibliography where each citation justifies a specific design decision. Full reference entries live in Appendix C.

## The pillars we build on

The design rests on eight conceptual pillars. Each one is backed by one or more papers; each one maps directly to a section of the architecture.

| Pillar | Load-bearing question | Primary citations | Used in |
|---|---|---|---|
| **Multi-agent orchestration works** | Is the overhead worth it? | Anthropic 2025 (MARS), Wu et al. 2023 (AutoGen), Hong et al. 2024 (MetaGPT) | §05, §06 |
| **Mixture of Experts / Agents** | How do you fuse multi-perspective output? | Shazeer et al. 2017 (sparse MoE), Wang et al. 2024 (Mixture-of-Agents) | §06, §09 |
| **Self-consistency + deliberation** | How do you separate signal from noise? | Wang et al. 2023 (Self-Consistency), Yao et al. 2023 (Tree-of-Thoughts), Irving et al. 2018 (AI Safety via Debate) | §06, §09 |
| **Reflection + iterative refinement** | How does the system get better? | Shinn et al. 2023 (Reflexion), Madaan et al. 2023 (Self-Refine) | §13 |
| **Process supervision > outcome only** | What do you reward? | Lightman et al. 2023 (Let's Verify Step by Step) | §13, §14 |
| **Context rot is real** | Why not just give the primary orchestrator everything? | Liu et al. 2023 (Lost in the Middle), Anthropic 2025 (context engineering) | §06, §10 |
| **Constitutional constraints** | How do you encode non-negotiable behavior? | Bai et al. 2022 (Constitutional AI) | §12 |
| **LLM-as-Judge, calibrated** | How do you score non-deterministic outputs? | Zheng et al. 2024 (MT-Bench / LLM-as-Judge), Brier 1950 (proper scoring rules) | §09, §14 |

## Pillar 1 — Multi-agent orchestration

**The headline evidence.** Anthropic's multi-agent research system (Opus 4 primary + Sonnet 4 subagents) beats a single-agent Opus 4 baseline by **+90.2%** on internal research evaluations, at a cost of **~15× the tokens** of a standard chat and **~4× the tokens** of a single-agent task *(Anthropic, "How we built our multi-agent research system", 2025)*. Token cost correlates with outcome value at **0.80+** with the rest of the variance explained by number of tool calls, model type, and agent count. The key architectural decision there is a central orchestrator that delegates to parallel specialists — not a free-form conversation among peers.

**Counter-evidence.** Cognition's "Don't Build Multi-Agents" argues that dividing context across agents loses the shared grounding needed for coherent output and leads to "committee of LLMs" pathologies. This is a real critique and it constrains the design space: it is valid for **depth-first, narrow-bandwidth** tasks where the whole problem fits in one context window and the cost of splitting exceeds the benefit of parallelism.

**Our resolution.** Multi-agent is a **structure, not a default.** Use it when the task (a) exceeds what one context can hold, (b) benefits from parallel search of solution space, or (c) requires specialist depth beyond generalist reach. Single-agent is the right call for narrow-bandwidth, tightly-scoped work. This PRD specifies the multi-agent case but architects both into §08 (parallel vs serial decision tree).

**Supporting frameworks (practice, not theory).**
- **AutoGen** *(Wu et al., Microsoft, 2023)* — conversable agents with an orchestrator pattern; demonstrates practical multi-agent scaffolding.
- **MetaGPT** *(Hong et al., 2024)* — Standard Operating Procedures encoded as multi-agent workflows. Key insight we borrow: **structured documents as the inter-agent communication contract**, not free-form dialog.
- **CrewAI / LangGraph** (industry) — role-based agents with explicit state machines.
- **ChatDev** *(Qian et al., 2023)* — waterfall software-company simulation. Instructive because its failure modes (compounding error across serial hops) directly motivate our hub architecture and swarm consensus.

## Pillar 2 — Mixture of Experts / Agents

**Architectural lineage.** Sparse Mixture of Experts *(Shazeer et al., 2017; Fedus et al., 2022 Switch Transformer)* proved that routing to specialists beats monolithic dense models on capacity-per-flop. GPT-4 and Claude 3/4 are widely believed to be MoE at the weight level.

**From MoE to MoA.** The Mixture-of-Agents paper *(Wang et al., Together AI, 2024)* shows that the same principle applies at the agent level: multiple LLMs each propose a response, a subsequent aggregator LLM combines them, and the result beats any constituent model on AlpacaEval and MT-Bench. MoA-Lite with 7B open-source models beats GPT-4 Omni on AlpacaEval-2.

**Design decision it justifies.** Cohort-scoped swarms (§06). Each swarm contains N specialist agents of the same domain with deliberate perspective diversity (different prompts, different models, different retrieval views). The swarm's output is a **confidence-interval consensus** aggregated by an orchestrator-layer model — not a majority vote, not a single-expert answer.

## Pillar 3 — Self-consistency and deliberation

**Self-Consistency** *(Wang et al., 2023)* — sample the same chain-of-thought query multiple times and take the majority answer. Improves GSM8K accuracy by ~17 points over greedy CoT. The principle generalizes: **an LLM's distribution of answers is a richer signal than any single sample.**

**Tree-of-Thoughts** *(Yao et al., 2023)* — branch-and-evaluate across reasoning trees with pruning. Game of 24 goes from 4% (CoT) to 74% (ToT).

**Debate** *(Irving et al., 2018)* — two agents argue opposite sides; a judge (or human) arbitrates. The theoretical frame: in the limit, debate makes truthful answers easier to recognize than to generate, because lies have to defend themselves.

**Design decisions these justify.**
- Per-swarm sampling (n ≥ 3, commonly n = 5) for confidence intervals (§09).
- Explicit adversary/skeptic role within cohort swarms to prevent echo-chamber (§06).
- Dissent is preserved, not averaged away (§09 output contract).

## Pillar 4 — Reflection and iterative refinement

**Reflexion** *(Shinn et al., 2023)* — after each attempt, an agent writes a verbal self-critique stored in episodic memory; subsequent attempts read it. HumanEval pass@1 jumps from ~80% to ~91%.

**Self-Refine** *(Madaan et al., 2023)* — same LLM generates, critiques, and revises its own output. Shows consistent uplift across reasoning tasks.

**Design decisions these justify.**
- Per-turn feedback cadence (§13): after every expert-agent turn, a Reflexion-style critique is appended to that agent's learnings section.
- Per-task retrospective cadence (§13): at end of task, an LLM judge reviews the campaign log and proposes concrete prompt diffs.
- Per-campaign eval-harness cadence (§13, §14): across a benchmark set, we compute Brier/ECE, drift, and completion metrics and update system-level configuration.

## Pillar 5 — Process supervision > outcome supervision

**Let's Verify Step by Step** *(Lightman et al., OpenAI, 2023)* — training reward models on per-step correctness (process reward models, PRMs) outperforms training on final-answer correctness (outcome reward models, ORMs). On MATH, a PRM-guided verifier achieves 78% vs 72% for ORMs.

**Design decisions it justifies.**
- Per-turn evals in §14: we don't wait until campaign end to score. Each expert-agent output is verifiable-check-tested at emission time.
- The deterministic verifier (§06) is the PRM analogue: it arbitrates claims at every hop.

## Pillar 6 — Context rot is real

**Lost in the Middle** *(Liu et al., 2023)* — LLMs given a long context find information better when it is at the beginning or end than in the middle. Retrieval accuracy in a 20-document context can drop 20+ points for documents in the middle.

**Context engineering** *(Anthropic, 2025)* — "the art and science of curating what will go into the limited context window from the universe of possible information." The key insight: **context is a budget, not free**. Every token the primary orchestrator sees competes for attention with every other token.

**Design decisions these justify.**
- Clean-context primary orchestrator (§06): only indexed, weighted, verified signals; no raw expert transcripts.
- Tiered memory (§10): working / hot / indexed / cold; load only what's needed at each tier.
- Summarization at cohort boundaries (§07): cohort sub-orchestrators emit packets for the primary, not the full agent log.

## Pillar 7 — Constitutional constraints

**Constitutional AI** *(Bai et al., Anthropic, 2022)* — train a model to critique its own outputs against a written constitution of principles, then refine. Reduces harmful outputs without hand-labeled harm data.

**Design decisions it justifies.**
- Guardrails layer (§12): every agent has a system-level constitution it is checked against, not just user-level instructions.
- Orchestrator-system validation (§06): outputs that violate the constitution are rejected before reaching the primary orchestrator.
- Distinction between "policy" (non-negotiable) and "preference" (soft): the former is constitutional, the latter is tunable per-campaign.

## Pillar 8 — LLM-as-Judge with calibration

**Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena** *(Zheng et al., 2024)* — GPT-4 as judge agrees with human judges ~80% of the time, comparable to inter-human agreement. Provides a scalable evaluation substrate *when calibrated*.

**Calibration via proper scoring rules** *(Brier, 1950)* — a Brier score rewards confidence only when the confidence is accurate. Expected Calibration Error (ECE) measures how well self-reported confidence matches actual accuracy over bins.

**Design decisions these justify.**
- Consensus aggregator in §09 uses LLM-as-judge for semantic-equivalence grouping.
- Verifier outputs feed a Brier/ECE calculator (§14) for continuous calibration.
- Confidence-interval reporting is a first-class output contract (§15 Consensus Packet schema), not a UI nicety.

## Secondary citations (mentioned in context, detailed in Appendix C)

- **Minsky, *Society of Mind* (1986)** — original motivation for specialist-agent composition.
- **Silver et al., AlphaGo (2016) / AlphaZero (2017)** — Monte Carlo Tree Search + self-play as a reference for branch exploration.
- **Prompt-injection literature** (Greshake et al. 2023, OWASP LLM Top 10) — motivates §12 guardrails and strict data-vs-instruction separation.
- **GAIA benchmark** *(Mialon et al., 2023)* — general AI assistant benchmark; referenced in §14.
- **SWE-bench** *(Jimenez et al., 2024)* — software-engineering benchmark; referenced in §14 and §18.
- **BrowseComp** *(OpenAI, 2025)* — browse-and-synthesize benchmark; referenced in §14.
- **MINT** *(Wang et al., 2024)* — multi-turn interactive benchmark with tool use.
- **NeMo Guardrails** *(NVIDIA, 2023)* — programmable guardrails; one adapter choice in §12.
- **Llama Guard** *(Meta, 2023 / v3 2024)* — classifier-based input/output safety; another adapter choice in §12.

## What this chapter does *not* attempt

It does not survey every agent framework, every prompting technique, or every eval benchmark. It cites the minimum set needed to justify the architecture's concrete choices. A PM or architect who wants to defend a choice that disagrees with ours starts with the citation in the table at the top — the paper is the interface.
