import fs from 'node:fs';
import path from 'node:path';
import matter from 'gray-matter';

export interface DocMeta {
  slug: string;           // e.g. "05-architecture-overview" or "appendices/A-diagram-index"
  title: string;          // first H1 or fallback
  part: string;           // Section grouping shown in nav
  order: number;          // sort within section
  relPath: string;        // path relative to prd root
}

export interface DocContent extends DocMeta {
  raw: string;
  body: string;           // stripped of leading H1 so we can render title ourselves
}

const PRD_ROOT = path.resolve(process.cwd(), '..', 'prd');
const DIAGRAMS_ROOT = path.resolve(process.cwd(), '..', 'diagrams');

/**
 * Hardcoded ordering/grouping mirrors README.md. Any new file must be added here
 * or it will be filtered out of the nav. This is deliberately explicit — the nav
 * is the PRD's spine, we want a build failure if something moves unannounced.
 */
export const DOC_MANIFEST: Array<{
  slug: string;
  part: string;
  order: number;
  relPath: string;
  fallbackTitle: string;
  kind: 'chapter' | 'appendix';
}> = [
  { slug: '00-preface',               part: 'Front matter',  order: 0,  relPath: '00-preface.md',               fallbackTitle: 'Preface', kind: 'chapter' },
  { slug: '01-executive-summary',     part: 'Front matter',  order: 1,  relPath: '01-executive-summary.md',     fallbackTitle: 'Executive summary', kind: 'chapter' },
  { slug: '02-intent-goals',          part: 'Front matter',  order: 2,  relPath: '02-intent-goals.md',          fallbackTitle: 'Intent & goals', kind: 'chapter' },
  { slug: '03-problem-statement',     part: 'Front matter',  order: 3,  relPath: '03-problem-statement.md',     fallbackTitle: 'Problem statement', kind: 'chapter' },

  { slug: '04-conceptual-foundations', part: 'Part I · Foundations',    order: 10, relPath: '04-conceptual-foundations.md', fallbackTitle: 'Conceptual foundations', kind: 'chapter' },

  { slug: '05-architecture-overview',  part: 'Part II · Architecture',  order: 20, relPath: '05-architecture-overview.md',  fallbackTitle: 'Architecture overview', kind: 'chapter' },
  { slug: '06-core-components',        part: 'Part II · Architecture',  order: 21, relPath: '06-core-components.md',        fallbackTitle: 'Core components', kind: 'chapter' },
  { slug: '07-communication-topology', part: 'Part II · Architecture',  order: 22, relPath: '07-communication-topology.md', fallbackTitle: 'Communication topology', kind: 'chapter' },
  { slug: '08-parallel-vs-serial',     part: 'Part II · Architecture',  order: 23, relPath: '08-parallel-vs-serial.md',     fallbackTitle: 'Parallel vs serial', kind: 'chapter' },

  { slug: '09-signal-consensus',       part: 'Part III · Signal & consensus', order: 30, relPath: '09-signal-consensus.md', fallbackTitle: 'Signal & consensus', kind: 'chapter' },

  { slug: '10-memory-architecture',    part: 'Part IV · Memory & drift', order: 40, relPath: '10-memory-architecture.md', fallbackTitle: 'Memory architecture', kind: 'chapter' },
  { slug: '11-drift-control',          part: 'Part IV · Memory & drift', order: 41, relPath: '11-drift-control.md',       fallbackTitle: 'Drift control', kind: 'chapter' },

  { slug: '12-guardrails',             part: 'Part V · Safety & feedback', order: 50, relPath: '12-guardrails.md',        fallbackTitle: 'Guardrails', kind: 'chapter' },
  { slug: '13-feedback-loops',         part: 'Part V · Safety & feedback', order: 51, relPath: '13-feedback-loops.md',    fallbackTitle: 'Feedback loops', kind: 'chapter' },
  { slug: '14-evaluation',             part: 'Part V · Safety & feedback', order: 52, relPath: '14-evaluation.md',        fallbackTitle: 'Evaluation', kind: 'chapter' },

  { slug: '15-protocol-spec',          part: 'Part VI · Protocol & adapters', order: 60, relPath: '15-protocol-spec.md', fallbackTitle: 'Protocol spec', kind: 'chapter' },
  { slug: '16-adapters',               part: 'Part VI · Protocol & adapters', order: 61, relPath: '16-adapters.md',      fallbackTitle: 'Adapters', kind: 'chapter' },

  { slug: '17-worked-example-rental',           part: 'Part VII · Worked examples', order: 70, relPath: '17-worked-example-rental.md',           fallbackTitle: 'Worked example · rental toolkit', kind: 'chapter' },
  { slug: '18-worked-example-code-architecture', part: 'Part VII · Worked examples', order: 71, relPath: '18-worked-example-code-architecture.md', fallbackTitle: 'Worked example · code architecture', kind: 'chapter' },
  { slug: '19-worked-example-ai-research',      part: 'Part VII · Worked examples', order: 72, relPath: '19-worked-example-ai-research.md',      fallbackTitle: 'Worked example · AI research', kind: 'chapter' },

  { slug: '20-risks-and-mitigations',  part: 'Part VIII · Risk & ops', order: 80, relPath: '20-risks-and-mitigations.md', fallbackTitle: 'Risks & mitigations', kind: 'chapter' },
  { slug: '21-roadmap',                part: 'Part VIII · Risk & ops', order: 81, relPath: '21-roadmap.md',               fallbackTitle: 'Roadmap', kind: 'chapter' },
  { slug: '22-open-questions',         part: 'Part VIII · Risk & ops', order: 82, relPath: '22-open-questions.md',        fallbackTitle: 'Open questions', kind: 'chapter' },

  { slug: '23-next-report',            part: 'Part IX · Next report',  order: 90, relPath: '23-next-report.md',           fallbackTitle: 'Round 2 scope', kind: 'chapter' },

  { slug: 'appendices/A-diagram-index', part: 'Appendices', order: 100, relPath: 'appendices/A-diagram-index.md', fallbackTitle: 'Appendix A · Diagram index', kind: 'appendix' },
  { slug: 'appendices/B-glossary',      part: 'Appendices', order: 101, relPath: 'appendices/B-glossary.md',      fallbackTitle: 'Appendix B · Glossary', kind: 'appendix' },
  { slug: 'appendices/C-bibliography',  part: 'Appendices', order: 102, relPath: 'appendices/C-bibliography.md',  fallbackTitle: 'Appendix C · Bibliography', kind: 'appendix' },
  { slug: 'appendices/D-schemas',       part: 'Appendices', order: 103, relPath: 'appendices/D-schemas.md',       fallbackTitle: 'Appendix D · Protocol schemas', kind: 'appendix' },
  { slug: 'appendices/E-proposed-skills', part: 'Appendices', order: 104, relPath: 'appendices/E-proposed-skills.md', fallbackTitle: 'Appendix E · Proposed skills', kind: 'appendix' },
];

