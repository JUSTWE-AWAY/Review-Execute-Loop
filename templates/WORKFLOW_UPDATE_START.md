# Workflow Update Start Prompt

You are performing a local workflow-maintenance task for this project. This does not authorize project implementation or changes to project-owned artifacts.

1. Run the updater in `--check` mode first. It is read-only.
2. If an update is available, run `--prepare` and report safe additions, safe replacements, structured migrations, conflicts, and untouched project-owned files.
3. Stop for explicit user approval before `--apply`.
4. Apply only the approved upgrade ID.
5. Validate the project and report any unresolved conflicts.

Never overwrite `AGENTS.md`, project briefs, approved plans, logs, prompts, results, review packets, Pro packets, `incoming/`, `deliverables/`, source code, data, or user outputs. Back up replaced managed files inside the upgrade record. Do not physically delete retired files.
