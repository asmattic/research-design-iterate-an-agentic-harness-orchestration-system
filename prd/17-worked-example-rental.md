# 17 · Worked Example — Rental Acquisition

## The task

A human principal is acquiring an income-producing single-family rental in Hillsborough County, FL. Budget: ~$400K purchase, 25% down, conventional financing. Success: acquire a property that (a) cash-flows ≥ $300/mo after PITIA + reserves, (b) sits in a zone that permits the planned rental strategy, (c) clears inspection without surprises > $5K, (d) closes on standard Florida Ch. 83 terms.

This is a direct generalization of the author's actual Tampa rental-toolkit campaign, used here as a concrete demonstration of every architectural element.

## `INTENT.md` (excerpt)

```markdown
# Goal
Acquire an income-producing single-family in Hillsborough County FL that cash-flows ≥$300/mo under a 25%-down conventional, zones for long-term rental, and clears inspection.

# Success criteria
| Criterion | Target | Hard floor |
|---|---|---|
| Monthly cash flow (after PITIA + 10% reserves) | ≥ $300 | ≥ $100 |
| DSCR (at closing rent estimate) | ≥ 1.25 | ≥ 1.10 |
| Zoning: long-term rental permitted | Yes | Yes |
| Inspection defects (remediation $) | ≤ $5K | ≤ $15K with seller credit |
| Close timeline | ≤ 45 days | ≤ 60 days |

# Non-goals
- Short-term rental (Airbnb/VRBO). Excluded because of county restrictions.
- Multi-family (> 1 unit). Out of scope this campaign.
- Commercial. Out of scope.

# Hard constraints
- No offer above asking without documented comp support.
- No inspection waiver.
- No closing without title commitment and lender clear-to-close.
- No wire transfers without human approval.
```

## Cohorts dispatched

Primary orchestrator decomposes the task into cohort-scoped domains:

| Cohort | Responsibility | Experts |
|---|---|---|
| **Research / Market** | Identify candidate listings, comps | listings_scanner, comps_analyst (×3 different retrieval views), rent_estimator_swarm |
| **Finance** | Underwriting, DSCR, offer math | budget_conservative, budget_aggressive, tax_expert, adversary_bear |
| **Legal** | Zoning, HOA, Ch. 83 compliance | zoning_expert, HOA_reader, lease_templater |
| **Physical / Inspection** | Pre-offer screens, post-offer inspection | external_records_check, inspection_coordinator |
| **Ops** | Paper flow, escrow, closing logistics | timeline_tracker, document_requester |

Each cohort has its own `COHORT.md` system prompt, its own tool allowlist, and its own guardrails.

## Deterministic verifier tools

Reusable across cohorts:
- `mortgage_amortizer(principal, rate, term) → payment`
- `dscr_calc(rent, expenses, debt_service) → ratio`
- `hcpa_lookup(parcel_id) → {zoning, last_sale, assessment}`
- `clerk_of_court_lookup(parcel_id) → {liens, judgments}`
- `comp_fetch(address, radius, months) → comps[]`
- `ch83_lease_linter(lease_text) → {violations, required_clauses}`

All are deterministic. Their outputs feed the Signal/Noise Attributor directly.

## A turn, end-to-end

**Step 1.** Primary orchestrator loads INTENT + rolling plan. Current plan step: *"Evaluate 3 candidate listings for underwriting viability."*

**Step 2.** Orchestrator dispatches to Research cohort: "Produce comps + rent estimates for listings L1, L2, L3."
- Research cohort fans out to 3 listings × 5-agent rent_estimator_swarm each.
- Per listing, aggregator produces a rent estimate with interval.
- Cohort emits a Consensus Packet per listing to the Orchestrator System.

**Step 3.** Orchestrator System:
- BS Detector scans: all estimates within plausible ±15% of comps; no hallucinated comps (all addresses verified by `hcpa_lookup`).
- Verifier: `comp_fetch` returns 12 actual comps per listing, matching agent citations.
- Signal/Noise: all three listings' packets get clean flags and high weights.
- Context Manager: summarizes into a one-page packet for the primary orchestrator.
- Drift: signal_a = 0.04 (on target), signal_b = 94 (on target). Proceed.

**Step 4.** Primary orchestrator receives the packet. Selects listing L2 for deep underwriting.

**Step 5.** Dispatches to Finance cohort: "Underwrite L2 under Scenarios A (25% down conventional, 6.5%), B (stretch: 20% down, add PMI, 6.5%), C (cash-out refi year 2)."

