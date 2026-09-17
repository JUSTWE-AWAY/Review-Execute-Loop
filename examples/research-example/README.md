# Research Example: Compare Two Existing Results

This example shows a small exploratory research task. It intentionally does not create a publication evidence package.

## Project Brief Excerpt

```text
Goal: Compare controller A and B on the existing evaluation dataset.
Scope: Reuse existing CSV data; compute success rate and median tracking error.
Out of scope: New simulation, controller modification, paper claims.
Acceptance: One comparison table, reproducible calculation, missing-data warning.
Profile: research
Mode: MANUAL
```

## Conversation Flow

1. Reviewer sees that the dataset already exists and proposes a bounded analysis.
2. User approves comparison only; no new simulation.
3. Reviewer prepares `PROMPT_step1_compare_existing.md`.
4. Executor calculates the metrics and returns `STEP_RESULT.md`.
5. Reviewer checks data coverage and calculation output, then discusses whether a new experiment is worthwhile.

See the filled [prompt](PROMPT_step1_compare_existing.md) and [result](STEP_RESULT_step1.md).

## What This Demonstrates

- The Reviewer does not turn a simple comparison into a formal evidence audit.
- The Executor reports missing rows rather than silently dropping them.
- A recommendation to run a new experiment is not authorization to run it.
