# Round 2 — Kickoff Plan & Next-Session Handoff

_Last updated: 2026-04-18, end of Round 1._

This is a handoff document for the next Cowork session (or any engineer picking this up). It tells you exactly where Round 1 finished, what's still loose, and how Round 2 should execute — mapped to chapter 23 of the PRD (`prd/23-next-report.md`) and the roadmap in §21.

---

## 1 · Where Round 1 landed

Round 1 (the PRD itself) is complete and public:

- **Repo:** `github.com/asmattic/claud-agentic-harness-orchestration-system` (public, MIT).
- **Tag-equivalent state:** 4 commits on `main`, HEAD = `efa9fbf` at handoff.
- **Artifacts shipped:** 25 PRD chapters, 5 appendices, 11 Mermaid diagrams, Next.js 16 docs site, memory snapshot (5 files), CI (3 jobs), Vercel config, LICENSE, SECURITY, CONTRIBUTING.
- **Protocol version:** `0.1.0`.
- **Docs site:** imported to Vercel, live URL pending.

The exit gate for Round 1 (human ratification of INTENT + design) is **cleared** — the user confirmed "I'm happy with the fact that the research is done and it's on GitHub."

## 2 · Loose ends from Round 1

| # | Item | Owner | Blocker |
|---|------|-------|---------|
| 1 | Paste the live Vercel URL into chat | User | Waiting on first successful deploy |
| 2 | Commit `docs: add live docs URL + Vercel badge` to `README.md` | Next session | #1 |
| 3 | Run `scripts/sync-memory.sh` if memory changed during Round 1→2 transition | Next session | None |
| 4 | Decide whether to cut a `v0.1.0` git tag for the PRD freeze | Next session | Ask user |
| 5 | Close/confirm §23.6 open questions (listed in §5 below) | User | None |

Nothing in this list blocks Round 2 kick-off. Items 1–2 can resolve async.

## 3 · Round 2 deliverables — the full artifact set

Direct from PRD §23.1. Each line is a gate; Round 2 is not done until every line ships.

### 3.1 · Protocol schemas at v0.2.0
- `agent-contract.schema.json`, `event-envelope.schema.json`, `consensus-packet.schema.json`, `orchestrator-state.schema.json`, `memory-index.schema.json`.
- Packaged as **Python** `harness-protocol` + **TypeScript** `@harness/protocol`.
- CI-runnable conformance test suite.
- Schemas become backward-compatible only within `0.2.x`.

### 3.2 · Reference scaffolding (`harness-reference/`)

**Templates (markdown):**
`INTENT.md`, `ORCHESTRATOR.md`, `AGENTS.md`, `COHORT.md`, `SWARM.md`, `CONSTITUTION.md`, `HANDOFF.md`.

**Executable modules — each ≤ 500 lines, typed, unit-tested:**
`drift_check.py`, `retrospective.py`, `consensus.py`, `memory_index.py`, `event_log.py`.

### 3.3 · Orchestrator System (`harness-os/`)
Six modules mapping 1:1 to §6.4:
`context_manager.py`, `bs_detector.py`, `validator.py`, `signal_noise.py`, `weight_tweaker.py`, `drift_detector.py`.

Each ships with: typed IO contract, unit tests, versioned prompts in `prompts/`, one recorded-campaign integration test.

### 3.4 · Deterministic verifier (`harness-verifier/`)
Runner + five built-in verifiers: `code_test_runner`, `schema_validator`, `citation_resolver`, `numeric_bound`, `type_check`. Plus an MCP-server wrapper so Claude Code can call them as tools.

### 3.5 · Eval harness (`evals/`)
CLI: `harness eval run --benchmark <name> --config <path> --output <dir>`.
Benchmarks: rental 20-scenario synthetic, protocol conformance, adversarial safety.
Scorers: calibration (Brier + ECE), drift, completion, cost, safety.
Regression gate: non-zero exit if a proposed config change regresses any score past threshold.
Report generator: produces `report.md` in §14.8 format.

### 3.6 · Claude Code adapter (`adapters/claude_code/`)
Python package + `.plugin` bundle. Six skills, four subagents + experts, Pre/PostToolUse hooks, `harness-verifier` MCP, install script, quickstart docs, one recorded demo campaign, conformance test pass.

### 3.7 · Rental-toolkit port (partial)
Finance + legal cohorts ported. Migration script for legacy event logs → new protocol. One held-out property runs end-to-end.

