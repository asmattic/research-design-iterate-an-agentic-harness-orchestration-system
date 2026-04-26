import { Mermaid } from '@/components/Mermaid';
import type { MDXComponents } from 'mdx/types';

export function useMDXComponents(components: MDXComponents): MDXComponents {
  return {
    Mermaid,
    ...components,
  };
}

export const mdxComponents = {
  Mermaid,
};
