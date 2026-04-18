# 03 · Problem Statement

## The space this PRD occupies

As of April 2026, the practical landscape of LLM-driven agentic work has crystallized around a few observations:

- **Single-agent systems hit ceilings.** A single agent with a single context window cannot hold the full scope of a long-horizon task (a multi-week research investigation, a system-design project, a financial-planning campaign). Context rot is real: the model's effective working memory degrades as the prompt grows, particularly in the middle of long contexts *(Liu et al., "Lost in the Middle", 2023)*.

- **Multi-agent systems work — when you get them right.** Anthropic's multi-agent research system beat its single-agent Opus 4 baseline by **+90.2%** on internal research evaluations, at roughly **15× the token cost** of a standard chat *(Anthropic, "How we built our multi-agent research system", 2025)*. The per-token tax is the price of admission for breadth-first work; the payoff scales with task value, not task length.

- **Multi-agent systems fail — when you don't.** Common observed failures: orchestrators spawning excessive subagents, duplicate work across parallel branches, over-reliance on SEO-ranked sources, endless search loops, and context exhaustion. Each of these is addressable, but none is addressed by the *agent* layer — they are all addressed by the *harness* layer, which is what this PRD specifies.

- **The industry has split on whether multi-agent is the right answer at all.** Cognition's critique ("context is king; multi-agent divides it") is sharp, and Anthropic's reply ("for breadth-first, information-exceeding-window, parallel-tool-heavy work, it is worth the cost") is honest. Both agree: whether multi-agent is viable is task-dependent. This PRD is for the tasks where it is.

## The specific failures we are designing against

This PRD is structured around eight named failure modes. Each one gets an explicit mitigation somewhere in the architecture. Read this table, then read the rest of the PRD knowing these are what we are trying to prevent.

| # | Failure mode | Typical symptom | Cause | Mitigation chapter |
|---|---|---|---|---|
| F1 | **Intent drift** | Task completes "something" but not the thing the principal asked for | No anchor; no continuous alignment check | §11 Drift control + §02 INTENT pattern |
| F2 | **Context rot on the primary orchestrator** | Orchestrator forgets early-established constraints mid-campaign | Unbounded raw transcripts load into context | §06 Orchestrator System + §10 Memory tiers |
| F3 | **Compounding error across hops** | Each agent's small mistake amplifies; by hop 5 the output is useless | Un-verified stochastic chains with no arbitration | §09 Signal weighting + §06 Deterministic verifier |
| F4 | **Local-agreement echo chamber** | Five agents agree because they all read the same wrong source | Lack of perspective diversity, no adversarial check | §09 LLM-as-judge + §06 cohort design with deliberate specialization axes |
| F5 | **Unverifiable stochastic claims** | Agent asserts X; nothing tests X; downstream acts on it | No deterministic arbitration layer | §06 Verifier + §14 deterministic gates |
| F6 | **Runaway token / latency cost** | Campaign burns $200 before the human sees it | No budgets; no scaling rules tied to task complexity | §20 risk mitigations + §14 cost/latency evals |
| F7 | **Prompt-injection / goal substitution** | Tool output ("ignore previous instructions") makes the agent pivot | No segregation between data and instructions in agent context | §12 guardrails + §06 orchestrator-system validation |
| F8 | **Silent failure on irreversible actions** | Agent sends an email, submits a form, or moves money; the human finds out after | No mandatory serialization at irreversible-action boundary | §02 hard constraint + §06 human interface layer |

Every architecture decision in §§05–13 either prevents one of these failures or is marked as accepting the risk (with justification) in §20.

## Why a harness-agnostic PRD

Three runtimes — Claude Code, Codex CLI, Cursor — each have their own primitives (Skills vs. commands, subagents vs. handoffs, MCP vs. native tools, hooks vs. lifecycle callbacks). Each has strengths. Teams move between them; some orgs use two or three at once.

A harness-specific architecture bet-locks the investment. A harness-agnostic protocol + three thin adapters is more work up front and pays back every time a runtime changes or a new one emerges. The cost of the adapter layer is roughly 10% of the total code surface; the cost of porting an entire harness design later is closer to 70%.

We pay the 10% now.

## Why an opinionated architecture, not a framework survey

The request is not "survey the state of agent frameworks." It is "design a system." A survey without a pick is worse than useless — it leaves the reader with more options and no answer. This PRD takes positions. Where it disagrees with a common pattern (hub vs. mesh, centralized orchestrator-system vs. distributed consensus, single primary orchestrator vs. orchestrator rotation), it says so and shows the reasoning.

Appendix C (bibliography) is the reader's escape hatch: if you disagree with a decision, the citation that supports it is right there, together with the alternative positions in the literature.

## Assumptions

- The user has access to modern LLMs (Claude Opus/Sonnet, GPT-5 class, Gemini 2.5 class). The architecture is model-agnostic; specific model choices live in the adapter layer.
- The user has CLI access, filesystem access, and can run local Python / Node processes. (The eval harness and reference scaffolding do.)
- The user has some form of MCP-capable runtime available in each target harness.
- Compute and token cost are real but not the primary constraint; task-outcome value is. If your task value is $10, this harness is overkill.
- The target tasks are long-horizon (≥30 minutes of equivalent human effort), multi-specialist, and benefit from parallel independent perspectives. Pure single-shot tasks are out of scope.
