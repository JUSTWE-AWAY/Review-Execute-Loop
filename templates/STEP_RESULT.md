# Step Result

```text
SCHEMA=review-execute-loop/0.2
PROMPT_ID=<prompt-id>
STEP_ID=<step-id>
STEP_KIND=<step-kind>
PARENT_STEP_ID=<parent-step-id-or-NONE>
STATUS=<COMPLETED-or-PARTIAL-or-BLOCKED>
ACTIVE_BRIEF_ID=<brief-id>
ACTIVE_REFERENCE_PLAN_ID=<plan-id-or-NONE>
PRO_REVIEW_SOURCE=<pro-review-id-or-NONE>
DELIVERABLE_TARGET=<path-or-NONE>
STARTED_UTC=<timestamp>
FINISHED_UTC=<timestamp>
RETURN_TARGET=<reviewer-task-id-or-MANUAL>
```

## Outcome

One concise paragraph stating what actually happened and the key result.

## Work Performed

- Actions actually completed:
- Important implementation or reasoning choices:

## Files Created Or Changed

| Path | Action | Purpose |
|---|---|---|
| `<path>` | created / modified / unchanged reference | `<purpose>` |

State whether any output was promoted into `deliverables/`. Do not call candidate or exploratory output final.

## Checks

| Check | Result | Evidence |
|---|---|---|
| `<actual check>` | pass / fail / not run | `<output or reason>` |

## Repairs And Deviations

- Technical repair attempts used: `<count>` / `<budget>`
- Deviations from prompt: `<none or exact difference>`
- Checks intentionally not run: `<none or list with reason>`

## Risks Or Decisions Needed

- `<none, or a precise issue requiring Reviewer/user judgment>`

## Recommended Next Action

Recommendation only; this is not authorization to continue.

## Completion Receipt

```text
PROMPT_ID=<prompt-id>
STEP_ID=<step-id>
STATUS=<status>
KEY_RESULT=<one line>
RESULT_PATH=<this file>
KEY_FILES=<short list>
DECISION_NEEDED=<YES-or-NO>
PRO_REVIEW_SOURCE=<pro-review-id-or-NONE>
DELIVERABLES_UPDATED=<short-path-list-or-NONE>
RETURN_TARGET=<reviewer-task-id-or-MANUAL>
```