### 3.8 · Documentation site update
New "Round 2" section on the docs-site. Adapter quickstart. Example campaign walkthrough (rental underwriting minireplay). Auto-generated schema reference. "How to add a cohort / verifier / adapter" guides.

## 4 · Round 2 acceptance criteria (from §23.2)

Round 2 is done when **all eight** pass:

1. Schemas validate against their conformance suite.
2. `harness-reference` clones, installs, passes its tests.
3. Claude Code adapter passes conformance.
4. Eval harness runs the synthetic rental benchmark E2E and produces a report.
5. Rental-toolkit finance + legal cohorts complete a test campaign on the harness.
6. Drift detector fires correctly in an intentionally-induced drift test.
7. Human approval gate engages on every irreversible action in the test campaign.
8. Docs site deploys with Round 2 content.

## 5 · Open questions to resolve at kickoff (from §23.6)

Ask the user at the start of next session:

- **Context manager embeddings vs lexical.** Build `context_manager.py` with vector embeddings from day 1, or ship lexical summarization for Round 2 and defer vectors to Round 3?
- **Retrospective output location.** Ship retrospective proposals as PR diffs against a central config repo, or as local files per campaign?
- **Benchmark size.** Synthetic rental set: stick with 20 scenarios as planned, or scale to 50?

Also:

- **Model access.** Which API keys + quotas will Round 2 use? (Anthropic only? Mixed?)
- **Legacy rental-toolkit access.** Where do the legacy event-log artifacts live? Needed for migration testing.
- **Security review.** Constitutional rules specifically for rental underwriting (PII, financial data).

## 6 · Proposed Round 2 execution plan

~3–5 weeks, sequencing driven by "what unblocks what" rather than by artifact list order. Each phase ends with something runnable.

### Phase 2A · Protocol + scaffolding skeleton (week 1)
- Create `harness-protocol` Python package: schemas + validators + conformance tests.
- Create `harness-reference` repo scaffold: template stubs, module stubs with typed signatures and failing unit tests.
- Start `evals/` skeleton: CLI parser + one dummy scorer.
- Milestone: `pip install harness-protocol && python -m harness_protocol.conform` succeeds on an example contract.

### Phase 2B · Reference modules pass unit tests (week 2)
- Implement `event_log.py`, `memory_index.py`, `drift_check.py`, `consensus.py`, `retrospective.py` against the week-1 unit tests.
- Finalize template markdown with placeholder-driven examples.
- Milestone: `harness-reference` passes CI.

### Phase 2C · Orchestrator System + verifier (week 3)
- `harness-os` six modules with typed IO + unit tests.
- `harness-verifier` runner + five built-in verifiers.
- MCP server wrapper around `harness-verifier`.
- Milestone: recorded-campaign integration test passes in `harness-os`.

### Phase 2D · Claude Code adapter + eval harness (week 4)
- Build `adapters/claude_code` skills, subagents, hooks, MCP.
- Wire `evals/` scorers to produce `report.md`.
- Rental 20-scenario synthetic benchmark seed data.
- Adversarial safety payload set (≥ 20 prompt-injection cases).
- Milestone: `harness eval run --benchmark rental` produces a report on one config.

### Phase 2E · Rental port + docs (week 5, overflow into week 6 if needed)
- Port finance + legal cohorts from legacy rental toolkit.
- Legacy-log migration script.
- One held-out property E2E campaign.
- Round 2 docs-site section + adapter quickstart + walkthrough + auto-generated schema reference.
- Milestone: all 8 acceptance criteria green; tag `v0.2.0`.

## 7 · Technical environment notes for the next Cowork session

Things that tripped this session up and should be pre-empted:

### 7.1 · Cowork sandbox + FUSE
The workspace mount uses FUSE, which rejects `rm` on `.git/index.lock` and breaks `git` atomic renames. **Always run git operations in `/sessions/<id>/git-work/repo/` (a regular filesystem), then round-trip the `.git` directory back to the workspace via:**

```
mv "$WS/.git" "$WS/.git-broken-$(date +%s)"
cp -r /sessions/<id>/git-work/repo/.git "$WS/.git"
```

`.git-broken-*` is already gitignored. Over time those dirs accumulate in the workspace; they're harmless FUSE residue.