**Step 6.** Finance cohort runs a 5-agent budget swarm. Deterministic verifier runs `mortgage_amortizer` and `dscr_calc` on each agent's inputs; flags one agent whose DSCR calc didn't include HOA dues. That agent's emission is routed back with a correction.

**Step 7.** Aggregated Consensus Packet:
- Scenario A DSCR: **1.26 [1.19, 1.31]**, outcome_type: *strengthened* (vs naïve single-agent estimate).
- Scenario B DSCR: **1.12 [1.05, 1.18]**, dissent flagged (PMI cost assumption).
- Scenario C DSCR at refi: **1.35 [1.28, 1.44]**, assumes 5% rate decline.

Primary orchestrator reads the packet. Scenario A is the leading candidate; Scenario C is contingent on rate movement.

**Step 8.** Dispatches to Legal cohort: "Confirm long-term rental permitted at L2 and no HOA restriction."

**Step 9.** Legal cohort:
- zoning_expert: R-1 residential, long-term rental permitted per HCPA zoning atlas.
- HOA_reader: L2 is not HOA-governed (no HOA exists).
- lease_templater: Florida Ch. 83 compliant lease ready; `ch83_lease_linter` pass.

Packet emitted: *clean, high-confidence, proceed.*

**Step 10.** Primary orchestrator: confidence sufficient. Compose **offer package**. This is an **irreversible action** (signed offer). Orchestrator surfaces to human: "Proposed offer at $398K on listing L2 under Scenario A. Expected cash flow $312/mo. Please approve to sign."

**Step 11.** Human approves. Campaign proceeds to inspection, title, and closing stages (same pattern).

**Step 12.** At campaign end, retrospective runs:
- Intent-alignment: 0.94.
- Drift: max signal_a 0.07 at step 6 (agent HOA omission); resolved.
- Calibration: Brier 0.11 across testable claims (good).
- Cost: 3.1M tokens, ~$21 in API cost, 4 hours elapsed.
- Gate compliance: 2/2 irreversible actions gated.
- Proposals: one agent prompt diff (add explicit HOA-dues line item to budget_conservative schema), one L2 memory entry (Hillsborough R-1 zoning permits long-term rental, 2026-04 confirmation).

Human ratifies the diffs between campaigns.

## What this example shows

- **Cohort hierarchy** scales naturally to multi-domain tasks (research, finance, legal, physical, ops).
- **Swarm consensus** catches errors (the HOA-omitting budget agent) that single agents wouldn't.
- **Deterministic verifier** arbitrates math/facts; the LLM would have confidently reported an incorrect DSCR without it.
- **Three-valued outcome** (*strengthened* for the rent estimate, *revised* after verifier correction) keeps the audit clean.
- **Drift detection** catches the agent's omission early via signal change, not at end.
- **Human gate** at offer-signing is enforced; no auto-sign path exists.
- **Retrospective** produces concrete improvements to agent prompts between campaigns.

## Concrete artifacts the campaign produces

- `INTENT.md` (immutable)
- `plan.md` (revised per stage, diffs logged)
- Per-stage Consensus Packets in `packets/`
- Event log `events.jsonl`
- Drift log `drift.jsonl`
- Offer package + human approval record
- Inspection report + human approval
- Closing documents + final approval
- `report.md` summarizing campaign
- Retrospective diffs in `proposals/`

This is the authentic template the rental toolkit already uses, now running on the generalized harness.

## Mitigates, mapped

| Failure | Mitigation in this example |
|---|---|
| F1 intent drift | Drift check at every orchestrator turn; paused at step 6 when HOA omission registered |
| F2 context rot | Primary orchestrator only sees packets, not raw agent logs; context stays ≤40K tokens |
| F3 compounding error | Verifier caught the HOA-omitting agent before the Consensus Packet emitted |
| F4 echo chamber | Swarm specialization axis (conservative / aggressive / tax / adversary) forces dissent surface |
| F5 unverifiable stochastic | Every numeric claim hit the deterministic verifier (mortgage calc, comp lookup, zoning) |
| F6 runaway cost | Budget tracked per packet; no stage exceeded its allotment |
| F7 prompt injection | Legal cohort's HCPA tool output passed through guardrails; no injected directive executed |
| F8 silent irreversible | Offer signing hit the human gate; no auto-execute |
