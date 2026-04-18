# 07 · Communication Topology — Hub vs Mesh

## The question, phrased in terms the principal will recognize

> "Is this architecture more analogous to Redux — where all updates route through a single reducer so every subscriber sees a single coherent state tree — or to a peer-pub/sub mesh where each agent subscribes to each other's emissions directly?"

That's not rhetorical. The answer has consequences for drift, cost, auditability, and the ability to onboard a new agent type later. This chapter picks **hub** (state-tree, Redux-analogue) as the default, and states the specific exceptions where a bounded peer pattern ("caucus") is allowed.

## The short answer

**Default topology: hub-and-spoke (state-tree).**
- All agent emissions pass through the Orchestrator System.
- The Orchestrator System is the single source of truth for what any other agent sees about another agent's work.
- Agents *never* subscribe to each other's raw output; they consume packets the Orchestrator System has produced.
- This is directly analogous to Redux's single-store model: actions → reducer → state → subscribers. The reducer (Orchestrator System) is the arbiter; the state (campaign memory + packets) is the single source of truth.

**Bounded exception: caucus.**
- A cohort sub-orchestrator may grant its member experts *scoped peer visibility* within the cohort for a single task, if (a) the task requires tight real-time iteration (e.g., debate, adversarial refinement), and (b) the caucus is time-boxed and turn-count-bounded, and (c) the caucus transcript is still summarized by the cohort before it leaves the cohort boundary.
- Cross-cohort peer chat is forbidden. It compounds drift.

## Why not mesh

**Intuition.** Mesh seems more "intelligent" — agents talk to each other, refine collaboratively, emerge a better answer. It's the Society of Mind ideal.

**Empirical counter.** In practice, peer meshes produce:

1. **Drift.** Each pairwise exchange adds a small distortion; N² exchanges compound to large distortion. The rental toolkit's evolution away from this pattern is representative.
2. **Hallucinated agreement.** Without mediation, agents echo each other's plausible-but-wrong premises. This is F4 (echo chamber).
3. **Opaque accountability.** When the campaign goes sideways, a mesh has no single log. A hub has the event log (§15).
4. **Unbounded cost.** Peer-to-peer chat has no natural termination. A hub can enforce a budget per packet.

**Theoretical counter.** Debate *(Irving et al., 2018)* works when there is an arbiter (judge). Remove the arbiter and debate degenerates. Our Orchestrator System is the arbiter.

**Citation.** Cognition's critique ("multi-agent divides context") is partly correct about mesh — peer-to-peer agents don't share context well. Anthropic's response is partly a refutation ("orchestrator-worker pattern works") — because the orchestrator-worker pattern *is* a hub, not a mesh. Both sides of this industry debate are converging on the hub architecture under different vocabulary.

## Why hub-and-spoke with an Orchestrator System

1. **Auditability.** One place to look when asking "why did the campaign decide X?" — the event log + the packet stream.
2. **Budget enforcement.** The hub enforces token/latency budgets per packet, per cohort, per campaign.
3. **Clean-context primary orchestrator.** The hub is what makes §6.3 possible.
4. **Pluggability.** New agent types onboard by implementing the Agent Contract (§15); they don't need to know about other agents.
5. **Eval tractability.** The eval harness (§14) has one stream to score. Meshes are a nightmare to eval.

## The Redux / Zustand analogy, slightly more precisely

| Redux / Zustand | This harness |
|---|---|
| Action | Agent Emission |
| Reducer | Orchestrator System (BS detector → validator → attributor → context manager) |
| Store | Tiered Memory + Event Log |
| Subscriber | Primary Orchestrator (and any cohort that needs a slice) |
| Middleware | Guardrails, drift detector |
| DevTools / time-travel | Event log replay for retrospectives |

The analogy is not perfect — LLM agents are stochastic producers, not deterministic action creators — but it captures the discipline we want: **all state changes flow through a single, observable, policy-checked reducer.**

## Where the architecture differs from naïve Redux

1. **Verifier is external.** Unlike a pure reducer, we run a deterministic verifier as a separate service and fold its result into the state update. This is closer to Redux-saga's effect-runner pattern.
2. **Signal weighting is probabilistic.** Two agents can emit contradictory claims; the reducer doesn't pick one and discard the other — it emits a consensus packet with intervals and preserved dissent.
3. **Drift detection is a first-class middleware.** It reads state, computes distance from INTENT, and can *pause* the campaign (not just log).

## Caucus — the bounded peer exception

Sometimes experts need to iterate in real time — adversarial debate, pair programming, pro/con analysis. A caucus allows this under strict conditions:

**Bounds:**
- Scope: within-cohort only. Cross-cohort caucus is forbidden.
- Turns: capped per task (default: 6 turns).
- Tokens: capped per caucus (default: 20K).
- Time: wall-clock capped (default: 2 minutes).
- Output: caucus transcript is summarized by the cohort sub-orchestrator into a consensus packet before it crosses the cohort boundary. The primary orchestrator never sees raw caucus transcripts.

**When to use:**
- Debate (two experts + judge) for a contested question.
- Pair programming between a code-author expert and a code-reviewer expert.
- Adversarial refinement (generator ↔ critic).

**When not to use:**
- Any task where the experts can work in parallel without real-time interaction.
- Any task that crosses cohort boundaries.
- Any open-ended brainstorming (cost runs away).

## Diagram references

- **D03 (Hub topology)** — default architecture.
- **D04 (Caucus — bounded peer exception)** — the scoped-mesh pattern within a cohort.

## Decision rule, one line

> If two agents need to share information, the default path is **hub**. Peer visibility is an exception requested by the cohort, approved by the Orchestrator System, time-boxed and token-boxed, and always re-serialized at the cohort boundary.
