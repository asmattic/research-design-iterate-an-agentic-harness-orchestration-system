import Link from 'next/link';
import { SidebarNav } from '@/components/SidebarNav';

export default function NotFound() {
  return (
    <div className="grid min-h-screen grid-cols-[18rem_1fr] bg-background max-lg:grid-cols-1">
      <SidebarNav />
      <main className="w-full max-w-6xl px-6 py-12 lg:px-14 lg:py-16">
        <div className="mb-5 text-xs font-semibold uppercase tracking-[0.16em] text-muted-foreground">
          404
        </div>
        <h1 className="max-w-3xl text-5xl font-semibold tracking-[-0.06em] text-foreground sm:text-6xl">
          Page not found
        </h1>
        <p className="mt-5 max-w-2xl text-lg leading-8 text-muted-foreground">
          That chapter doesn&apos;t exist in this PRD. Try the{' '}
          <Link href="/" className="text-foreground underline underline-offset-4">
            table of contents
          </Link>
          .
        </p>
      </main>
    </div>
  );
}
