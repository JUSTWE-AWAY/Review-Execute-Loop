# Review-Execute Loop

A lightweight, model-agnostic workflow for long AI-assisted projects.

Review-Execute Loop separates two responsibilities:

- **Reviewer / Orchestrator** inspects results, discusses decisions with the user, and prepares the next approved task.
- **Executor** performs one approved task, records the result, and stops.
- **User** decides whether to continue, revise the goal, hold, or finish.

It works for research, software, writing, analysis, and other multi-step work. It does not require a specific model, paid service, custom skill, or task-management API.

[中文说明](README.zh-CN.md)

## Why Use It?

Long AI tasks often fail because one conversation plans, executes, judges itself, and silently expands the scope. This toolkit introduces a small independent review loop while keeping files and prompts intentionally lean.

The core guarantees are:

- the Executor does not authorize the next task;
- the Reviewer does not execute the task it reviews;
- the user approves each new scope;
- each prompt and result has a stable ID;
- recovery reads the current task and recent state before old history;
- direct task messaging is optional, with a manual copy-paste fallback.

## Two Modes

### Direct Loop

Use when your AI application can send a message from one task or conversation to another.

```text
User <-> Reviewer --approved prompt--> Executor
          ^                            |
          +-------result receipt-------+
```

The Reviewer is the normal user-facing control surface. It writes one complete prompt, dispatches it once, and receives one completion receipt.

### Manual Relay

Use with web chat, different AI products, different machines, or any environment without direct task messaging.

```text
Reviewer prompt -> user copy/paste -> Executor
Executor result -> user copy/paste -> Reviewer
```

Both modes use the same prompt and result contracts. Only transport changes.

## Five-Minute Start

### Option A: Initialize With Python

Python 3.9+ is sufficient; there are no third-party dependencies.

```bash
python tools/init.py /path/to/your-project --profile research --mode direct
```

Profiles: `generic`, `research`, `software`, and `writing`. Modes: `direct` and `manual`.

The initializer never overwrites an existing `.workflow/` directory or `AGENTS.md`. If the project already has `AGENTS.md`, it leaves it untouched and writes a suggested Codex block under `.workflow/`.

### Option B: Manual Setup

1. Copy `starter/.workflow/` into the project root.
2. Copy `templates/` to `.workflow/templates/`.
3. Choose one file from `profiles/` and copy it to `.workflow/PROFILE.md`.
4. For Codex, adapt `starter/AGENTS.md.example` into project-root `AGENTS.md`; preserve existing project instructions.
5. Fill `.workflow/PROJECT_BRIEF.md` and `.workflow/WORKFLOW_STATE.md`.
6. Give `.workflow/templates/EXECUTOR_START.md` to the execution window.
7. Give `.workflow/templates/REVIEWER_START.md` to the review window.

For Direct Loop, bind two distinct task IDs before routine dispatch. For Manual Relay, task IDs may stay `NOT_APPLICABLE`.

## First Project Cycle

1. Discuss the goal in the first window; do not execute yet.
2. Confirm `PROJECT_BRIEF.md` with the user.
3. Let that first window become the Executor and perform setup only.
4. Open a distinct Reviewer, or use a web reviewer in Manual Relay mode.
5. The Reviewer inspects the latest result and discusses the next bounded scope.
6. After user approval, the Reviewer fills `EXECUTION_PROMPT.md`.
7. The Executor performs that prompt, fills one `STEP_RESULT.md`, appends one completion event, and stops.
8. The Reviewer checks the result and repeats the cycle only after another user decision.

## Runtime Files

Only four long-lived project files are required:

| File | Purpose |
|---|---|
| `.workflow/WORKFLOW.md` | Stable roles, safety rules, recovery, and loop behavior |
| `.workflow/PROJECT_BRIEF.md` | Active goal, scope, constraints, and acceptance criteria |
| `.workflow/WORKFLOW_STATE.md` | Mode, role bindings, active prompt, and return target |
| `.workflow/STEP_LOG.md` | Append-only transition log with pointer-only paths |

Each task adds only:

- one complete prompt under `.workflow/prompts/review/`;
- one result record under `.workflow/step_records/`;
- the actual task outputs.

There is no mandatory separate summary, status-flags file, handoff package, evidence ledger, or complete-history reread.

## Context Recovery

- Normal execution: current prompt + matching recent log bundle + prompt-named files.
- New session or compressed context: add `WORKFLOW.md` and role/state confirmation.
- Deep recovery: open an older result only for a concrete missing fact.

Paths in the log are pointers, not instructions to recursively read every file.

## Profiles

Profiles add domain checks without changing the loop:

- `generic`: general task and artifact management;
- `research`: evidence, provenance, and reproducibility proportional to the task;
- `software`: scoped edits, tests, and migration safety;
- `writing`: source fidelity, version preservation, and citation safety.

Do not combine every profile by default. Choose the smallest applicable one.

## Platform Adapters

- `adapters/codex/`: project-root instruction block and direct-task setup.
- `adapters/manual-web/`: web or cross-platform copy-paste procedure.
- `adapters/generic/`: a generic system/developer prompt for other AI tools.

Direct dispatch is an optimization, not a requirement. If a platform cannot address another task reliably, use Manual Relay without changing the workflow state semantics.

## Validate

Validate this distribution:

```bash
python tools/validate.py --distribution .
```

Validate an initialized project:

```bash
python tools/validate.py --project /path/to/your-project
```

The validator is read-only and uses only the Python standard library.

## What This Toolkit Does Not Include

Version 0.1 intentionally excludes server schedulers, publication workflows, evidence databases, multi-agent swarms, automatic Pro escalation, and domain-specific approval ladders. Add those as separate extensions only when a real project needs them.

## License

MIT. See [LICENSE](LICENSE).
