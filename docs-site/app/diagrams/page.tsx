import { listDiagrams } from '@/lib/docs';
import { SidebarNav } from '@/components/SidebarNav';
import { Mermaid } from '@/components/Mermaid';

export const metadata = {
  title: 'Diagrams',
};

const DIAGRAM_META: Record<string, { question: string; chapter: string }> = {
  'D01-system-layers':      { question: 'What are the layers of this architecture, top to bottom?',                        chapter: '§05' },
  'D02-orchestrator-system':{ question: 'What are the six sub-responsibilities of the Orchestrator System?',              chapter: '§06' },
  'D03-hub-topology':       { question: 'How does the hub-and-spoke communication topology work?',                         chapter: '§07' },
  'D04-caucus':             { question: 'When peer visibility is granted, how is it scoped?',                              chapter: '§07' },
  'D05-dispatch-tree':      { question: 'How does the harness pick single / serial / parallel / swarm / caucus?',         chapter: '§08' },
  'D06-consensus':          { question: "How does a swarm's output become a Consensus Packet?",                            chapter: '§09' },
  'D07-memory-tiers':       { question: 'How do L0 / L1 / L2 / L3 relate and flow?',                                       chapter: '§10' },
  'D08-drift-loop':         { question: 'How is drift measured continuously and acted on?',                                chapter: '§11' },
  'D09-guardrail-stack':    { question: 'How do the four guardrail classes layer at boundaries?',                          chapter: '§12' },
  'D10-feedback-loops':     { question: 'How do Reflexion / retrospective / eval-harness relate?',                         chapter: '§13' },
  'D11-eval-cadences':      { question: 'How do per-turn / per-task / per-campaign evals flow into config?',               chapter: '§14' },
};

export default function DiagramsPage() {
  const diagrams = listDiagrams();
  return (
    <div className="layout">
      <SidebarNav />
      <main className="site-main">
        <div className="meta">Workspace</div>
        <h1>All diagrams</h1>
        <p>
          Eleven Mermaid diagrams, one per architectural question. Each appears in
          its referenced chapter. This page is an at-a-glance index.
        </p>
        {diagrams.map(d => {
          const meta = DIAGRAM_META[d.id];
          return (
            <section key={d.id} id={d.id} style={{ marginTop: '2rem' }}>
              <h2 style={{ margin: '0 0 0.25rem' }}>
                {d.id}
                {meta && (
                  <span style={{ marginLeft: '0.5rem', color: 'var(--fg-muted)', fontSize: '0.9rem', fontWeight: 400 }}>
                    {meta.chapter}
                  </span>
                )}
              </h2>
              {meta && (
                <p style={{ marginTop: 0, color: 'var(--fg-muted)' }}>{meta.question}</p>
              )}
              <Mermaid chart={d.body} caption={`${d.id}.mermaid`} />
            </section>
          );
        })}
      </main>
    </div>
  );
}
