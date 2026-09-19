# Step Log

Append-only transition log. Never rewrite, reorder, or delete completed events. Paths are lookup pointers and do not instruct recursive reading.

## Event Schema

```text
### <UTC timestamp> | <EVENT> | <STEP_ID>
PROMPT_ID=<id or NONE>
ROLE=<EXECUTOR or REVIEWER>
SOURCE_ROLE=<LOCAL_EXECUTOR, LOCAL_REVIEWER, REMOTE_REVIEWER, USER, or NONE>
STATUS=<COMPLETED, PARTIAL, BLOCKED, APPROVED, HELD, or CLOSED>
ONE_LINE_RESULT=<short factual statement>
RESULT_PATH=<path or NONE>
PROMPT_PATH=<path or NONE>
KEY_FILES=<short comma-separated paths or NONE>
TARGET=<task id, MANUAL, or NONE>
RETURN_TARGET=<task id, MANUAL, or NONE>
USER_APPROVAL=<reference or NONE>
SUPERSEDES=<event reference or NONE>
PRO_REVIEW_ID=<id or NONE>
REVIEW_PACKET_ID=<id or NONE>
```

## Setup Events

<!-- Append the first real event below. Do not invent earlier history. -->

In Direct mode, normal events are `EXECUTION_COMPLETED`, `REVIEW_COMPLETED`, and `PROMPT_ISSUED`. In Manual mode, use `EXECUTION_COMPLETED` plus `MANUAL_PROMPT_RECEIVED` when the user delivers an approved remote-review prompt. The latter is a transport/import event written by Executor, not a claim that Executor performed the review.

Setup may add `STEP0_COMPLETED`, `REVIEW_PACKET_CREATED`, and `EXECUTOR_PROMOTED`. Manual review adds `MANUAL_REVIEW_RETURNED` before `MANUAL_PROMPT_RECEIVED`. For both transport events, set `ROLE=EXECUTOR` and `SOURCE_ROLE=REMOTE_REVIEWER`; the event records import provenance and does not claim Executor performed review.

When Pro review is actually used, append `PRO_REVIEW_REQUESTED`, `PRO_REVIEW_RETURNED`, and `PRO_REVIEW_DECIDED` as the corresponding transitions occur. Do not add empty Pro events to ordinary steps. The decision event records adopt, partial adopt, defer, or reject in `ONE_LINE_RESULT` and cites user approval.
