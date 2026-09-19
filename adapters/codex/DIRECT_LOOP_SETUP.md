# Codex Direct Loop Setup

Use this adapter only when the Codex environment can identify tasks and send messages between them.

## Setup

1. Initialize the project, place prior materials under protected `incoming/`, and use `.workflow/templates/PROJECT_SETUP_START.md` to approve the brief and Step 0 scope.
2. Keep the initial task as Setup Facilitator / Executor Candidate. Record its verified ID and deep link when available.
3. Run the fixed `.workflow/templates/STEP0_START.md` after user approval and stop with a Step 0 result.
4. With explicit user approval, create or select a distinct Reviewer task.
5. Record verified IDs and deep links in `.workflow/WORKFLOW_STATE.md`:
   - `EXECUTOR_TASK_ID`
   - `EXECUTOR_TASK_LINK`
   - `REVIEWER_TASK_ID`
   - `REVIEWER_TASK_LINK`
   - `RETURN_TARGET_TASK_ID`
   - `RETURN_TARGET_TASK_LINK`
6. Reviewer checks Step 0. Promote `EXECUTOR_STATUS` from `CANDIDATE` to `ACTIVE` only after accepted review and user confirmation.
7. `MODE=DIRECT` may be selected during setup, but routine dispatch remains blocked until distinct verified IDs and return targets are recorded. Then give the tasks their respective start prompts.

## Dispatch

After user approval, Reviewer writes one complete prompt and sends one concise message:

```text
PROMPT_ID=<id>
PROMPT_PATH=<path>
EXECUTOR_TARGET=<id>
RETURN_TARGET=<reviewer-id>
EXECUTOR_TASK_LINK=<executor-link-or-NONE>
REVIEWER_TASK_LINK=<reviewer-link-or-NONE>
Read the prompt, execute only its scope, return one completion receipt, and stop.
```

Executor returns only the completion receipt from `STEP_RESULT.md`. Reviewer then reads the result and named artifacts. It should not fetch the full execution transcript or every tool output by default.

Before dispatch, Reviewer updates the active step/prompt/approval pointers and sets `PHASE=READY_FOR_EXECUTION`. After completion, Executor updates only the latest result pointer, timestamp, and `PHASE=AWAITING_REVIEW`.

If the send fails or task addressing is unavailable, record the failed delivery once and use the Manual Relay fallback. Do not resend the same prompt ID automatically.

Creating, replacing, archiving, or closing a task is an external state change and requires user approval.

## Optional Pro Review

When the user approves a deep decision review or cold review, Reviewer creates the flat packet under `.workflow/pro_reviews/`, records the active Pro-review pointers, and may create or select a distinct temporary Pro task only with user approval. Send the packet path and return target once. Pro returns `PRO_FEEDBACK.md` to Reviewer and does not contact Executor with an executable prompt.

After feedback returns, Reviewer discusses adopt, partial adopt, defer, or reject with the user. Only an approved normal `EXECUTION_PROMPT.md` may be dispatched to Executor. Archive or close a temporary Pro task only with user approval.
