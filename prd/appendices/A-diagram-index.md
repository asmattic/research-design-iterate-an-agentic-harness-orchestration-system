# Appendix A · Diagram Index

Eleven Mermaid diagrams live at `/diagrams/`. Each answers one architectural question. Each is embedded in its corresponding chapter.

| # | Diagram | Question answered | Chapter | File |
|---|---|---|---|---|
| **D01** | System Layers | What are the layers of this architecture, top to bottom? | §05 | `D01-system-layers.mermaid` |
| **D02** | Orchestrator System detail | What are the six sub-responsibilities of the Orchestrator System and how do they compose? | §06 | `D02-orchestrator-system.mermaid` |
| **D03** | Hub topology (default) | How does the hub-and-spoke communication topology work? | §07 | `D03-hub-topology.mermaid` |
| **D04** | Caucus — bounded peer | When peer visibility is granted, how is it scoped? | §07 | `D04-caucus.mermaid` |
| **D05** | Dispatch decision tree | How does the harness pick single / serial / parallel / swarm / caucus? | §08 | `D05-dispatch-tree.mermaid` |
| **D06** | Consensus aggregation | How does a swarm's output become a Consensus Packet? | §09 | `D06-consensus.mermaid` |
| **D07** | Memory tiers | How do L0 / L1 / L2 / L3 relate and flow? | §10 | `D07-memory-tiers.mermaid` |
| **D08** | Drift control loop | How is drift measured continuously and acted on? | §11 | `D08-drift-loop.mermaid` |
| **D09** | Guardrail stack | How do the four guardrail classes layer at boundaries? | §12 | `D09-guardrail-stack.mermaid` |
| **D10** | Feedback loops (three cadences) | How do Reflexion / retrospective / eval-harness relate? | §13 | `D10-feedback-loops.mermaid` |
| **D11** | Eval cadences | How do per-turn / per-task / per-campaign evals flow into config? | §14 | `D11-eval-cadences.mermaid` |

Rendering notes: Mermaid diagrams are rendered client-side in the Next.js docs site via the official `mermaid` package. Each `.mermaid` file is also embedded in the corresponding chapter markdown via an MDX `<Mermaid>` component.

## How to add a diagram

1. Add the `.mermaid` file to `/diagrams/` with an ID prefix (D12 onwards).
2. Add a row to the table above.
3. Embed it in the relevant chapter with the `<Mermaid>` component (see docs site).
4. Update this appendix.
