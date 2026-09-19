# Codex Direct Loop Setup

Use this adapter only when the Codex environment can identify tasks and send messages between them.

## Setup

1. Initialize the project and use `.workflow/templates/PROJECT_SETUP_START.md` to approve `PROJECT_BRIEF.md` without starting substantive work.
2. Keep the initial task as Executor.
3. With explicit user approval, create or select a distinct Reviewer task.
4. Record verified IDs in `.workflow/WORKFLOW_STATE.md`:
   - `EXECUTOR_TASK_ID`
   - `REVIEWER_TASK_ID`
   - `RETURN_TARGET_TASK_ID`
5. Set `MODE=DIRECT` only after the IDs are distinct and verified.
6. Give the two tasks their respective start prompts.

## Dispatch

After user approval, Reviewer writes one complete prompt and sends one concise message:

```text
PROMPT_ID=<id>
PROMPT_PATH=<path>
EXECUTOR_TARGET=<id>
RETURN_TARGET=<reviewer-id>
Read the prompt, execute only its scope, return one completion receipt, and stop.
```

Executor returns only the completion receipt from `STEP_RESULT.md`. Reviewer then reads the result and named artifacts. It should not fetch the full execution transcript or every tool output by default.

Before dispatch, Reviewer updates the active step/prompt/approval pointers and sets `PHASE=READY_FOR_EXECUTION`. After completion, Executor updates only the latest result pointer, timestamp, and `PHASE=AWAITING_REVIEW`.

If the send fails or task addressing is unavailable, record the failed delivery once and use the Manual Relay fallback. Do not resend the same prompt ID automatically.

Creating, replacing, archiving, or closing a task is an external state change and requires user approval.
