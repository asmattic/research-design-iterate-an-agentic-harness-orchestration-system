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
    <div className="layout">
      <SidebarNav activeSlug={fullSlug} />
      <main className="site-main">
        <article>
          <div className="meta">{doc.part}</div>
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
          <div className="pager">
            {prev ? (
              <Link href={`/docs/${prev.slug}`} aria-label={`Previous: ${prev.title}`}>
                <small>← Previous</small>
                {prev.title}
              </Link>
            ) : (
              <span />
            )}
            {next ? (
              <Link
                href={`/docs/${next.slug}`}
                aria-label={`Next: ${next.title}`}
                style={{ textAlign: 'right' }}
              >
                <small>Next →</small>
                {next.title}
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
