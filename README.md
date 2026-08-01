# Agentic Harness Orchestration System

A research-and-design effort to specify a **harness-agnostic orchestration layer** for parallel LLM agents — mixture-of-experts cohorts with confidence intervals, three-valued cross-checking, deterministic verifier precedence, and tiered memory.

This repository contains the source PRD, diagram set, docs site, and (forthcoming) reference scaffolding.

**Live docs:** _coming soon_ (Vercel deployment pending — URL will be added once the first deploy lands).

## Status

- **Round 1 (complete, 2026-04-18)** — PRD v0.1.0. 25 chapters, 5 appendices, 11 Mermaid diagrams, Next.js 16 docs site. Harness protocol version 0.1.0.
- **Round 2 (in progress, started 2026-07-31)** — Protocol package shipped first: `packages/harness-protocol/` (canonical v0.2 JSON Schemas + example fixtures) and `packages/harness-protocol-py/` (Python `harness-protocol` with validators + conformance runner). Remaining: reference scaffolding (templates + drift_check + retrospective + consensus + memory_index + event_log), Orchestrator System Python package, deterministic verifier, eval harness prototype, Claude Code adapter, partial rental-toolkit port. Orchestration loop re-based on wayfinder — see `WAYFINDER-DESIGN.md`. Schema target: v0.2.0.
- **Round 3+** — Multi-adapter coverage (Codex CLI, Cursor) and benchmark integration (SWE-bench Verified, GAIA, BrowseComp, MINT).

## Layout

| Directory      | Contents                                                                                          |
|----------------|---------------------------------------------------------------------------------------------------|
| `prd/`         | Source markdown. `README.md` is the spine. Chapters `00-preface.md`–`23-next-report.md`. Appendices `A`–`E` under `appendices/`. |
| `diagrams/`    | 11 Mermaid files `D01`–`D11`. Each answers one architectural question (see `prd/appendices/A-diagram-index.md`). |
| `docs-site/`   | Next.js 16 App Router project that renders the PRD with Tailwind CSS v4, shadcn/ui search primitives, and a Vercel-docs-inspired design system. Node 24, pnpm 10. See `docs-site/README.md`. |
| `packages/`    | Round 2 protocol artifacts. `harness-protocol/` holds the canonical v0.2 JSON Schemas + example fixtures (Appendix D is the design sketch; these files are normative). `harness-protocol-py/` is the installable Python package. |
| `memory/`      | Snapshot of the Cowork session memory. Refreshed via `scripts/sync-memory.sh`.                     |
| `scripts/`     | Maintenance scripts. Currently: `sync-memory.sh`.                                                  |

## Reading the PRD

The fastest path is the rendered docs site:

```bash
cd docs-site
pnpm install
pnpm dev   # http://localhost:4567
```

If you'd rather read raw markdown, start at `prd/README.md` — it links every chapter and appendix in order.

## Memory snapshot

The Cowork sessions that built this PRD persist context in an auto-memory directory at a sandbox-local path. Because that path doesn't resolve outside the sandbox, the canonical files are mirrored into `memory/` and committed to the repo.

Refresh the snapshot:

```bash
scripts/sync-memory.sh
```

Check for drift (exits non-zero if the snapshot is stale; useful for pre-commit or CI):

```bash
scripts/sync-memory.sh --check
```

The `.auto-memory/` symlink at the repo root points at the live, in-session copy. It is gitignored and only meaningful inside a Cowork sandbox.

## Conventions

- Chapter ordering is driven by `docs-site/lib/docs.ts` (`DOC_MANIFEST`). Adding a chapter requires updating the manifest *and* the TOC in `prd/README.md`.
- Docs-site section headings stay grouped by `DOC_MANIFEST.part`; sidebar item labels strip leading chapter number prefixes while routes and sort order keep the numeric slugs.
- Diagram references inside chapters are written as bare filenames (e.g. `D04-orchestrator-loop.mermaid`); the docs-site preprocessor inlines them on first mention. Mentions inside markdown table rows are deliberately **not** inlined (see `docs-site/scripts/preprocess.test.mjs`) — index tables like Appendix A list filenames without embedding.
- Terminology in `prd/appendices/B-glossary.md` is canonical — `packet`, `caucus`, `cohort`, `orchestrator system`, `drift`, etc. — and is used consistently across chapters.

## Development Workflow

This project follows a feature-branch workflow:

1. Create a feature branch from `main` (e.g., `feat/your-feature-name`)
2. Make your changes and commit
3. Push the branch and open a PR
4. Wait for CI/CD checks to pass
5. Merge to `main` after approval

### Local verification

- Full local gate: `pnpm --dir docs-site run test:js` (typecheck → unit tests → build → smoke test). The unit suite (`docs-site/scripts/preprocess.test.mjs`) guards the markdown preprocessor; CI does not run it yet ([ASM-572](https://linear.app/asmattic/issue/ASM-572)).
- **Known issue:** `pnpm dev` (Turbopack) currently reports Ready but never serves requests ([ASM-571](https://linear.app/asmattic/issue/ASM-571)). Verify pages against the production server instead: `pnpm --dir docs-site build && pnpm --dir docs-site start` (port 4567).

### Deployment

- The site deploys to the Vercel project **harness-prd-docs** (production stays behind Vercel SSO by design — log in to view).
- Pushes to `main` do **not** auto-deploy yet — the Git integration is not connected ([ASM-570](https://linear.app/asmattic/issue/ASM-570)). Until then, deploy manually from the repo root: `npx vercel deploy --prod` (the root `vercel.json` carries the build config).

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for the workflow on adding chapters or diagrams, conventions, and the pre-PR checklist. Security issues should follow [SECURITY.md](./SECURITY.md).

## License

[MIT](./LICENSE) — see the LICENSE file for the full text.
