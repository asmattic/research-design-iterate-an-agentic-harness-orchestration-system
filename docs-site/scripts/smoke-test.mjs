import { existsSync, readdirSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const docsSiteDir = dirname(dirname(fileURLToPath(import.meta.url)));
const repoRoot = dirname(docsSiteDir);

const checks = [];

function check(name, condition, detail) {
  checks.push({ name, passed: Boolean(condition), detail });
}

function markdownFiles(dir) {
  if (!existsSync(dir)) {
    return [];
  }

  return readdirSync(dir).filter((file) => file.endsWith(".md"));
}

const prdDir = join(repoRoot, "prd");
const diagramsDir = join(repoRoot, "diagrams");
const prdFiles = markdownFiles(prdDir);
const diagramFiles = existsSync(diagramsDir)
  ? readdirSync(diagramsDir).filter((file) => file.endsWith(".mermaid"))
  : [];

check("PRD markdown source exists", prdFiles.length > 0, `${prdFiles.length} markdown files found`);
check("Mermaid diagram source exists", diagramFiles.length > 0, `${diagramFiles.length} diagram files found`);
check("Docs manifest module exists", existsSync(join(docsSiteDir, "lib", "docs.ts")));
check("Global search component exists", existsSync(join(docsSiteDir, "components", "DocsSearch.tsx")));
check("App router root page exists", existsSync(join(docsSiteDir, "app", "page.tsx")));

const packageJson = JSON.parse(readFileSync(join(docsSiteDir, "package.json"), "utf8"));

check("Build script is registered", packageJson.scripts?.build === "next build");
check("Typecheck script is registered", Boolean(packageJson.scripts?.typecheck));
check("test:js includes build verification", packageJson.scripts?.["test:js"]?.includes("pnpm run build"));

const failed = checks.filter((item) => !item.passed);

for (const item of checks) {
  const suffix = item.detail ? ` (${item.detail})` : "";
  console.log(`${item.passed ? "PASS" : "FAIL"} ${item.name}${suffix}`);
}

if (failed.length > 0) {
  console.error(`Smoke test failed: ${failed.map((item) => item.name).join(", ")}`);
  process.exit(1);
}
