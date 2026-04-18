import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: {
    default: 'Agentic Harness Orchestration System · PRD',
    template: '%s · Harness PRD',
  },
  description:
    'Research-grade PRD for a portable orchestration layer for parallel LLM agents with confidence-interval consensus, drift control, and deterministic-verifier precedence.',
  authors: [{ name: 'Asmattic' }],
  other: {
    'prd-version': '0.1.0',
    'harness-version': '0.1.0',
  },
};

/**
 * We load the Anthropic brand fonts (Poppins for headings, Lora for body) via
 * standard <link> tags rather than `next/font/google`. `next/font/google`
 * fetches at build time, which breaks in air-gapped or offline build envs.
 * The <link> approach fetches on the client and falls back to system fonts
 * (Arial for headings, Georgia for body) if the CDN is unreachable.
 *
 * To self-host the fonts instead, drop WOFF2 files into /public/fonts/ and
 * switch to `next/font/local` in this file.
 */
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          rel="stylesheet"
          href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Lora:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap"
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
