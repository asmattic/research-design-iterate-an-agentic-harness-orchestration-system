'use client';

import { useEffect, useId, useRef, useState } from 'react';

type Props = {
  chart: string;
  caption?: string;
};

/**
 * Client-side Mermaid renderer.
 *
 * Why client-side: mermaid.js depends on browser DOM (SVG measurement, text
 * layout). Rendering server-side would require headless browser work and
 * add build complexity for no gain — the docs site is static enough that
 * client render latency is invisible.
 *
 * How: each instance generates a unique id, initializes the mermaid library
 * once per page with the Anthropic theme variables, and renders on mount.
 */
export function Mermaid({ chart, caption }: Props) {
  const uid = useId().replace(/[^a-zA-Z0-9_-]/g, '');
  const id = `mm-${uid}`;
  const ref = useRef<HTMLDivElement>(null);
  const [svg, setSvg] = useState<string>('');
  const [error, setError] = useState<string>('');

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const mermaid = (await import('mermaid')).default;

        // Theme picked up from Anthropic brand tokens (see app/globals.css).
        // We initialize once per mount — mermaid.initialize is idempotent.
        const dark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        mermaid.initialize({
          startOnLoad: false,
          securityLevel: 'strict',
          fontFamily: "'Lora', 'Georgia', serif",
          theme: 'base',
          themeVariables: {
            background: dark ? '#1e1d1b' : '#faf9f5',
            primaryColor: dark ? '#2d2c29' : '#e8e6dc',
            primaryTextColor: dark ? '#faf9f5' : '#141413',
            primaryBorderColor: dark ? '#4a4842' : '#b0aea5',
            lineColor: dark ? '#b0aea5' : '#585856',
            secondaryColor: '#d97757',
            tertiaryColor: '#6a9bcc',
            fontSize: '14px',
          },
        });

        const { svg } = await mermaid.render(id, chart);
        if (!cancelled) setSvg(svg);
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : String(e));
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [chart, id]);

  if (error) {
    return (
      <figure className="mermaid-wrap" role="img" aria-label="mermaid error">
        <pre>Mermaid render error:{'\n'}{error}</pre>
      </figure>
    );
  }

  return (
    <figure className="mermaid-wrap">
      <div ref={ref} dangerouslySetInnerHTML={{ __html: svg }} />
      {caption && <figcaption className="mermaid-caption">{caption}</figcaption>}
    </figure>
  );
}
