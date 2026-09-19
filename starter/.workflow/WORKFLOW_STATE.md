# Workflow State

Schema: `review-execute-loop/0.3`

```text
MODE=CHOOSE_DIRECT_OR_MANUAL
PHASE=SETUP
PROFILE=generic
TOOLKIT_VERSION=0.3.0

ACTIVE_BRIEF_ID=BRIEF-001
ACTIVE_BRIEF_PATH=.workflow/PROJECT_BRIEF.md
ACTIVE_REFERENCE_PLAN_ID=NONE
ACTIVE_REFERENCE_PLAN_PATH=NONE
DELIVERABLES_ROOT=deliverables

EXECUTOR_TASK_ID=PENDING_OR_NOT_APPLICABLE
EXECUTOR_TASK_LINK=PENDING_OR_NOT_APPLICABLE
EXECUTOR_STATUS=CANDIDATE
REVIEWER_TASK_ID=PENDING_OR_NOT_APPLICABLE
REVIEWER_TASK_LINK=PENDING_OR_NOT_APPLICABLE
RETURN_TARGET_TASK_ID=PENDING_OR_NOT_APPLICABLE
RETURN_TARGET_TASK_LINK=PENDING_OR_NOT_APPLICABLE

CURRENT_STEP_ID=setup
ACTIVE_PROMPT_ID=NONE
ACTIVE_PROMPT_PATH=NONE
LATEST_RESULT_PATH=NONE

ACTIVE_REVIEW_PACKET_ID=NONE
ACTIVE_REVIEW_PACKET_PATH=NONE

ACTIVE_PRO_REVIEW_ID=NONE
ACTIVE_PRO_REVIEW_PATH=NONE

LAST_USER_APPROVAL=NONE
LAST_UPDATED_UTC=YYYY-MM-DDTHH:MM:SSZ
```

## State Rules

- `MODE` is `DIRECT` or `MANUAL` after setup.
- Direct mode requires distinct verified Executor and Reviewer IDs plus a valid return target.
- Manual mode may use `NOT_APPLICABLE` IDs and links.
- Update this file only for current pointers and bindings. Historical decisions belong in `STEP_LOG.md`.
- Do not infer or invent task IDs.
- Direct Reviewer owns the active prompt, approval, step, and dispatch phase pointers.
- Manual Executor owns those prompt pointers only when importing the exact user-approved prompt.
- Executor owns the latest result pointer and completion phase. Each role updates `LAST_UPDATED_UTC` with its own state change.
- A reference plan is optional and never authorizes execution. Preserve superseded versions.
- Reviewer owns active Pro-review pointers; Pro feedback cannot update execution pointers or authorize a prompt.
- `EXECUTOR_STATUS` remains `CANDIDATE` until independent setup/Step 0 review and user confirmation. Only Reviewer or imported remote-review authorization may promote it to `ACTIVE`.
- Deep links are optional when the platform does not expose them, but Direct mode must preserve them when available.
- Executor owns active Manual review-packet pointers only while packaging or importing external review.
