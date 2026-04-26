import { Mermaid } from '@/components/Mermaid';
import type { ElementType } from 'react';

type MDXComponents = Record<string, ElementType>;

type MDXComponents = Record<string, React.ComponentType<any>>;

export function useMDXComponents(components: MDXComponents): MDXComponents {
  return {
    Mermaid,
    ...components,
  };
}

export const mdxComponents = {
  Mermaid,
};
