import type { Metadata } from 'next';
import './globals.css';
import { Geist } from "next/font/google";
import { cn } from "@/lib/utils";

const geist = Geist({subsets:['latin'],variable:'--font-sans'});

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

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={cn("font-sans", geist.variable)}>
      <body className="min-h-screen bg-background text-foreground antialiased">
        {children}
      </body>
    </html>
  );
}
