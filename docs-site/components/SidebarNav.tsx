import Link from 'next/link';
import { groupedDocs } from '@/lib/docs';

export function SidebarNav({ activeSlug }: { activeSlug?: string }) {
  const groups = groupedDocs();
  return (
    <nav className="site-nav" aria-label="Documentation">
      <div className="accent-bar" aria-hidden>
        <span />
        <span />
        <span />
      </div>
      <Link href="/" className="brand">
        Agentic Harness
        <br />
        Orchestration System
      </Link>
      <span className="brand-sub">Round 1 · PRD v0.1.0</span>
      {groups.map(group => (
        <div key={group.part}>
          <h5>{group.part}</h5>
          <ul>
            {group.docs.map(doc => (
              <li key={doc.slug}>
                <Link
                  href={`/docs/${doc.slug}`}
                  className={activeSlug === doc.slug ? 'active' : ''}
                >
                  {doc.title}
                </Link>
              </li>
            ))}
          </ul>
        </div>
      ))}
      <h5>Workspace</h5>
      <ul>
        <li>
          <Link href="/diagrams">All diagrams</Link>
        </li>
      </ul>
    </nav>
  );
}
