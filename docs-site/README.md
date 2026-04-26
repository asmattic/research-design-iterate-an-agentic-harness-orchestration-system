# Harness PRD docs site

Next.js 16 (App Router) docs site for the Agentic Harness Orchestration System PRD.

## Quick start

```bash
# Requires Node 24 and pnpm 10+
nvm use            # reads .nvmrc → Node 24
corepack enable
corepack prepare pnpm@10.33.0 --activate

pnpm install
pnpm dev
# http://localhost:4567
```

## Production build

```bash
pnpm build
pnpm start
```

## How this site works

The site reads PRD content from its siblings on disk, at build time:

```
/prd/                  ← source markdown chapters
  00-preface.md
  01-executive-summary.md
  ...
  appendices/*.md
/diagrams/             ← source mermaid diagrams
  D01-system-layers.mermaid
  ...
/docs-site/            ← this Next.js project
```

The pipeline:

1. `lib/docs.ts` — manifests the chapter list in reading order, reads each
  markdown file with `gray-matter`, extracts H1 titles for nav.
2. `lib/preprocess.ts` — transforms raw markdown before MDX compilation:
  - Fenced `mermaid`blocks become`
    - Inline `D05-dispatch-tree.mermaid` references inline the diagram file
    (first mention only)
    - Stray `<` in math/schema prose is escaped to `<` so MDX doesn't choke.
3. `app/docs/[...slug]/page.tsx` — renders each chapter with
  `next-mdx-remote/rsc`, `remark-gfm`, and `rehype-slug` / `rehype-autolink-headings`.
4. `components/Mermaid.tsx` — a client component that renders Mermaid SVG on
  the client, themed from the neutral docs design tokens.
5. `components/DocsSearch.tsx` — a shadcn `CommandDialog` search palette fed by
  `getSearchIndex()` in `lib/docs.ts`.

## Design system

The docs use a Vercel-docs-inspired stack:

- Tailwind CSS v4 for layout, typography, spacing, borders, and page composition.
- shadcn/ui source-owned primitives for interactive UI, starting with
  `Button`, `Dialog`, and `Command` for global search.
- CSS variables in `app/globals.css` as the shared token layer.
- Responsive font-size tokens in `app/globals.css` (`--text-*`,
  `--font-size-body`, `--line-height-body`) so prose and navigation scale up
  across viewport sizes.


| Token            | Role               | Value     |
| ---------------- | ------------------ | --------- |
| `--bg`           | Page background    | `#ffffff` / `#000000` |
| `--bg-subtle`    | Subtle surfaces    | `#fafafa` / `#111111` |
| `--fg`           | Primary text       | `#111111` / `#ededed` |
| `--fg-muted`     | Secondary text     | `#666666` / `#a1a1a1` |
| `--border`       | Hairline borders   | `#e5e5e5` / `#262626` |
| `--accent`       | Primary accent     | `#000000` / `#ffffff` |


Typography uses `next/font/google` for Geist with the CSS token fallback kept
Geist-compatible.
The sidebar and home page expose a `⌘K` command search powered by the markdown
manifest in `lib/docs.ts`.

### Design-system maintenance map

- `app/globals.css` owns Tailwind imports, shadcn theme variables, neutral
  light/dark tokens, responsive type scale, prose defaults, and Mermaid/card
  surface styling.
- `components.json`, `components/ui/*`, and `lib/utils.ts` are shadcn-owned
  source files. Add new primitives with `pnpm dlx shadcn@latest add <name>` and
  keep local edits minimal.
- `components/DocsSearch.tsx` owns the global search interaction. It uses
  shadcn `Button`, `Command`, and `Dialog`, supports `⌘K` / `Ctrl+K`, and
  navigates through Next's App Router.
- `components/SidebarNav.tsx` owns the docs navigation shell. Section headings
  such as `Front matter` and `Part I · Foundations` stay visible, while leading
  chapter number prefixes are stripped from sidebar item labels only.
- `app/page.tsx`, `app/docs/[...slug]/page.tsx`, and `app/diagrams/page.tsx`
  compose the docs screens with Tailwind utilities over the shared token layer.
- `lib/docs.ts` owns the manifest, grouping, previous/next navigation, diagram
  loading, and the plain-text search index.

## Adding a chapter

1. Create the markdown file in `../prd/` (or `../prd/appendices/`).
2. Add an entry to the `DOC_MANIFEST` array in `lib/docs.ts` — specify the
  slug, the part grouping, the order, and the relative path.
3. Use the desired reader-facing H1 in the markdown file. Numeric filename/order
  prefixes are preserved for routing and sort order, but sidebar labels remove
  leading numeric prefixes.
4. Save. Dev server reloads automatically.

## Adding a diagram

1. Add `Dxx-slug.mermaid` to `../diagrams/`.
2. Reference it in a chapter as `Dxx-slug.mermaid` — the preprocessor inlines it.
3. Optionally add a row in the `DIAGRAM_META` object in `app/diagrams/page.tsx`
  so the all-diagrams index lists its question and chapter.

## Troubleshooting

- **Mermaid renders blank on first load:** the component initializes on mount,
so SSR shows an empty figure. This is intentional — the client render happens
within a few frames and avoids a headless-browser build step.
- **MDX parse error mentioning "unexpected `<`":** the preprocessor escapes
stray `<` but if a chapter adds a bare `<Component>` reference without
importing it, MDX will fail. Either import the component in
`mdx-components.tsx` or wrap the text in backticks.

