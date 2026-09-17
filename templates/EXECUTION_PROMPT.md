# Execution Prompt

```text
SCHEMA=review-execute-loop/0.1
PROMPT_ID=<unique-id>
STEP_ID=<short-step-id>
BASELINE_STEP_ID=<reviewed-step-id-or-setup>
MODE=<DIRECT-or-MANUAL>
EXECUTOR_TARGET=<verified-task-id-or-MANUAL>
RETURN_TARGET=<verified-reviewer-id-or-MANUAL>
ACTIVE_BRIEF_ID=<brief-id>
USER_APPROVAL=<date/time or concise reference>
REPAIR_BUDGET=<nonnegative integer>
RESULT_PATH=.workflow/step_records/<step-id>_<timestamp>/STEP_RESULT.md
```

## Goal

State one bounded outcome for this task.

## Why This Task

Summarize the reviewed evidence and user decision that justify this scope. Do not paste long history.

## Files To Read

- Required entry files:
- Directly relevant inputs:

These are entry points, not a command to scan unrelated history. Necessary read-only dependency tracing is allowed within scope.

## Allowed Writes

- Paths or files that may be created or modified:
- New version/output location:

## Protected And Forbidden

- Files or paths that must not change:
- Explicitly excluded tasks:
- External or destructive actions not authorized:

## Procedure

1. Describe the minimum work needed.
2. Describe any ordered dependency.
3. State what may be repaired automatically within scope.

Do not add unrelated improvements or domain-wide audits.

## Acceptance Checks

- Minimum checks required for this task:
- Checks that are intentionally not required:

## Early Stop

Stop and return `PARTIAL` or `BLOCKED` if:

- the approved goal or factual baseline is contradicted;
- a protected boundary must change;
- required authorization, input, or credential is missing;
- the repair budget is exhausted;
- continuing would create an external, destructive, privacy, legal, or material cost impact not approved here.

## Required Return

- Create the result at `RESULT_PATH` using `.workflow/templates/STEP_RESULT.md`.
- Record actual work, outputs, checks, skipped checks, repairs, deviations, and decisions needed.
- Append one `EXECUTION_COMPLETED` event.
- Return one concise receipt to `RETURN_TARGET` or the user.
- Stop. Do not prepare the next prompt.
