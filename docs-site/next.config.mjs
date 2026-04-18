/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Note: the site reads sibling /prd and /diagrams files at build time via
  // lib/docs.ts. Their contents are baked into the prerendered static pages,
  // so no outputFileTracingIncludes is needed. (Turbopack rejects globs that
  // navigate out of the project root.) For `standalone` deployments that
  // need to read the files at runtime, switch to baking them into /public
  // with a prebuild script.
};

export default nextConfig;
