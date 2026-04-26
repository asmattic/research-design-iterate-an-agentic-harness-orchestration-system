import Link from 'next/link';
import { notFound } from 'next/navigation';
import { MDXRemote } from 'next-mdx-remote/rsc';
import remarkGfm from 'remark-gfm';
import rehypeSlug from 'rehype-slug';
import rehypeAutolinkHeadings from 'rehype-autolink-headings';

import { DOC_MANIFEST, getDoc, prevNextOf } from '@/lib/docs';
import { SidebarNav } from '@/components/SidebarNav';
import { Mermaid } from '@/components/Mermaid';
import { preprocessMarkdown } from '@/lib/preprocess';

export function generateStaticParams() {
  return DOC_MANIFEST.map(entry => ({
    slug: entry.slug.split('/'),
  }));
}

export const dynamicParams = false;

interface PageProps {
  params: Promise<{ slug: string[] }>;
}

export async function generateMetadata({ params }: PageProps) {
  const { slug } = await params;
  const doc = getDoc(slug.join('/'));
  if (!doc) return { title: 'Not found' };
  return { title: doc.title };
}

export default async function DocPage({ params }: PageProps) {
  const { slug } = await params;
  const fullSlug = slug.join('/');
  const doc = getDoc(fullSlug);
  if (!doc) notFound();

  const { prev, next } = prevNextOf(fullSlug);
  const preprocessed = preprocessMarkdown(doc.body);

  return (
    <div className="grid min-h-screen grid-cols-[18rem_1fr] bg-background max-lg:grid-cols-1">
      <SidebarNav activeSlug={fullSlug} />
      <main className="w-full max-w-6xl px-6 py-12 lg:px-14 lg:py-16">
        <article className="docs-prose max-w-3xl">
          <div className="mb-5 text-xs font-semibold uppercase tracking-[0.16em] text-muted-foreground">
            {doc.part}
          </div>
          <h1>{doc.title}</h1>
          <MDXRemote
            source={preprocessed}
            components={{ Mermaid }}
            options={{
              mdxOptions: {
                remarkPlugins: [remarkGfm],
                rehypePlugins: [
                  rehypeSlug,
                  [rehypeAutolinkHeadings, { behavior: 'wrap' }],
                ],
              },
            }}
          />
          <div className="mt-12 grid gap-3 border-t border-border pt-6 sm:grid-cols-2">
            {prev ? (
              <Link
                href={`/docs/${prev.slug}`}
                aria-label={`Previous: ${prev.title}`}
                className="rounded-xl border border-border bg-card p-4 text-card-foreground no-underline transition hover:bg-muted"
              >
                <small className="mb-1 block text-xs font-medium uppercase tracking-[0.12em] text-muted-foreground">
                  ← Previous
                </small>
                <span className="font-medium">{prev.title}</span>
              </Link>
            ) : (
              <span />
            )}
            {next ? (
              <Link
                href={`/docs/${next.slug}`}
                aria-label={`Next: ${next.title}`}
                className="rounded-xl border border-border bg-card p-4 text-right text-card-foreground no-underline transition hover:bg-muted"
              >
                <small className="mb-1 block text-xs font-medium uppercase tracking-[0.12em] text-muted-foreground">
                  Next →
                </small>
                <span className="font-medium">{next.title}</span>
              </Link>
            ) : (
              <span />
            )}
          </div>
        </article>
      </main>
    </div>
  );
}
