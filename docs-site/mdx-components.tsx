import { Mermaid } from '@/components/Mermaid';
import type { ElementType } from 'react';

type MDXComponents = Record<string, ElementType>;

export function useMDXComponents(components: MDXComponents): MDXComponents {
  return {
    Mermaid,
    ...components,
  };
}

export const mdxComponents = {
  Mermaid,
};
