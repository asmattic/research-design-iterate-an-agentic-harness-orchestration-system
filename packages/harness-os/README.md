# harness-os

The **Orchestrator System** — the middleware layer between the primary
orchestrator and the cohort layer (PRD §6.4). Six sub-responsibilities, each a
module with a typed IO contract:

| Module | §6.4 | Round 2 core |
|---|---|---|
| `context_manager` | 6.4.1 | Budget-aware context assembly from orchestrator state + packets; drops oldest packets first, never the intent |
| `bs_detector` | 6.4.2 | Deterministic heuristics (over-confidence, unsupported numerics, malformed citations); LLM-judge prompt versioned in `prompts/` |
| `validator` | 6.4.3 | Bridges emissions' testable claims to the `harness-verifier` runner and attaches results |
| `signal_noise` | 6.4.4 | §9.1 factor-weighted claim scoring (calibration / verifier / agreement / BS flags / authority) |
| `weight_tweaker` | 6.4.5 | Applies retrospective weight-adjustment proposals to the per-agent trust table, clamped |
| `drift_detector` | 6.4.6 | Wraps `harness_reference.drift_check`; maps status to a campaign action and an event-ready payload |

Install (dev checkout, with its two sibling dependencies):

```bash
pip install -e packages/harness-protocol-py -e packages/harness-reference \
            -e packages/harness-verifier -e "packages/harness-os[test]"
```

The recorded-campaign integration test (`tests/test_integration_campaign.py`)
replays `fixtures/recorded-campaign.jsonl` through all six modules end to end —
the Phase 2C milestone gate.

LLM-layer prompts are versioned files under `prompts/` (e.g.
`bs_detector.v1.md`); the deterministic cores here never call a model — model
wiring is the adapter layer's job (§16).

Protocol version 0.2.0.
