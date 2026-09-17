# Manual Relay Setup

Use when the Reviewer is a web chat, another AI product, another machine, or any environment without reliable direct task messaging.

## Setup

1. Set `MODE=MANUAL` in `.workflow/WORKFLOW_STATE.md`.
2. Set task IDs and return target to `NOT_APPLICABLE` or `MANUAL`.
3. Give the Reviewer `.workflow/templates/REVIEWER_START.md`, the active project brief, the selected profile, and the latest result text.
4. Give the Executor `.workflow/templates/EXECUTOR_START.md` and the user-approved complete prompt.

## Executor To Reviewer

Copy the `Completion Receipt` and the concise content of `STEP_RESULT.md`. Upload only files the Reviewer actually needs. Local paths are useful labels but are not readable by a remote web reviewer unless the corresponding files are uploaded.

## Reviewer To Executor

The Reviewer should return one complete prompt following `.workflow/templates/EXECUTION_PROMPT.md` plus a short review receipt. The user approves it before transfer. The Executor archives that exact prompt under `.workflow/prompts/review/`, preserves its unique `PROMPT_ID` (or assigns one only when missing), appends `MANUAL_PROMPT_RECEIVED` with the approval reference, and then executes it. Executor does not append a fake `REVIEW_COMPLETED` event or alter the reviewed scope.

Do not ask the user to copy a separate long handoff, status file, and prompt when one complete result or prompt is sufficient.

## Minimal Copy Messages

To the Executor:

```text
This is the user-approved next task. Archive this complete prompt, execute only its scope, return STEP_RESULT, and stop.
```

To the Reviewer:

```text
Review the following STEP_RESULT and named evidence. Discuss the next decision with me before drafting another execution prompt.
```
