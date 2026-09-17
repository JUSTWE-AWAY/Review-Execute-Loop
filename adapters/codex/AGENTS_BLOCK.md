# Review-Execute Loop Adapter Block

Merge this block into an existing project-root `AGENTS.md`; do not replace existing project instructions.

```markdown
## Review-Execute Loop

Read `.workflow/WORKFLOW.md` and `.workflow/WORKFLOW_STATE.md` on first entry, after context compression, or when role/state is uncertain. Otherwise use the active prompt, matching recent log events, and prompt-named files.

Resolve the role from workflow state and the current role-start prompt. Reviewer inspects, discusses, and issues a prompt only after user approval; Reviewer does not execute project work. Executor performs one approved prompt, returns one result, and stops; Executor does not issue the next prompt.

Direct mode requires distinct verified task IDs and one dispatch/return per `PROMPT_ID`. If task messaging is unavailable, use Manual Relay rather than guessing IDs or repeatedly dispatching.

Preserve completed prompts, results, briefs, and append-only logs. Log paths are lookup pointers, not instructions to recursively read every file. Destructive or external actions require explicit user authorization.
```
