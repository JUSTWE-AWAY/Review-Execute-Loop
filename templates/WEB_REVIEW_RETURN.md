# Review Return

Return this as `REVIEW_RETURN.md`. It is archived by the local Executor as external-review provenance; the Executor does not rewrite it or claim authorship.

```text
SCHEMA=review-execute-loop/0.3
REVIEW_PACKET_ID=<matching-id>
STEP_ID=<reviewed-step-id>
REVIEW_STATUS=<ACCEPT-or-REVISE-or-RECOVER-or-HOLD-or-CLOSE>
EXECUTOR_PROMOTION=<APPROVE-or-NOT_APPLICABLE-or-DO_NOT_APPROVE>
NEXT_PROMPT_APPROVED=<YES-or-NO>
USER_APPROVAL=<reference-or-NONE>
```

## Review Summary


## Evidence Checked


## Findings And Risks


## Discussion Outcome


## Required Corrections Or Next Scope


## Brief Or Plan Decision

- Brief remains valid:
- Reference-plan revision needed:
- Pro review recommended:

## Files The Next Prompt May Reference


This return records review judgment only. If `NEXT_PROMPT_APPROVED=YES`, provide a separate complete `NEXT_EXECUTION_PROMPT.md`. Do not embed partial instructions that Executor could mistake for an executable prompt.
