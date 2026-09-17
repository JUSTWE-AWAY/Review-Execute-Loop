# Step Log

Append-only transition log. Never rewrite, reorder, or delete completed events. Paths are lookup pointers and do not instruct recursive reading.

## Event Schema

```text
### <UTC timestamp> | <EVENT> | <STEP_ID>
PROMPT_ID=<id or NONE>
ROLE=<EXECUTOR or REVIEWER>
STATUS=<COMPLETED, PARTIAL, BLOCKED, APPROVED, HELD, or CLOSED>
ONE_LINE_RESULT=<short factual statement>
RESULT_PATH=<path or NONE>
PROMPT_PATH=<path or NONE>
KEY_FILES=<short comma-separated paths or NONE>
TARGET=<task id, MANUAL, or NONE>
RETURN_TARGET=<task id, MANUAL, or NONE>
USER_APPROVAL=<reference or NONE>
SUPERSEDES=<event reference or NONE>
```

## Setup Events

<!-- Append the first real event below. Do not invent earlier history. -->

In Direct mode, normal events are `EXECUTION_COMPLETED`, `REVIEW_COMPLETED`, and `PROMPT_ISSUED`. In Manual mode, use `EXECUTION_COMPLETED` plus `MANUAL_PROMPT_RECEIVED` when the user delivers an approved remote-review prompt. The latter is a transport/import event written by Executor, not a claim that Executor performed the review.