/** Very small H1 extractor — no markdown parser needed for the nav title. */
function extractH1(raw: string, fallback: string): string {
  const match = raw.match(/^#\s+(.+?)\s*$/m);
  return match ? match[1].trim() : fallback;
}

function stripLeadingH1(raw: string): string {
  return raw.replace(/^#\s+.+?\n+/m, '');
}

export function listDocs(): DocMeta[] {
  return DOC_MANIFEST.map(entry => {
    const abs = path.join(PRD_ROOT, entry.relPath);
    let title = entry.fallbackTitle;
    if (fs.existsSync(abs)) {
      const raw = fs.readFileSync(abs, 'utf-8');
      const parsed = matter(raw);
      title = extractH1(parsed.content, entry.fallbackTitle);
    }
    return {
      slug: entry.slug,
      title,
      part: entry.part,
      order: entry.order,
      relPath: entry.relPath,
    };
  });
}

export function getDoc(slug: string): DocContent | null {
  const entry = DOC_MANIFEST.find(e => e.slug === slug);
  if (!entry) return null;
  const abs = path.join(PRD_ROOT, entry.relPath);
  if (!fs.existsSync(abs)) return null;
  const raw = fs.readFileSync(abs, 'utf-8');
  const parsed = matter(raw);
  const title = extractH1(parsed.content, entry.fallbackTitle);
  return {
    slug: entry.slug,
    title,
    part: entry.part,
    order: entry.order,
    relPath: entry.relPath,
    raw: parsed.content,
    body: stripLeadingH1(parsed.content),
  };
}

export function listDiagrams(): Array<{ id: string; body: string }> {
  if (!fs.existsSync(DIAGRAMS_ROOT)) return [];
  return fs.readdirSync(DIAGRAMS_ROOT)
    .filter(f => f.endsWith('.mermaid'))
    .sort()
    .map(f => ({
      id: f.replace(/\.mermaid$/, ''),
      body: fs.readFileSync(path.join(DIAGRAMS_ROOT, f), 'utf-8'),
    }));
}

export function getDiagram(id: string): string | null {
  const abs = path.join(DIAGRAMS_ROOT, `${id}.mermaid`);
  if (!fs.existsSync(abs)) return null;
  return fs.readFileSync(abs, 'utf-8');
}

/**
 * Group docs by part, preserving order. Used by the sidebar nav.
 */
export function groupedDocs(): Array<{ part: string; docs: DocMeta[] }> {
  const docs = listDocs().sort((a, b) => a.order - b.order);
  const groups: Array<{ part: string; docs: DocMeta[] }> = [];
  for (const doc of docs) {
    const last = groups[groups.length - 1];
    if (last && last.part === doc.part) last.docs.push(doc);
    else groups.push({ part: doc.part, docs: [doc] });
  }
  return groups;
}

export function prevNextOf(slug: string): { prev: DocMeta | null; next: DocMeta | null } {
  const docs = listDocs().sort((a, b) => a.order - b.order);
  const i = docs.findIndex(d => d.slug === slug);
  if (i < 0) return { prev: null, next: null };
  return {
    prev: i > 0 ? docs[i - 1] : null,
    next: i < docs.length - 1 ? docs[i + 1] : null,
  };
}
