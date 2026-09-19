# Changelog

All notable changes to Review-Execute Loop are recorded here.

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
