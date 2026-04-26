import Link from 'next/link';
import { getSearchIndex, groupedDocs } from '@/lib/docs';
import { SidebarNav } from '@/components/SidebarNav';
import { DocsSearch } from '@/components/DocsSearch';

export default function HomePage() {
  const groups = groupedDocs();
  const searchEntries = getSearchIndex();

  // Surface a handful of highlight chapters as entry points for the landing grid.
  const highlights: Array<{ slug: string; eyebrow: string; title: string; blurb: string }> = [
    {
      slug: '01-executive-summary',
      eyebrow: 'Start here',
      title: 'Executive summary',
      blurb: 'Five non-negotiables, five portability commitments, measurable targets.',
    },
    {
      slug: '03-problem-statement',
      eyebrow: 'Why this exists',
      title: 'Eight failure modes (F1–F8)',
      blurb: 'Intent drift, context rot, compounding error, echo chamber, unverifiable claims, runaway cost, prompt injection, silent irreversible actions.',
    },
    {
      slug: '05-architecture-overview',
      eyebrow: 'Architecture',
      title: 'The six-layer stack',
      blurb: 'Human → INTENT → Primary Orchestrator → Orchestrator System → Cohorts → Swarms, with deterministic-verifier and tiered-memory side-flows.',
    },
    {
      slug: '09-signal-consensus',
      eyebrow: 'Consensus',
      title: 'Confidence-interval consensus',
      blurb: 'Three-valued outcome (strengthened / revised / unchanged-but-calibrated). Dissent preserved.',
    },
    {
      slug: '17-worked-example-rental',
      eyebrow: 'Worked example',
      title: 'Rental-acquisition campaign',
      blurb: 'End-to-end run with Research, Finance, Legal, Physical, Ops cohorts and deterministic verifiers.',
    },
    {
      slug: '23-next-report',
      eyebrow: 'Round 2',
      title: 'Reference scaffolding & eval-harness prototype',
      blurb: 'Protocol schemas, Python orchestrator system, Claude Code adapter, rental-toolkit port, regression gates.',
    },
  ];

  return (
    <div className="grid min-h-screen grid-cols-[18rem_1fr] bg-background max-lg:grid-cols-1">
      <SidebarNav />
      <main className="w-full max-w-6xl px-6 py-12 lg:px-14 lg:py-16">
        <section className="mb-10 border-b border-border pb-10">
          <div className="mb-3 text-xs font-semibold uppercase tracking-[0.16em] text-muted-foreground">
            PRD · v0.1.0 · Round 1
          </div>
          <h1 className="max-w-4xl text-5xl font-semibold tracking-[-0.06em] text-foreground sm:text-6xl lg:text-7xl">
            Agentic Harness Orchestration System
          </h1>
          <p className="mt-5 max-w-3xl text-lg leading-8 text-muted-foreground">
            A harness-agnostic architecture for coordinating parallel LLM agents with
            confidence-interval consensus, drift control against an immutable{' '}
            <code>INTENT.md</code>, and deterministic-verifier precedence over any
            LLM opinion.
          </p>
          <p className="mt-4 flex flex-wrap gap-2">
            <span className="rounded-full border border-border bg-muted px-2.5 py-1 text-xs font-medium uppercase tracking-[0.12em] text-foreground">
              23 chapters
            </span>
            <span className="rounded-full border border-border bg-muted px-2.5 py-1 text-xs font-medium uppercase tracking-[0.12em] text-foreground">
              5 appendices
            </span>
            <span className="rounded-full border border-border bg-muted px-2.5 py-1 text-xs font-medium uppercase tracking-[0.12em] text-foreground">
              11 diagrams
            </span>
          </p>
          <div className="mt-6">
            <DocsSearch entries={searchEntries} variant="hero" />
          </div>
        </section>

        <h2 id="highlights" className="mb-4 text-2xl font-semibold tracking-[-0.03em]">
          Highlights
        </h2>
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {highlights.map(h => (
            <Link
              key={h.slug}
              href={`/docs/${h.slug}`}
              className="group rounded-xl border border-border bg-card p-5 text-card-foreground no-underline shadow-sm transition hover:border-border-strong hover:bg-muted"
            >
              <div className="mb-2 text-xs font-semibold uppercase tracking-[0.12em] text-muted-foreground">
                {h.eyebrow}
              </div>
              <h3 className="m-0 text-base font-semibold tracking-[-0.02em] text-foreground">
                {h.title}
              </h3>
              <p className="mt-2 text-sm leading-6 text-muted-foreground">{h.blurb}</p>
            </Link>
          ))}
        </div>

        <h2 id="table-of-contents" className="mb-4 mt-12 text-2xl font-semibold tracking-[-0.03em]">
          Full table of contents
        </h2>
        {groups.map(group => (
          <div key={group.part} className="mb-6 rounded-xl border border-border bg-card p-5">
            <h3 className="m-0 mb-3 text-sm font-semibold uppercase tracking-[0.12em] text-muted-foreground">
              {group.part}
            </h3>
            <ul className="m-0 grid list-none gap-2 p-0 sm:grid-cols-2">
              {group.docs.map(doc => (
                <li key={doc.slug} className="m-0">
                  <Link
                    href={`/docs/${doc.slug}`}
                    className="text-sm text-foreground underline-offset-4 hover:underline"
                  >
                    {doc.title}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        ))}

        <h2 id="portability-note" className="mt-12 text-2xl font-semibold tracking-[-0.03em]">
          Why harness-agnostic
        </h2>
        <p className="max-w-3xl text-muted-foreground">
          This PRD describes a <em>layer</em>, not a product. The protocol schemas
          (Agent Contract, Event Envelope, Consensus Packet, Orchestrator State,
          Memory Index) are portable across Claude Code, Codex CLI, and Cursor via
          thin adapters. See{' '}
          <Link href="/docs/16-adapters">Adapters</Link> and{' '}
          <Link href="/docs/appendices/D-schemas">Appendix D · Protocol schemas</Link>.
        </p>
      </main>
    </div>
  );
}
