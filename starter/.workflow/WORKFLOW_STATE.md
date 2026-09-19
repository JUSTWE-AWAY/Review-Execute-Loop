# Workflow State

Schema: `review-execute-loop/0.1`

```text
MODE=CHOOSE_DIRECT_OR_MANUAL
PHASE=SETUP
PROFILE=generic

ACTIVE_BRIEF_ID=BRIEF-001
ACTIVE_BRIEF_PATH=.workflow/PROJECT_BRIEF.md

EXECUTOR_TASK_ID=PENDING_OR_NOT_APPLICABLE
REVIEWER_TASK_ID=PENDING_OR_NOT_APPLICABLE
RETURN_TARGET_TASK_ID=PENDING_OR_NOT_APPLICABLE

CURRENT_STEP_ID=setup
ACTIVE_PROMPT_ID=NONE
ACTIVE_PROMPT_PATH=NONE
LATEST_RESULT_PATH=NONE

LAST_USER_APPROVAL=NONE
LAST_UPDATED_UTC=YYYY-MM-DDTHH:MM:SSZ
```

## State Rules

- `MODE` is `DIRECT` or `MANUAL` after setup.
- Direct mode requires distinct verified Executor and Reviewer IDs plus a valid return target.
- Manual mode may use `NOT_APPLICABLE` IDs.
- Update this file only for current pointers and bindings. Historical decisions belong in `STEP_LOG.md`.
- Do not infer or invent task IDs.
- Direct Reviewer owns the active prompt, approval, step, and dispatch phase pointers.
- Manual Executor owns those prompt pointers only when importing the exact user-approved prompt.
- Executor owns the latest result pointer and completion phase. Each role updates `LAST_UPDATED_UTC` with its own state change.
