# External Review Packet

Create this as `00_REVIEW_PACKET.md` inside one flat `.workflow/review_packets/<step-id>_<timestamp>_review/` folder.

You are the independent Reviewer / Orchestrator. You are not the Executor. Read this packet and its numbered attachments, review the completed step, and discuss your findings with the user before drafting any next execution prompt. Do not edit project outputs or claim access to local paths that were not attached.

The Executor performs only a user-approved prompt and stops after returning one result. It cannot approve its own work, promote itself after Step 0, or create the next task scope.

```text
SCHEMA=review-execute-loop/0.3
REVIEW_PACKET_ID=<unique-id>
STEP_ID=<reviewed-step-id>
MODE=MANUAL
EXECUTOR_TASK_ID=<id-or-NOT_APPLICABLE>
EXECUTOR_TASK_LINK=<link-or-NOT_APPLICABLE>
REVIEWER_TASK_ID=NOT_APPLICABLE
REVIEWER_TASK_LINK=NOT_APPLICABLE
```

## Project Goal And Boundaries

- Active brief ID:
- Goal:
- Protected boundaries:
- Final deliverables:

## Current Route

- Active reference plan ID or `NONE`:
- Current route summary:
- Known fallbacks:

## Reviewed Step

- Prompt ID:
- Step ID and kind:
- Result status:
- Key outcome:
- Repairs or deviations:
- Decisions requested:

## Step Result

Paste the complete `STEP_RESULT.md` here unless it is attached as a numbered file.

## Key Evidence And Attachments

| Numbered file | Purpose | Complete or excerpted |
|---|---|---|
| `03_ATTACHMENT_<name>` |  |  |

## Review Questions

1. Was the approved scope actually completed?
2. Are the claimed checks and evidence sufficient for this step?
3. Are there material errors, unsupported conclusions, or boundary violations?
4. Does the active brief still fit, and is plan revision or Pro review needed?
5. What is the smallest sensible next action: accept, revise, recover, hold, or close?

## Required Interaction And Return

First report findings and discuss them with the user. Do not draft the full next prompt before the user approves the exact scope.

Return one `REVIEW_RETURN.md` using `01_REVIEW_RETURN_TEMPLATE.md`. For Step 0, explicitly state whether Executor promotion is approved. After the user approves a next scope, return one complete `NEXT_EXECUTION_PROMPT.md` using `02_EXECUTION_PROMPT_TEMPLATE.md`.
