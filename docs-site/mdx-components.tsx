import type { MDXComponents } from 'mdx/types';
import { Mermaid } from '@/components/Mermaid';

export function useMDXComponents(components: MDXComponents): MDXComponents {
  return {
    Mermaid,
    ...components,
  };
}

export const mdxComponents = {
  Mermaid,
};
