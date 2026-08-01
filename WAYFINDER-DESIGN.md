# Wayfinder as the Orchestrator Loop

_Design doc · drafted 2026-07-31 · status: draft for ratification_

**Decision being recorded:** the harness orchestration system's campaign loop is re-based on the **wayfinder** skill from `mattpocock/skills` — adopting its field-tested mechanics as the reference semantics for the orchestrator loop, and positioning the harness as the system that automates what wayfinder currently leaves manual.

**Sources.**

- `skills/engineering/wayfinder/SKILL.md` at the synced fork (`asmattic/skills` @ `6765cf6`, local clone `~/dev/mattpocock-skills`). Supporting skills: `handoff`, `to-spec`, `to-tickets`, `implement`, `code-review`, `research`, `grilling`, `domain-modeling`.
- Video: "mattpocock/skills: A complete AI Coding workflow, end-to-end" (`youtube.com/watch?v=M6mYodf0dJM`) — the main flow.
- Video: "LIVE: The /wayfinder Demo" (`youtube.com/watch?v=251hsWgoTPM`) — a full map charted and worked live, including parallel sessions.
- Written breakdown: `aihero.dev/skills-wayfinder`.

---

## 1 · Why base on wayfinder

Wayfinder is the closest existing artifact to this PRD's orchestrator loop that has real-world mileage: the skills repo reports 162K stars and 7.5M downloads, the author runs his production content platform on it, and it already spans harnesses (Claude Code, Codex, Cursor — every skill ships `agents/openai.yaml` metadata). Its author's framing on stream — *model ⊂ harness ⊂ environment; improving the harness and environment is free leverage* — is this project's thesis (§03, §05).

Basing on it buys three things:

1. **Reference semantics with evidence.** Instead of inventing an orchestrator loop and validating it in Round 2 evals, we formalize a loop that demonstrably works at the "100 sessions against one map" scale (his course-planning campaign) and produces implementable specs (the 5,000-line PR driven ticket-by-ticket from a wayfinder-derived spec).
2. **A concrete interop target.** A campaign whose state lives in an issue tracker as a map + tickets is inspectable by humans with zero custom UI, and by any harness with tracker access. This partially answers open questions Q10 (human-gate UX) and Q13 (external-ecosystem interop) in §22.
3. **A differentiation list, from the source.** The pain points Pocock names on stream (§6 below) are precisely the gaps this harness exists to fill. Wayfinder is the protocol; we build the orchestrator that runs it.

## 2 · The wayfinder loop, restated in PRD terms

Wayfinder plans work "more than one agent session can hold" as a **shared map** of **decision tickets** on an issue tracker, worked until "the way to the destination is clear." Restated in this PRD's vocabulary:

