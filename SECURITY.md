# Security Policy

## Reporting a vulnerability

This repository contains a research PRD, accompanying diagrams, and a static documentation site. It does not run user input in production. That said, if you find a vulnerability — in the docs-site dependencies, in the build pipeline, or in any reference scaffolding added in later rounds — please report it privately.

**Preferred channel:** open a GitHub Security Advisory on this repository (Security tab → "Report a vulnerability"). This keeps the discussion private until a fix is available.

**Fallback:** email mattoldfieldweb@gmail.com with subject prefix `[security]`.

Please include:

- A description of the issue and its impact.
- Steps to reproduce, or a minimal proof-of-concept.
- Affected commit SHA or version tag.
- Whether you have a suggested fix.

I will acknowledge receipt within 5 business days. Coordinated disclosure is appreciated — please give a reasonable window (typically 90 days, shorter if the impact is limited) before public disclosure.

## Supported versions

This is pre-1.0 research-stage software. Only the `main` branch is supported. Older PRD versions remain in git history for reference but receive no security updates.
