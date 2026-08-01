// Unit tests for lib/preprocess.ts (run with `node --test` from docs-site/,
// Node >= 23.6 strips the TS types natively).
//
// The load-bearing case: diagram filenames mentioned inside markdown table
// rows must NOT be substituted. Splicing a block-level <Mermaid /> into a
// `| cell |` breaks the table and, under next-mdx-remote >= 6, compiles to a
// <Mermaid> whose chart prop is undefined (every embed on the appendix
// diagram-index page rendered "Cannot read properties of undefined").
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import { preprocessMarkdown } from "../lib/preprocess.ts";

const docsSiteDir = dirname(dirname(fileURLToPath(import.meta.url)));
const repoRoot = dirname(docsSiteDir);

test("prose mention of a diagram file is inlined as <Mermaid>", () => {
  const out = preprocessMarkdown(
    "See the flow in D01-system-layers.mermaid for details.",
  );
  assert.match(out, /<Mermaid chart=\{`/);
  assert.match(out, /caption="D01-system-layers\.mermaid"/);
});

test("table-row mention is left untouched", () => {
  const md = [
    "| # | File |",
    "| --- | --- |",
    "| D01 | `D01-system-layers.mermaid` |",
  ].join("\n");
  const out = preprocessMarkdown(md);
  assert.doesNotMatch(out, /<Mermaid/);
  assert.ok(
    out.includes("| D01 | `D01-system-layers.mermaid` |"),
    "table row should survive verbatim",
  );
});

test("table-row mention does not consume the first-reference slot", () => {
  const md = [
    "| # | File |",
    "| --- | --- |",
    "| D01 | `D01-system-layers.mermaid` |",
    "",
    "The prose mention of D01-system-layers.mermaid should still inline.",
  ].join("\n");
  const out = preprocessMarkdown(md);
  assert.match(out, /caption="D01-system-layers\.mermaid"/);
  assert.ok(out.includes("| D01 | `D01-system-layers.mermaid` |"));
});

test("only the first prose mention is inlined", () => {
  const md =
    "First: D01-system-layers.mermaid.\n\nSecond: `D01-system-layers.mermaid`.";
  const out = preprocessMarkdown(md);
  const embeds = out.match(/<Mermaid /g) ?? [];
  assert.equal(embeds.length, 1);
  assert.ok(out.includes("`D01-system-layers.mermaid`"));
});

test("fenced mermaid blocks become <Mermaid>", () => {
  const out = preprocessMarkdown("```mermaid\ngraph TD\nA --> B\n```");
  assert.match(out, /<Mermaid chart=\{`graph TD/);
});

test("appendix A stays a plain table with no embeds", () => {
  const md = readFileSync(
    join(repoRoot, "prd", "appendices", "A-diagram-index.md"),
    "utf-8",
  );
  const out = preprocessMarkdown(md);
  // The appendix prose mentions "`<Mermaid>` component" as inline code —
  // only actual embeds carry a chart prop.
  assert.doesNotMatch(out, /<Mermaid chart=/);
  const rowsIn = md.split("\n").filter((l) => /^\s*\|/.test(l)).length;
  const rowsOut = out.split("\n").filter((l) => /^\s*\|/.test(l)).length;
  assert.equal(rowsOut, rowsIn, "table rows must survive preprocessing");
});
