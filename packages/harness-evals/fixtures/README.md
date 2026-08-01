# Fixtures

`recorded-campaign.jsonl` is a small recorded wayfinding campaign (`camp_evals_smoke`): 8 event
envelopes covering ticket claim, an agent emission, a tool call/result, a verifier result, a
drift check, ticket resolution, and a decision. The `smoke` benchmark scores it with the dummy scorer.

Every line must validate against `packages/harness-protocol/schemas/event-envelope.schema.json`
(Draft 2020-12). CI enforces this via the test suite — do not hand-edit without re-validating.

To regenerate or extend: append complete envelopes (distinct `event_id`, same `campaign_id`,
timestamps in order), then validate each line with `python3 -m jsonschema` / `Draft202012Validator`.
