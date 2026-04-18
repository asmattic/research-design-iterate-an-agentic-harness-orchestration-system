# Contributing

This repo holds a PRD, its diagram set, and a Next.js docs site that renders both. Contributions that fit any of the three are welcome; the workflows below cover the common cases.

## Repo layout

See the top-level [README](./README.md). Short version: `prd/` is markdown source, `diagrams/` is Mermaid, `docs-site/` is the Next 16 renderer, `memory/` is a snapshot of session memory.

## Local setup

```bash
cd docs-site
pnpm install        # Node 24, pnpm 10 — see .nvmrc and package.json#engines
pnpm dev            # http://localhost:4567
```

The dev server reads from sibling directories (`../prd`, `../diagrams`) at request time. No content needs to be copied.

## Adding a chapter

1. Create the markdown file under `prd/` with the next ordinal — e.g. `24-something.md`.
2. Add an entry to `DOC_MANIFEST` in `docs-site/lib/docs.ts`. The manifest is the spine of the navigation; nothing renders without an entry there.
3. Update the table of contents in `prd/README.md` (it is hand-maintained, intentionally — it doubles as a printable index).
4. Run `pnpm dev` and confirm the chapter appears in the sidebar and renders correctly.
5. If the chapter uses a new diagram, follow "Adding a diagram" first.

## Adding a diagram

1. Create the Mermaid file under `diagrams/` as `Dxx-slug.mermaid` — pick the next `Dxx`. Use the existing files as a style template (Anthropic theme `classDef` colors, `flowchart TD`, etc.).
2. Add the diagram to `prd/appendices/A-diagram-index.md` with the architectural question it answers and the chapter that owns it.
3. Reference the diagram in the relevant chapter by bare filename:
   ```
   See `D12-some-slug.mermaid`.
   ```
   The docs-site preprocessor inlines the first such reference per chapter. Subsequent references render as plain code spans.

## Conventions

- **Voice and structure** are described in `memory/user_asmattic_style.md`. New chapters should match it: short paragraphs, decision-then-reason, tables for structured comparisons, citations only when a decision depends on them.
- **Terminology** in `prd/appendices/B-glossary.md` is canonical. If a new concept needs a noun, add it there too.
- **Citations** earn their place: an entry in `prd/appendices/C-bibliography.md` must back at least one design decision in the chapters.
- **Diagrams** answer one architectural question each. If a new diagram doesn't fit that constraint, it probably belongs as a smaller inline diagram in the chapter rather than a top-level `Dxx`.

## Pre-PR checklist

```bash
cd docs-site && pnpm build               # site builds and typechecks
scripts/sync-memory.sh --check           # memory snapshot is in sync
```

CI runs both on every PR; locally is faster.

## Memory snapshot

The `memory/` directory is a snapshot of the Cowork session memory used while building the PRD. The canonical location is sandbox-local. To refresh the snapshot before committing:

```bash
scripts/sync-memory.sh
```

If you don't run Cowork, you can ignore `memory/` — it's reference material, not a build input.