### 7.2 · Sandbox network allowlist
As of this session:
- `github.com` → 200 (OK).
- `api.github.com` → 403 (blocked, even after user's allowlist change).
- `cli.github.com`, `raw.githubusercontent.com`, `codeload.github.com`, `uploads.github.com` → 403.

Implication: **no `gh` commands from the sandbox.** The user runs `gh` from their own terminal. Plan any Round 2 flows assuming "Claude prepares commits in sandbox; user pushes."

If the next session tries these and they still 403, don't waste time diagnosing — go straight to the user-terminal path.

### 7.3 · GitHub PAT scopes
User's PAT needs `repo` **and** `workflow` (the second was missed at first push; `gh auth refresh -s repo,workflow` fixes it). Any commit touching `.github/workflows/*.yml` needs `workflow`.

### 7.4 · Vercel deployment model
Vercel MCP's `deploy_to_vercel` is a hint tool, not an actual deploy trigger. Deployment is **Git integration** — every push to `main` auto-deploys. `vercel.json` at repo root is authoritative; Vercel UI settings should not be overridden.

### 7.5 · Next.js 16 tsconfig
Next 16 rewrites `docs-site/tsconfig.json` on `pnpm dev`/`pnpm build` (adds `jsx: "react-jsx"`, `.next/dev/types/**/*.ts` include, array-per-line reformat). **Do not revert these.** See `memory/feedback_nextjs_tsconfig.md`. Round 2 work touching the docs site should stage and commit whatever tsconfig changes come out of the toolchain.

### 7.6 · Memory snapshot
Canonical memory lives at `/sessions/<id>/mnt/.auto-memory/`. Before a Round 2 commit that meaningfully changed memory, run:

```
scripts/sync-memory.sh         # refresh memory/
scripts/sync-memory.sh --check # pre-commit drift check
```

CI's `memory-snapshot` job enforces internal consistency (not source-match) so you don't strictly have to sync on every commit — but do sync when memory content changes and you want it reflected in the public repo.

### 7.7 · PRD-shape CI
CI's `prd-shape` job greps `docs-site/lib/docs.ts` for `kind: 'chapter'` / `kind: 'appendix'` counts and compares to `prd/*.md` counts. If Round 2 adds chapters (likely), update `DOC_MANIFEST` **in the same commit** or CI will red.

## 8 · Risks & mitigations for Round 2

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Schema churn mid-round breaks adapter | Medium | High | Freeze schemas at end of Phase 2A; any change after that needs a v0.2.x bump + adapter re-test. |
| Claude Code plugin spec changes during Round 2 | Medium | Medium | Pin plugin schema version; re-validate adapter bundle in CI. |
| Legacy rental-toolkit logs unavailable or undocumented | Medium | High | Write migration script against a synthetic log first; real-log ingestion becomes a gate item, not a blocker. |
| Eval costs balloon ($5K–$15K budget) | Low | Medium | Require `--dry-run` mode on `harness eval run`; gate live runs on user approval; use cheap models for iteration. |
| Drift detector false-positives on benign refactors | High | Low | Ship with conservative thresholds + a documented override; tune via §11 composite on recorded campaigns. |
| Sandbox can't run Python/Node Round 2 test suites | Low | High | Verify Phase 2A locally first; if sandbox blocks, execute tests in user terminal and capture results. |

## 9 · What the next session should read first

In order, so context loads efficiently:

1. This file (`ROUND-2-PLAN.md`).
2. `prd/23-next-report.md` — the Round 2 spec.
3. `prd/21-roadmap.md` — Rounds 2 and 3 in the broader arc.
4. `prd/appendices/D-schemas.md` — schema skeletons to finalize.
5. `prd/06-orchestrator-system.md` — the six sub-responsibilities `harness-os/` must implement.
6. `prd/appendices/B-glossary.md` — canonical terminology; use exactly.
7. `memory/project_harness_prd.md` — load-bearing decisions that are non-negotiable.

## 10 · First two commits of Round 2 (suggested)

Once the user says "start Round 2":

1. **`chore: begin Round 2 — protocol package skeleton`**
   - `harness-protocol/` Python package with schemas copied from `prd/appendices/D-schemas.md`, stub validators, stub conformance tests.
   - Update root `README.md` status block: "Round 2 in progress."

2. **`test(protocol): add conformance suite and CI job`**
   - Pytest suite + a new `.github/workflows/protocol.yml` job.
   - First visible CI signal for Round 2.

Everything after that follows the phase plan in §6.

---

**One-line handoff:** Round 1 is live and ratified; Round 2 starts with the protocol package and ends with a runnable rental underwriting campaign on Claude Code, behind eight acceptance gates and five weeks of phased execution.
