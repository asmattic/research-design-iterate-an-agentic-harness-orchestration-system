_Session handoff — written by the outgoing session at its end, read by the next session (human or agent) at its start. Semantics per WAYFINDER-DESIGN §5.5, adopting the /handoff skill's rules as normative: pointer-not-copy, redaction, suggested skills. The handoff may become another agent's prompt — write accordingly._

# Handoff — <campaign id> · <date/time>

## Destination and current phase

- Destination: <one line — INTENT's goal; do not restate the whole INTENT, link it>
- Phase: <wayfinding | execution> · <one line on where in the phase we stand>

## State pointers

NEVER duplicate content already in artifacts — reference specs, tickets, ADRs, and commits by path or URL. The next session zooms on demand.

- INTENT: <path>
- Map: <tracker URL or path>
- Spec (if synthesized): <path or URL>
- Relevant commits / branches: <refs>
- <other artifacts: ADRs, research branches, event-log ranges>

## Decisions since last handoff

One-line gists with links; detail lives in the ticket resolutions.

- <gist of decision 1> — <ticket ref>
- <gist of decision 2> — <ticket ref>

## Open frontier

Tickets claimable right now (open ∧ blockers closed ∧ unclaimed):

- <ticket ref> — <one line> — <type: grilling | prototype | research | task | implementation>
- <ticket ref> — <one line>

## Fog snapshot

Questions in scope but not yet stateable precisely:

- <fog entry 1 — loose phrasing is fine; that is what fog is>
- <fog entry 2>

## Ruled out of scope since last handoff

- <gist> — <reason> — <ticket ref if any>

## Suggested skills for the next session

- <skill or workflow 1 — and why it fits the next ticket>
- <skill 2>

## Redaction rule

Before writing this file, strip all API keys, passwords, tokens, and PII. Reference secrets by the name of their storage location, never by value. If a needed value is sensitive, say where the next session can obtain it, not what it is.

_Template: harness-reference v0.2.0 · see prd/ and WAYFINDER-DESIGN.md for rationale_
