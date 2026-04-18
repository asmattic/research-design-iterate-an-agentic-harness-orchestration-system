import Link from 'next/link';
import { SidebarNav } from '@/components/SidebarNav';

export default function NotFound() {
  return (
    <div className="layout">
      <SidebarNav />
      <main className="site-main">
        <div className="meta">404</div>
        <h1>Page not found</h1>
        <p>
          That chapter doesn&apos;t exist in this PRD. Try the{' '}
          <Link href="/">table of contents</Link>.
        </p>
      </main>
    </div>
  );
}
