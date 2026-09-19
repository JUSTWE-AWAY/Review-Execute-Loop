# Review-Execute Loop Adapter Block

Merge this block into an existing project-root `AGENTS.md`; do not replace existing project instructions.

```markdown
## Review-Execute Loop

Read `.workflow/WORKFLOW.md` and `.workflow/WORKFLOW_STATE.md` on first entry, after context compression, or when role/state is uncertain. Otherwise use the active prompt, matching recent log events, and prompt-named files.

Resolve the role from workflow state and the current role-start prompt. Reviewer inspects, discusses, and issues a prompt only after user approval; Reviewer does not execute project work. Executor performs one approved prompt, returns one result, and stops; Executor does not issue the next prompt.

The initial task is Setup Facilitator / Executor Candidate. It may run only the fixed user-approved Step 0 and becomes active Executor only after independent review acceptance and user confirmation.

Pro Reviewer is an optional temporary deep-review role, not a model name. It returns advice in `PRO_FEEDBACK.md` and never authorizes or executes project work. The normal Reviewer and user decide whether to adopt that advice.

Direct mode requires distinct verified task IDs and one dispatch/return per `PROMPT_ID`. If task messaging is unavailable, use Manual Relay rather than guessing IDs or repeatedly dispatching.

Preserve completed prompts, results, briefs, and append-only logs. Log paths are lookup pointers, not instructions to recursively read every file. Destructive or external actions require explicit user authorization.

Treat project-root `incoming/` as immutable user source material. Never edit, rename, move, overwrite, quarantine, or delete it. Write all derived work elsewhere.

Keep approved final outputs under `deliverables/` using stable three-digit folder prefixes. Do not place candidates there before user-approved promotion.
```
