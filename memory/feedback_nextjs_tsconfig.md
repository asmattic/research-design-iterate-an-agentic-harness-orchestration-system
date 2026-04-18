---
name: Next 16 tsconfig auto-edits are canonical
description: Don't fight Next.js 16's automatic rewrites of docs-site/tsconfig.json — they are required for the app to typecheck.
type: feedback
originSessionId: dee45bae-57e2-4eaf-80fe-fea93aa03fed
---
When `pnpm dev` or `pnpm build` runs in `docs-site/`, Next.js 16 rewrites `tsconfig.json` to add specific settings and reformat the file. Specifically, it adds:

- `"jsx": "react-jsx"` (replacing `"preserve"`)
- `".next/dev/types/**/*.ts"` to `include`
- An array-per-line reformat of `lib`, `plugins`, `paths`, etc.

These changes are **required** by the Next 16 toolchain — confirmed by the user after running the project in Cursor's terminal. Do not revert or "clean up" the file to the pre-Next form. Commit Next's regenerated version.

**Why:** Next 16 mandates these tsconfig settings; reverting causes typecheck failures and forces another rewrite on the next dev/build cycle.

**How to apply:** When the workspace shows `docs-site/tsconfig.json` as modified after a Next dev/build run, treat the diff as canonical and stage/commit it. Don't try to keep the hand-written terser version.
