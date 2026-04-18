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
  the client, themed with the Anthropic palette (orange/blue/green accents,
   warm off-white background).

## Branding

Anthropic brand tokens are declared as CSS variables in `app/globals.css`:


| Token            | Role               | Value     |
| ---------------- | ------------------ | --------- |
| `--c-dark`       | Text on light bg   | `#141413` |
| `--c-light`      | Page background    | `#faf9f5` |
| `--c-mid-gray`   | Secondary elements | `#b0aea5` |
| `--c-light-gray` | Subtle backgrounds | `#e8e6dc` |
| `--c-orange`     | Primary accent     | `#d97757` |
| `--c-blue`       | Secondary accent   | `#6a9bcc` |
| `--c-green`      | Tertiary accent    | `#788c5d` |


Typography uses `next/font/google` for Poppins (headings) and Lora (body),
wired into the CSS variables `--font-poppins` and `--font-lora`.

## Adding a chapter

1. Create the markdown file in `../prd/` (or `../prd/appendices/`).
2. Add an entry to the `DOC_MANIFEST` array in `lib/docs.ts` — specify the
  slug, the part grouping, the order, and the relative path.
3. Save. Dev server reloads automatically.

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

