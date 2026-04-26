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
    <div className="grid min-h-screen grid-cols-[18rem_1fr] bg-background max-lg:grid-cols-1">
      <SidebarNav />
      <main className="w-full max-w-6xl px-6 py-12 lg:px-14 lg:py-16">
        <div className="mb-5 text-xs font-semibold uppercase tracking-[0.16em] text-muted-foreground">
          Workspace
        </div>
        <h1 className="max-w-3xl text-5xl font-semibold tracking-[-0.06em] text-foreground sm:text-6xl">
          All diagrams
        </h1>
        <p className="mt-5 max-w-3xl text-lg leading-8 text-muted-foreground">
          Eleven Mermaid diagrams, one per architectural question. Each appears in
          its referenced chapter. This page is an at-a-glance index.
        </p>
        {diagrams.map(d => {
          const meta = DIAGRAM_META[d.id];
          return (
            <section key={d.id} id={d.id} className="mt-10 rounded-xl border border-border bg-card p-5">
              <h2 className="m-0 text-2xl font-semibold tracking-[-0.03em] text-foreground">
                {d.id}
                {meta && (
                  <span className="ml-2 align-middle text-sm font-normal text-muted-foreground">
                    {meta.chapter}
                  </span>
                )}
              </h2>
              {meta && (
                <p className="mt-1 text-muted-foreground">{meta.question}</p>
              )}
              <Mermaid chart={d.body} caption={`${d.id}.mermaid`} />
            </section>
          );
        })}
      </main>
    </div>
  );
}
