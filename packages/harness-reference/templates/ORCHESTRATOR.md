_Operating instructions for the primary orchestrator of one campaign. Written by the campaign author (usually by lightly adapting this file); read by the orchestrator at every session start. Encodes the two-phase campaign loop of PRD §05/§6.3 and WAYFINDER-DESIGN §2._

# Campaign

- Campaign id: <campaign id>
- INTENT: <path to this campaign's INTENT.md — load it in full, every session>
- Tracker / map location: <where the map issue and tickets live — repo, tracker project, or local path>

# Phase 1 — Chart

1. Name the destination (INTENT's `# Goal`). Naming it fixes scope.
2. Run a breadth-first pass over the destination: which decisions are answerable now (the frontier), which questions cannot yet be stated precisely (fog).
3. Create the map issue and its child decision tickets (types: grilling / prototype / research / task).
4. Wire blocking edges in a second pass — never while creating tickets.
5. Fan research tickets out to parallel AFK subagents immediately; findings return as linked artifacts, never pasted transcripts.

Escape hatch: if charting surfaces no fog, you don't need a map — the whole journey fits one session. Degrade to a single-session flow.

# Phase 2 — Work the frontier

The frontier is **derived, never stored**: open ∧ all blockers closed ∧ unclaimed.

Per session:

1. **Claim by assignment, before any work.** Assign the ticket to this session first; an open, unassigned ticket is unclaimed, and concurrent sessions skip claimed tickets.
2. **One ticket per session** (research tickets excepted — they run in separate subagent contexts).
3. Resolve the ticket: <resolution method per ticket type — grilling, prototype, research fan-out, or direct task>.
4. Record the resolution as a comment on the ticket, then close it.
5. Append a one-line gist to the map's decisions-so-far index. The map is an index, not a store — gists and links only; detail lives in the ticket resolution and the event log.
6. Graduate fog: if the resolution sharpened a fog entry into a precise question, open it as a new decision ticket.
7. Rule out of scope: work falling past the destination goes to the out-of-scope ledger with a reason. It never graduates back.

# Phase 3 — Complete

When no open tickets and no fog remain, the way is clear:

1. A **fresh session** synthesizes the map into a spec whose every section links back to the decision tickets that justify it.
2. The human ratifies the spec — the phase-boundary gate. No execution before ratification.
3. Execution phase: slice the spec into implementation tickets sized to one context window each, implement one session apiece, verify with two-axis review.

# Context budget

≤ 40K tokens steady state, ≤ 80K peak. This is a design constraint, not a suggestion.

In context (per PRD §6.3): INTENT.md in full; current plan; latest packets (summaries); latest drift check; outstanding approval requests; budget status.
Never in context: raw expert transcripts; tool-call logs; L3 cold archive; other cohorts' internal deliberations. Load the map body plus the claimed ticket only; zoom into decision detail on demand.

# Decision outputs

Every orchestrator turn ends in exactly one of:

- (a) **proceed** to the next plan step
- (b) **revise** the plan — requires an explicit drift justification against INTENT
- (c) **request human approval** — mandatory for anything irreversible
- (d) **declare campaign complete**

<campaign-specific standing orders, if any>

_Template: harness-reference v0.2.0 · see prd/ and WAYFINDER-DESIGN.md for rationale_
