'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { SearchIcon } from 'lucide-react';

import type { SearchEntry } from '@/lib/docs';
import { Button } from '@/components/ui/button';
import {
  Command,
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from '@/components/ui/command';
import { cn } from '@/lib/utils';

type Props = {
  entries: SearchEntry[];
  variant?: 'sidebar' | 'hero';
};

export function DocsSearch({ entries, variant = 'sidebar' }: Props) {
  const router = useRouter();
  const [open, setOpen] = useState(false);

  useEffect(() => {
    function onKeyDown(event: KeyboardEvent) {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
        event.preventDefault();
        setOpen(value => !value);
      }
    }

    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, []);

  function navigateTo(entry: SearchEntry) {
    setOpen(false);
    router.push(entry.href);
  }

  return (
    <>
      <Button
        type="button"
        variant="outline"
        onClick={() => setOpen(true)}
        className={cn(
          'w-full justify-between border-border bg-background text-muted-foreground shadow-none hover:bg-muted hover:text-foreground',
          variant === 'hero' && 'h-12 max-w-2xl rounded-xl px-4 text-base',
        )}
      >
        <span className="inline-flex items-center gap-2">
          <SearchIcon className="size-4" />
          Search
        </span>
        <kbd className="hidden rounded-md border bg-muted px-1.5 py-0.5 font-mono text-[10px] text-muted-foreground sm:inline-block">
          ⌘K
        </kbd>
      </Button>

      <CommandDialog
        open={open}
        onOpenChange={setOpen}
        title="Search documentation"
        description="Search documentation."
        className="max-w-2xl border border-border bg-popover shadow-2xl"
      >
        <Command shouldFilter>
          <CommandInput placeholder="Search" />
          <CommandList className="max-h-112">
            <CommandEmpty>No documentation found.</CommandEmpty>
            <CommandGroup heading="Documentation">
              {entries.map(entry => (
                <CommandItem
                  key={entry.slug}
                  value={`${entry.title} ${entry.part}`}
                  keywords={[entry.part, entry.excerpt, entry.text]}
                  onSelect={() => navigateTo(entry)}
                  className="items-start gap-3 py-3"
                >
                  <div className="grid gap-1">
                    <span className="text-xs font-medium uppercase tracking-[0.12em] text-muted-foreground">
                      {entry.part}
                    </span>
                    <span className="font-medium text-foreground">{entry.title}</span>
                    <span className="line-clamp-2 text-xs leading-5 text-muted-foreground">
                      {entry.excerpt}
                    </span>
                  </div>
                </CommandItem>
              ))}
            </CommandGroup>
          </CommandList>
        </Command>
      </CommandDialog>
    </>
  );
}
