# Software Example: Fix One Failing Test

This example demonstrates a scoped code repair in Direct Loop mode.

## Project Brief Excerpt

```text
Goal: Restore the failing empty-input behavior in the CSV parser.
Scope: Parser implementation and its focused tests.
Out of scope: Parser redesign, CLI changes, dependency upgrades.
Acceptance: Focused test passes and existing parser tests remain green.
Profile: software
Mode: DIRECT
```

## Conversation Flow

1. Executor previously returned one failing test and a stack trace.
2. Reviewer explains the likely boundary error and asks the user whether to authorize a focused fix.
3. User approves only parser behavior and tests.
4. Reviewer creates and dispatches the prompt once.
5. Executor patches the parser, runs the focused suite, returns a result, and stops.
6. Reviewer checks the diff and tests before discussing any next task.

See the filled [prompt](PROMPT_step2_fix_empty_input.md) and [result](STEP_RESULT_step2.md).

## What This Demonstrates

- No unrelated refactor is bundled with the fix.
- One allowed implementation repair does not permit an API redesign.
- Passing the focused suite is reported precisely; an unrun full suite is not implied.
