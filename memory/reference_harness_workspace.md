---
name: Harness PRD workspace layout
description: Where the Agentic Harness Orchestration System PRD, diagrams, and docs site live on disk, and how they relate.
type: reference
originSessionId: dee45bae-57e2-4eaf-80fe-fea93aa03fed
---
The project lives under a Cowork workspace folder named *"Research, Design & Iterate an Agentic Harness Orchestration System"* with three top-level directories:

- **prd/** — source markdown.
  - `README.md` — spine/table of contents.
  - `00-preface.md` through `23-next-report.md` — 24 ordered chapters.
  - `appendices/A-diagram-index.md` through `E-proposed-skills.md` — 5 appendices.
  - Chapters are ordered and grouped by `DOC_MANIFEST` in `docs-site/lib/docs.ts`. Adding a chapter requires updating that manifest.

- **diagrams/** — 11 Mermaid files `D01-*.mermaid` through `D11-*.mermaid`. The index and question-per-diagram mapping is in `prd/appendices/A-diagram-index.md`. Any reference to `Dxx-slug.mermaid` inside a chapter is inlined by the docs-site preprocessor (first mention only).

- **docs-site/** — Next.js 16 App Router project.
  - Node 24, pnpm 10.33.0, next-mdx-remote v5, mermaid v11, Poppins/Lora via CDN `<link>`.
  - Build: `pnpm install && pnpm build`. Dev: `pnpm dev` on port 4567.
  - Key files: `lib/docs.ts` (manifest), `lib/preprocess.ts` (mermaid inlining + stray `<` escaping), `components/Mermaid.tsx` (client renderer with Anthropic theme), `app/globals.css` (Anthropic brand CSS tokens).
  - `next/font/google` was intentionally removed — it blocks offline builds. Fonts come from `<link>` in `app/layout.tsx`.

**How to apply:** When the user references "the PRD" or "chapter N", this is where it lives. When adding new content, update the `DOC_MANIFEST` in `docs-site/lib/docs.ts` *and* the TOC in `prd/README.md` — the nav is driven by the manifest, the TOC is hand-maintained.