1. **Chart** — a grilling session pins the **destination** (≈ the campaign's `INTENT.md` goal statement: usually "a decision-complete spec," explicitly not execution). A second breadth-first grilling pass maps the **frontier** — decisions answerable now — and sketches the **fog** (known-unknowable-yet). The map issue and its child tickets are created; blocking edges are wired second-pass; **research tickets are immediately fanned out to parallel subagents** (≈ AFK cohort dispatch).
2. **Work** — each session claims exactly one ticket (claim = tracker assignment, made *before* any work so concurrent sessions skip it), resolves it (grilling / prototype / research / task), posts the answer as a resolution comment, closes the ticket, and appends a one-line pointer to the map's **Decisions so far** index. Resolution graduates fog into new tickets, or rules work **out of scope** when it falls past the destination.
3. **Complete** — no open tickets, no fog: the way is clear. A fresh session runs `to-spec` against the map, producing a spec whose every section links back to the decision tickets that justify it ("context pointers the agent can walk down"). The map is closed. `to-tickets` slices the spec into implementation tickets sized to one context window; `implement` executes them one session each (AFK-capable — Pocock runs them via GitHub Actions); `code-review` runs two parallel sub-agent axes over the whole diff; then human review.

The load-bearing type distinction, quoted from the live demo: *"decision tickets can only be resolved by making the decision; implementation tickets are when those decisions are reified in the code."* A campaign therefore has two phases with different packet kinds — **wayfinding (decide)** then **execution (build)** — and the spec is the boundary artifact between them.

## 3 · Concept mapping

| Wayfinder mechanic | PRD concept | Ref |
|---|---|---|
| Destination (named first; fixes scope) | `INTENT.md` goal + "what done looks like" | §6.2 |
| Map issue (index, not store; gists + links only) | Orchestrator State snapshot; pointer-not-copy memory discipline | §6.3, §10 |
| Decision ticket | Packet-producing task in the wayfinding phase | §15 |
| Ticket types: grilling / prototype / research / task | Task taxonomy; HITL vs AFK = human-gate flag per task | §6.1, Q10 |
| Frontier = open ∧ unblocked ∧ unclaimed | Scheduler dispatch predicate | §6.3 |
| Claim-by-assignment, claim-before-work | Concurrency/claim protocol for parallel sessions | §07 |
| Native blocking edges, rendered by the tracker | Dependency graph with zero-custom-UI human visibility | Q10 |
| Fog of war / "Not yet specified" | Explicit uncertainty ledger (test: *can the question be stated precisely?* — not answered) | §22 pattern |
| "Out of scope" section (never graduates) | Non-goals enforcement; drift boundary | §6.2, §11 |
| Decisions-so-far one-line index | Event-log-backed decision index (L2 pointer into L3 detail) | §10 |
| Research subagents fanned in parallel, findings on research branches | AFK cohort fan-out; artifacts linked, not pasted | §6.5, §6.6 |
| One ticket per session; "smart zone" ≈ 140K tokens | Context budget as design constraint (primary: ≤40K steady) | §6.3 |
| `to-spec` from the map in a fresh session | Synthesis/consensus stage; spec = ratified packet set | §09 |
| `code-review` two axes in parallel sub-agents, **no cross-axis reranking** | Perspective-diverse verification; preserved dissent — a two-expert instance of the no-silent-overwrite rule | §09, §6.6 |
| `handoff` (pointer-not-copy, redaction, suggested-skills) | `HANDOFF.md` template semantics | §23.1 |
| `setup-matt-pocock-skills` tracker-ops doc | Adapter configuration pattern: capability doc per environment | §16 |

## 4 · What wayfinder lacks — what the PRD adds

The mapping is not symmetric. Wayfinder has **no deterministic verification, no calibration, no measured drift, and no automated consensus** — the human *is* the orchestrator system. The PRD layers on top, without changing the loop:

- **Deterministic verifier precedence** (§6.7): wayfinder resolutions are accepted on the human's say-so; the harness routes testable claims through the verifier before a ticket may close.
- **Confidence-interval consensus + three-valued outcomes** (§09): research-ticket findings arrive as single-agent reports; the harness can swarm them and preserve dissent in the resolution comment.
- **Drift detection** (§6.4.6): wayfinder's out-of-scope section is a *manual* drift boundary; the harness measures distance from the destination continuously and alarms.
- **Calibration and weight-tweaking** (§6.4.4–6.4.5): repeated campaigns should learn which ticket-resolvers to trust.
- **Guardrails and the event log** (§12, §10): tracker comments are the human-visible trace; the JSONL event log remains the auditable ground truth beneath them.

This division is clean: **wayfinder = the loop and its human ergonomics; harness = the quality, safety, and automation machinery around each loop step.**

## 5 · Design changes to adopt (Round 2 re-base)

### 5.1 Two-phase campaign model
Introduce the **wayfinding phase** (decision packets) preceding the **execution phase** (implementation packets) as first-class campaign structure. The spec produced by `to-spec` is the phase-boundary artifact and requires human ratification (existing §6.1 gate). Chapters affected: §05, §06, §15.

### 5.2 Orchestrator State ⊇ the map
`orchestrator-state.schema.json` (v0.2.0) gains map semantics:

- `destination` (string, immutable per effort — mirror of INTENT's goal)
- `decisions[]` — index entries: `{ticket_ref, one_line_gist}` (pointer-not-copy; detail lives in the event log / tracker)
- `fog[]` — loosely-stated coming questions (the "Not yet specified" ledger)
- `out_of_scope[]` — `{gist, reason, ticket_ref?}` (never graduates)
- `tickets[]` — `{ref, type: grilling|prototype|research|task|implementation, mode: hitl|afk, status: open|claimed|closed|out_of_scope, blocked_by[], assignee?}`

The **frontier is derived, never stored**: `open ∧ blocked_by all closed ∧ unclaimed`.

### 5.3 Claim protocol
Adopt claim-by-assignment verbatim: a session assigns the ticket to itself **before any work**; an open unassigned ticket is unclaimed. Add event kinds to the event envelope: `ticket_claimed`, `ticket_resolved`, `fog_graduated`, `scope_ruled_out`.

### 5.4 One-ticket-per-session as budget discipline
Encode wayfinder's rule (one ticket per session, research excepted) as the default execution policy in `ORCHESTRATOR.md`, justified by the same context-rot evidence already cited in §6.3. Research tickets are exempt because they run in *separate* subagent contexts.

### 5.5 Template set re-base (§23.1 deliverables)
- **`INTENT.md`** — unchanged structure, but §6.2's "Goal" is explicitly the wayfinder destination, and "Non-goals" seeds the map's out-of-scope section.
- **`ORCHESTRATOR.md`** — encodes the loop of §2 above: chart → work frontier → graduate fog → complete → synthesize spec → execute → review.
- **`HANDOFF.md`** — adopt the `/handoff` skill's rules as normative: no duplication of content already in artifacts (reference by path/URL), sensitive-data redaction, and a "suggested skills for the next session" section.

### 5.6 Verification stage adopts the no-rerank rule
`code-review`'s explicit prohibition — *"do not merge or rerank findings across axes; that's the reranking the separation exists to prevent"* — generalizes to the consensus layer: axis-scoped verdicts are reported side by side; only within-axis aggregation is permitted. Fold into §09.

### 5.7 Adapter alignment (§16, Appendix E)
- Adopt the **tracker-ops doc pattern**: the adapter's setup step writes a per-repo capability doc (which tracker, how to query the frontier, how to wire blocking) that skills consult at run time — this is how wayfinder achieves GitHub/GitLab/Linear/Jira/local-markdown portability with one skill body.
- The six Appendix-E skills remain, but two get wayfinder-facing triggers: `harness-drift-detector` runs at ticket-resolution time against the destination; `harness-context-manager` implements the map-is-index load discipline (map body + claimed ticket only; zoom on demand).
- Author all six against `writing-great-skills` (its failure-mode vocabulary, e.g. Negation, is the best available style guide for predictable skills).

## 6 · The automation gap = the product

Pain points Pocock states on stream, each mapping to a harness component that closes it:

| Pain point (his words, paraphrased) | Harness answer |
|---|---|
| Spawning a session per ticket is manual copy-paste — "I do want to make this less manual" | Scheduler: frontier query → auto-spawn session per unblocked ticket, claim on spawn |
| Worktree/env state across parallel sessions is "brutal"; wants remote sandboxes | Execution-environment manager in the adapter layer (worktree lifecycle; sandbox/VM backends later) |
| "You often have to ask if you're done yet" — no needs-input/done signals | Event-log-driven notifications; HITL tickets surface as approval requests (Q10) |
| Cross-session decision conflicts brokered by hand ("point the sessions at each other") | Hub topology (§07): resolutions route through the orchestrator; drift/consistency check on each `ticket_resolved` event |
| Auto-approval classifier blocks tracker writes mid-flow | Adapter pre-approves the tracker-ops command surface declared in the capability doc |

## 7 · Risks

| Risk | Mitigation |
|---|---|
| Upstream churn — the skill was renamed twice in three months (decision-mapping → wayfinding → wayfinder) and its mechanics still move weekly | Pin semantics to fork commit `6765cf6`; treat upstream as input to revisions, not a moving dependency. The schema, not the skill text, is normative for us. |
| Attribution/licensing | `mattpocock/skills` grants a standard open license; cite prominently (this doc, §00, and Appendix C). We formalize concepts; we do not vendor his prose. |
| Informal semantics vs. formal schema mismatch (e.g., wayfinder tolerates a human bending the rules; a schema cannot) | Where the skill is loose, the PRD decides and records the delta in this doc's successor chapter; conformance tests target our schema only. |
| Two-phase model adds ceremony to small campaigns | Adopt wayfinder's own escape hatch: if charting surfaces no fog, there is no map — degrade to a single-session flow (his "you don't need a map" rule). |

## 8 · Follow-on work

1. Amend **§05 / §06 / §09 / §15** per §5 above; add the loop as a new diagram (`D12-wayfinder-loop.mermaid`) and register it in Appendix A. Any chapter count change must update `DOC_MANIFEST` in the same commit (CI `prd-shape`).
2. Record answered fractions of **Q6, Q10, Q13** in §22 with pointers here.
3. Add Pocock's repo + both videos to **Appendix C** (bibliography).
4. Round 2 scaffolding order is unchanged (schemas first), but `orchestrator-state.schema.json` now lands with the §5.2 map fields, and the recorded-campaign integration test replays a small wayfinder map end-to-end.
