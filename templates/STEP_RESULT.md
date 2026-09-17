# Step Result

```text
SCHEMA=review-execute-loop/0.1
PROMPT_ID=<prompt-id>
STEP_ID=<step-id>
STATUS=<COMPLETED-or-PARTIAL-or-BLOCKED>
ACTIVE_BRIEF_ID=<brief-id>
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
RETURN_TARGET=<reviewer-task-id-or-MANUAL>
```
