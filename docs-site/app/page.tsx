import Link from 'next/link';
import { groupedDocs } from '@/lib/docs';
import { SidebarNav } from '@/components/SidebarNav';

export default function HomePage() {
  const groups = groupedDocs();

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
    <div className="layout">
      <SidebarNav />
      <main className="site-main">
        <section className="hero">
          <div className="eyebrow">PRD · v0.1.0 · Round 1</div>
          <h1>Agentic Harness Orchestration System</h1>
          <p className="lede">
            A harness-agnostic architecture for coordinating parallel LLM agents with
            confidence-interval consensus, drift control against an immutable{' '}
            <code>INTENT.md</code>, and deterministic-verifier precedence over any
            LLM opinion.
          </p>
          <p className="lede" style={{ marginTop: '0.6rem' }}>
            <span className="badge">23 chapters</span>
            <span className="badge blue">5 appendices</span>
            <span className="badge green">11 diagrams</span>
          </p>
        </section>

        <h2 id="highlights">Highlights</h2>
        <div className="card-grid">
          {highlights.map(h => (
            <Link key={h.slug} href={`/docs/${h.slug}`} className="card">
              <div className="card-eyebrow">{h.eyebrow}</div>
              <h3>{h.title}</h3>
              <p>{h.blurb}</p>
            </Link>
          ))}
        </div>

        <h2 id="table-of-contents">Full table of contents</h2>
        {groups.map(group => (
          <div key={group.part} style={{ marginBottom: '1.4rem' }}>
            <h3 style={{ fontSize: '1rem', marginBottom: '0.3rem' }}>{group.part}</h3>
            <ul>
              {group.docs.map(doc => (
                <li key={doc.slug}>
                  <Link href={`/docs/${doc.slug}`}>{doc.title}</Link>
                </li>
              ))}
            </ul>
          </div>
        ))}

        <h2 id="portability-note">Why harness-agnostic</h2>
        <p>
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
