# Execution Prompt

```text
SCHEMA=review-execute-loop/0.1
PROMPT_ID=RP-001
STEP_ID=step1
BASELINE_STEP_ID=setup
MODE=MANUAL
EXECUTOR_TARGET=MANUAL
RETURN_TARGET=MANUAL
ACTIVE_BRIEF_ID=BRIEF-001
USER_APPROVAL=approved comparison-only scope
REPAIR_BUDGET=1
RESULT_PATH=.workflow/step_records/step1_example/STEP_RESULT.md
```

## Goal

Compare controller A and B using only the existing evaluation CSV.

## Files To Read

- `data/evaluation.csv`
- `scripts/metrics.py`

## Allowed Writes

- `analysis/step1/controller_comparison.csv`
- `analysis/step1/run_metrics.py`
- the required result record

## Protected And Forbidden

- Do not edit source data or controller code.
- Do not run a new simulation.
- Do not write manuscript claims.

## Acceptance Checks

- Report row counts and missing values.
- Calculate success rate and median tracking error once with the saved script.
- Confirm the output table can be regenerated from the named input.

## Early Stop

Stop if controller labels or metric columns do not match the brief. Do not guess their meaning.

## Required Return

Write one result record, append `EXECUTION_COMPLETED`, return the receipt, and stop.
