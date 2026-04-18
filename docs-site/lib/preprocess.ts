/**
 * Preprocess PRD markdown into MDX-compatible source before handing it to
 * next-mdx-remote. Two responsibilities:
 *
 *   1. Inline `.mermaid` diagram references. When a paragraph mentions a
 *      diagram file by name (D05-dispatch-tree.mermaid), substitute the
 *      file's contents as a <Mermaid> component. First reference only —
 *      subsequent mentions keep their inline code text.
 *
 *   2. Escape stray `<` characters that aren't part of valid HTML/MDX
 *      components. The PRD markdown uses `<` in math expressions and
 *      schema-ish snippets which MDX would otherwise reject.
 *
 * The preprocessor is intentionally small and scripted rather than a
 * full AST pass — the PRD has a known shape and we don't want to
 * introduce a remark plugin dependency just for these two rules.
 */

import fs from 'node:fs';
import path from 'node:path';

const DIAGRAMS_ROOT = path.resolve(process.cwd(), '..', 'diagrams');

function escapeForTemplateLiteral(s: string): string {
  return s
    .replace(/\\/g, '\\\\')
    .replace(/`/g, '\\`')
    .replace(/\$\{/g, '\\${');
}

function readDiagram(id: string): string | null {
  const abs = path.join(DIAGRAMS_ROOT, `${id}.mermaid`);
  if (!fs.existsSync(abs)) return null;
  return fs.readFileSync(abs, 'utf-8');
}

/**
 * Escape MDX-sensitive characters in text that is not inside code fences.
 * The main gotcha: `<` followed by a non-letter is fine; `<letter` is parsed
 * as a component. A few chapter files have `≤ N` as `< N` that we need to
 * protect. Fenced code and inline code are left alone.
 */
function escapeStrayAngles(md: string): string {
  const fenceRe = /(```[\s\S]*?```|`[^`\n]*`)/g;
  const segments: string[] = [];
  let last = 0;
  let m: RegExpExecArray | null;
  while ((m = fenceRe.exec(md)) !== null) {
    segments.push(md.slice(last, m.index).replace(/</g, (c, i, full) => {
      const next = full[i + 1];
      // Allow `<` that clearly starts a tag: letter, /, !, ?.
      if (next && /[a-zA-Z/!?]/.test(next)) return c;
      return '&lt;';
    }));
    segments.push(m[0]);
    last = m.index + m[0].length;
  }
  segments.push(md.slice(last).replace(/</g, (c, i, full) => {
    const next = full[i + 1];
    if (next && /[a-zA-Z/!?]/.test(next)) return c;
    return '&lt;';
  }));
  return segments.join('');
}

export function preprocessMarkdown(md: string): string {
  const inlined = new Set<string>();

  // Pass 1 — fenced ```mermaid blocks become <Mermaid chart={`...`} />.
  let out = md.replace(
    /```mermaid\n([\s\S]*?)```/g,
    (_full, code: string) =>
      `\n<Mermaid chart={\`${escapeForTemplateLiteral(code.trim())}\`} />\n`,
  );

  // Pass 2 — inline diagram references. Match the first mention of each
  // `D\d\d-slug.mermaid` and substitute the file body.
  out = out.replace(
    /`?(D\d{2}-[a-z0-9-]+)\.mermaid`?/g,
    (match, id: string) => {
      if (inlined.has(id)) return match;
      const body = readDiagram(id);
      if (!body) return match;
      inlined.add(id);
      return `\n\n<Mermaid chart={\`${escapeForTemplateLiteral(body.trim())}\`} caption="${id}.mermaid" />\n\n`;
    },
  );

  // Pass 3 — escape stray `<` that would confuse MDX.
  out = escapeStrayAngles(out);

  return out;
}
