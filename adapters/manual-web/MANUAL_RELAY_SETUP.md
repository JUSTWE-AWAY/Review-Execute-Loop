# Manual Relay Setup

Use when the Reviewer is a web chat, another AI product, another machine, or any environment without reliable direct task messaging.

## Setup

1. Set `MODE=MANUAL` in `.workflow/WORKFLOW_STATE.md`.
2. Set task IDs, task links, and return target to `NOT_APPLICABLE` or `MANUAL`.
3. Initial Setup Facilitator runs the user-approved fixed Step 0 while remaining `EXECUTOR_STATUS=CANDIDATE`.
4. Create one flat per-step packet and zip with `tools/review_packet.py create`.
5. Give the zip to the external Reviewer. The packet itself contains role rules, brief/plan context, result, return template, and execution-prompt template.
6. After review discussion, bring back `REVIEW_RETURN.md` and, only after user approval, `NEXT_EXECUTION_PROMPT.md`.

## Executor To Reviewer

Run the packet creator with the completed `STEP_RESULT.md` and only the key files the Reviewer actually needs. It writes under `.workflow/review_packets/` and creates a matching zip. Local paths are labels only; a remote Reviewer can read only content included in the packet.

## Reviewer To Executor

The Reviewer first returns `REVIEW_RETURN.md` and discusses the decision with the user. After the user approves the exact next scope, Reviewer returns one complete `NEXT_EXECUTION_PROMPT.md`. Use `tools/review_packet.py import` to archive both exact files, update current pointers, append `MANUAL_REVIEW_RETURNED` and `MANUAL_PROMPT_RECEIVED`, and record Step 0 promotion when explicitly approved. Executor does not append a fake `REVIEW_COMPLETED` event or alter the reviewed scope.

Do not ask the user to assemble a separate long handoff, status file, and prompt. The zip is the outbound review transport; `REVIEW_RETURN.md` and one complete prompt are the inbound transport.

## Optional Pro Review

Reviewer may prepare a flat `.workflow/pro_reviews/` folder and optional zip after the user approves a major decision review or cold review. The user carries that packet to a temporary deep-review conversation and returns the complete `PRO_FEEDBACK.md`. Local paths alone are not sufficient for a remote reviewer; attach the numbered files or paste their contents.

The normal Reviewer checks returned feedback against current project facts and discusses adoption with the user. A `PRO_DRAFT_PROMPT` is not copied directly to Executor. Only the later user-approved normal execution prompt enters the Manual Relay.

## Minimal Copy Messages

To the Executor:

```text
This is the user-approved next task. Archive this complete prompt, execute only its scope, return STEP_RESULT, and stop.
```

To the Reviewer:

```text
Read the attached flat review packet. Act only as Reviewer, discuss the next decision with me, and do not draft another execution prompt until I approve its exact scope.
```
