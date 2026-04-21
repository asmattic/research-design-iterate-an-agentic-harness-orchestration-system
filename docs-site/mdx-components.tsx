import { Mermaid } from '@/components/Mermaid';

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
