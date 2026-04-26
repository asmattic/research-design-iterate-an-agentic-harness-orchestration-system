import Link from 'next/link';
import { getSearchIndex, groupedDocs } from '@/lib/docs';
import { DocsSearch } from '@/components/DocsSearch';
import { cn } from '@/lib/utils';

function sidebarTitle(title: string): string {
  return title
    .replace(/^\s*(?:§\s*)?\d{1,2}\s*(?:[.:·—–-]|\s+)\s*/u, '')
    .trim();
}

export function SidebarNav({ activeSlug }: { activeSlug?: string }) {
  const groups = groupedDocs();
  const searchEntries = getSearchIndex();
  return (
    <nav
      className="sticky top-0 h-screen overflow-y-auto border-r border-border bg-background/90 px-4 py-5 backdrop-blur-xl max-lg:static max-lg:h-auto max-lg:border-r-0 max-lg:border-b"
      aria-label="Documentation"
    >
      <Link href="/" className="grid gap-0.5 text-sm font-semibold leading-5 text-foreground no-underline">
        <span>Agentic Harness</span>
        <small className="text-sm font-medium text-muted-foreground">Orchestration System</small>
      </Link>
      <span className="mb-4 mt-1 block text-xs text-muted-foreground">Round 1 · PRD v0.1.0</span>
      <DocsSearch entries={searchEntries} />
      {groups.map(group => (
        <div key={group.part} className="mt-5">
          <h5 className="mb-2 text-[0.68rem] font-semibold uppercase tracking-[0.12em] text-muted-foreground">
            {group.part}
          </h5>
          <ul className="m-0 list-none p-0">
            {group.docs.map(doc => (
              <li key={doc.slug} className="m-0">
                <Link
                  href={`/docs/${doc.slug}`}
                  aria-current={activeSlug === doc.slug ? 'page' : undefined}
                  className={cn(
                    'block rounded-lg px-2 py-1.5 text-sm leading-5 text-muted-foreground no-underline transition hover:bg-muted hover:text-foreground',
                    activeSlug === doc.slug && 'bg-muted font-medium text-foreground',
                  )}
                >
                  {sidebarTitle(doc.title)}
                </Link>
              </li>
            ))}
          </ul>
        </div>
      ))}
      <h5 className="mb-2 mt-5 text-[0.68rem] font-semibold uppercase tracking-[0.12em] text-muted-foreground">
        Workspace
      </h5>
      <ul className="m-0 list-none p-0">
        <li className="m-0">
          <Link
            href="/diagrams"
            className="block rounded-lg px-2 py-1.5 text-sm leading-5 text-muted-foreground no-underline transition hover:bg-muted hover:text-foreground"
          >
            All diagrams
          </Link>
        </li>
      </ul>
    </nav>
  );
}
