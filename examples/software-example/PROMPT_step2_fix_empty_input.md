# Execution Prompt

```text
SCHEMA=review-execute-loop/0.2
PROMPT_ID=SW-002
STEP_ID=step2
STEP_KIND=MAIN
PARENT_STEP_ID=NONE
BASELINE_STEP_ID=step1
MODE=DIRECT
EXECUTOR_TARGET=executor-task-id
RETURN_TARGET=reviewer-task-id
ACTIVE_BRIEF_ID=BRIEF-001
ACTIVE_REFERENCE_PLAN_ID=NONE
PRO_REVIEW_SOURCE=NONE
DELIVERABLE_TARGET=NONE
USER_APPROVAL=approved focused parser fix
REPAIR_BUDGET=1
RESULT_PATH=.workflow/step_records/step2_example/STEP_RESULT.md
```

## Goal

Make the CSV parser return an empty collection for an empty input instead of raising an index error.

## Files To Read

- `src/csv_parser.py`
- `tests/test_csv_parser.py`
- the failing traceback in the previous result

## Allowed Writes

- `src/csv_parser.py`
- `tests/test_csv_parser.py`
- the required result record

## Protected And Forbidden

- Do not change the public function signature.
- Do not refactor unrelated parsing behavior.
- Do not upgrade dependencies.

## Acceptance Checks

- Add or preserve a focused empty-input regression test.
- Run the parser test module.
- Report whether the full test suite was run.

## Early Stop

Stop if the expected empty-input behavior conflicts with documented API behavior.

## Required Return

Write one result, append `EXECUTION_COMPLETED`, return one receipt to the Reviewer, and stop.
