# Pro Review Packet

Create this as `00_PRO_REVIEW_PACKET.md` inside one flat `.workflow/pro_reviews/<pro-review-id>_<timestamp>_<reason>/` folder.

`Pro` means a temporary deep-review role with more time for decision review or independent cold review. It does not name a particular product or model. Pro does not execute project work, modify project artifacts, or authorize the next execution prompt.

```text
SCHEMA=review-execute-loop/0.3
PRO_REVIEW_ID=<unique-id>
REVIEW_KIND=<DECISION_REVIEW-or-COLD_REVIEW>
BASELINE_STEP_ID=<step-id-or-setup>
REQUESTED_BY=<USER-or-REVIEWER>
MODE=<DIRECT-or-MANUAL>
RETURN_TARGET=<reviewer-task-id-or-MANUAL>
USER_APPROVAL=<reference-authorizing-packet-or-send>
```

## Review Mandate

- Exact decision or artifact to review:
- Why ordinary Reviewer analysis is insufficient:
- What this review must not decide or change:

For `COLD_REVIEW`, present the evidence and options neutrally. Do not disclose the Reviewer's preferred answer.

## Project Snapshot

- Project goal:
- Current stage and baseline step:
- Active brief ID:
- Active reference plan, if relevant:
- Protected boundaries:

## Established Facts

- Facts supported by current files or results:
- Important negative results:

## Evidence And Uncertainty

Include the minimum sufficient excerpts, metrics, tables, figures, or logs. Separate observed facts from interpretations.

## Options And Tradeoffs

| Option | Expected benefit | Risk | Cost or reversibility |
|---|---|---|---|
| A |  |  |  |
| B |  |  |  |

## Questions For Pro

1. 
2. 
3. 

## Flat Attachments

| Numbered file | Purpose | Full file or excerpt |
|---|---|---|
| `02_ATTACHMENT_<name>` |  |  |

Do not attach the whole project, large raw data, secrets, or unrelated history.

## Required Return

Discuss the issue with the user when clarification is useful. At the end, return one self-contained Markdown file named `PRO_FEEDBACK.md` using `01_PRO_FEEDBACK_TEMPLATE.md`.

Any suggested next prompt must be marked `PRO_DRAFT_PROMPT`. It is advice only. The normal Reviewer will verify it against current project facts, discuss adoption with the user, and rewrite an approved execution prompt.
