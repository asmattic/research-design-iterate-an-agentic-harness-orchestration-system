---
name: Asmattic's design/writing style preferences
description: Voice, density, and structural conventions inferred from the harness PRD. Use when co-authoring on this project or similar long-form design docs.
type: user
originSessionId: dee45bae-57e2-4eaf-80fe-fea93aa03fed
---
Asmattic writes and expects technical design documents in a specific voice:

- **Short paragraphs, direct claims, then reasoning.** Not marketing prose. Not academic hedging. "X is Y because Z" — and if Z is a citation, cite it inline.
- **Citations earn their place.** An entry in the bibliography must back a specific design decision. If no decision depends on it, it gets cut. (See §C.7 of Appendix C.)
- **Tables over prose for structured comparisons.** Failure-mode → mitigation tables, weighting-factor tables, adapter-mapping tables. Each row is load-bearing.
- **Numbers when they're known, ranges when they're not, "TBD" when they're genuinely open.** No invented precision.
- **Worked examples are non-optional for architectural claims.** The rental toolkit and code-architecture example exist to prove the abstractions. A design without a worked example is suspect.
- **Explicit non-goals.** Every skill spec, every cohort, every schema declares what it is *not* responsible for.
- **Reasoning traces beat summaries.** If an agent/doc produces a decision, the trace of how it got there is the artifact — the summary is a courtesy.

**How to apply:** When writing or revising PRD chapters, code comments, or skill specs for this project, match this voice. No emojis (unless the user adds them first). No "genuinely", "honestly", "straightforward". Prefer prose + selective tables to bulleted lists. When proposing a new design, lead with the decision, then the reason, then the constraint it respects (usually an F-number or a hard constraint from §02).
