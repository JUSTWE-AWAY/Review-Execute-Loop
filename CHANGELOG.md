# Changelog

All notable changes to Review-Execute Loop are recorded here.

## 0.3.1 - 2026-09-19

- Fixed the Windows review-packet round-trip smoke test for temporary paths that use short and long aliases.

## 0.3.0 - 2026-09-19

- Added protected project-root `incoming/` for immutable user-supplied starting materials.
- Changed setup to Setup Facilitator and Executor Candidate, with fixed Step 0 before independent review and formal Executor promotion.
- Added per-step flat Manual/Web review packets, zip generation, review-return import, and transport-provenance log events.
- Added distinct task ID and deep-link fields for Direct recovery and navigation.
- Added installation manifests and safe project upgrade check, prepare, conflict, backup, and apply workflows.
- Added compatibility baselines for v0.1.1 and v0.2.0 projects.
- Preserved project briefs, plans, logs, prompts, results, review packets, Pro packets, `AGENTS.md`, `incoming/`, `deliverables/`, code, and data during upgrades.

## 0.2.0 - 2026-09-19

- Added optional model-agnostic Pro decision review and independent cold-review packets.
- Added flat Pro packet and feedback templates with user-controlled adoption.
- Added optional `step0`, structural step IDs, substeps, retries, and forward-recovery rules.
- Added an optional provisional reference plan with explicit fallbacks and versioned route changes.
- Added a protected `deliverables/` convention with stable `001_*`, `002_*` ordering and finer artifact subfolders.
- Preserved existing final-output directories during initialization.
- Kept legacy schema `0.1` project validation available with a warning.

## 0.1.1 - 2026-09-19

- Added a dedicated setup prompt for the first project discussion and role transition.
- Defined minimal ownership rules for active prompt and result pointers.
- Added clone, ZIP, Windows, macOS, and Linux onboarding commands.
- Added cross-platform initializer and validator smoke tests.
- Replaced published environment-specific deny-list literals with generic private-path checks and optional local markers.
- Kept the public introduction focused on supported workflow behavior.

## 0.1.0 - 2026-09-17

- Added the platform-neutral Reviewer/Executor core.
- Added Direct Loop and Manual Relay transports.
- Added lean project starter files and four task profiles.
- Added Codex, manual-web, and generic adapters.
- Added research and software walkthroughs.
- Added dependency-free initialization and validation tools.
