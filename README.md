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
- major decisions can pause for an optional model-agnostic Pro Review without bypassing user approval.

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

First obtain the toolkit:

```bash
git clone https://github.com/JUSTWE-AWAY/Review-Execute-Loop.git
cd Review-Execute-Loop
```

Alternatively, use GitHub's **Code > Download ZIP**, extract it, and open a terminal in the extracted folder.

### Option A: Initialize With Python

Python 3.9+ is sufficient; there are no third-party dependencies.

Windows:

```powershell
py -3 tools/init.py E:/path/to/project --profile research --mode direct
```

macOS or Linux:

```bash
python3 tools/init.py /path/to/your-project --profile research --mode direct
```

Profiles: `generic`, `research`, `software`, and `writing`. Modes: `direct` and `manual`.

The initializer never overwrites an existing `.workflow/` directory, `AGENTS.md`, or `deliverables/` directory. If the project already has `AGENTS.md`, it leaves it untouched and writes a suggested Codex block under `.workflow/`.

### Option B: Manual Setup

1. Copy `starter/.workflow/` into the project root.
2. Copy `starter/deliverables/` into the project root only when the project does not already have a final-output directory.
3. Copy `templates/` to `.workflow/templates/`.
4. Choose one file from `profiles/` and copy it to `.workflow/PROFILE.md`.
5. For Codex, adapt `starter/AGENTS.md.example` into project-root `AGENTS.md`; preserve existing project instructions.
6. Give `.workflow/templates/PROJECT_SETUP_START.md` to the first project window.
7. After setup is approved, give `.workflow/templates/EXECUTOR_START.md` to that window.
8. Give `.workflow/templates/REVIEWER_START.md` to the independent review window.

For Direct Loop, bind two distinct task IDs before routine dispatch. For Manual Relay, task IDs may stay `NOT_APPLICABLE`.

## First Project Cycle

1. Give the first window `.workflow/templates/PROJECT_SETUP_START.md` and discuss the goal; do not execute project work yet.
2. Confirm `PROJECT_BRIEF.md` with the user.
3. Let that first window become the Executor and perform setup only.
4. Open a distinct Reviewer, or use a web reviewer in Manual Relay mode.
5. For an existing or complex project, Reviewer may first issue an optional `step0` baseline inventory; a simple project may start at `step1`.
6. The Reviewer inspects the latest result and discusses the next bounded scope.
7. After user approval, the Reviewer fills `EXECUTION_PROMPT.md`.
8. The Executor performs that prompt, fills one `STEP_RESULT.md`, appends one completion event, and stops.
9. The Reviewer checks the result and repeats the cycle only after another user decision.

## Runtime Files

Only four long-lived project files are required:

| File | Purpose |
|---|---|
| `.workflow/WORKFLOW.md` | Stable roles, safety rules, recovery, and loop behavior |
| `.workflow/PROJECT_BRIEF.md` | Active goal, scope, constraints, and acceptance criteria |
| `.workflow/WORKFLOW_STATE.md` | Mode, role bindings, active prompt, and return target |
| `.workflow/STEP_LOG.md` | Append-only transition log with pointer-only paths |

`.workflow/REFERENCE_PLAN.md` is optional. It records a tentative route, decision points, fallbacks, and assumptions without freezing exploration or authorizing execution.

Each task adds only:

- one complete prompt under `.workflow/prompts/review/`;
- one result record under `.workflow/step_records/`;
- the actual task outputs.

There is no mandatory separate summary, status-flags file, handoff package, evidence ledger, or complete-history reread.

## Steps, Retries, And Plan Changes

- `step0`: optional baseline inventory for an existing or complex project;
- `step1`, `step2`: main progression;
- `step2a`, `step2b`: sibling substeps;
- `step2a.1`: deeper substep;
- `step2a.1-r1`: reviewed retry or recovery;
- an optional short suffix may follow the structural ID.

A technical fault may be repaired within the approved prompt budget. A later retry uses a new prompt and ID. When evidence changes the preferred route but preserves the final goal and boundaries, create a new reference-plan version. When the goal or protected boundary changes, create a new project-brief version. Preserve failed results and superseded plans rather than rewriting history.

## Optional Pro Review

Pro Review means a temporary deep-review role with more time for a major decision or independent cold review; it is not a particular model or product. Reviewer may recommend it for a material route, architecture, method, claim, release, high-cost commitment, conflicting evidence, or user-requested cold review.

After user approval, Reviewer creates a small flat packet under `.workflow/pro_reviews/`. Pro returns `PRO_FEEDBACK.md`; the normal Reviewer then discusses adopt, partial adopt, defer, or reject with the user. A `PRO_DRAFT_PROMPT` is advice only and never goes directly to Executor.

## Final Deliverables

User-approved final, publication-facing, release, or handover outputs belong under `deliverables/`:

```text
deliverables/
├─ 001_<primary-deliverable>/
├─ 002_<supporting-deliverable>/
└─ 003_<additional-deliverable>/
```

Keep candidates and temporary outputs elsewhere. Do not renumber existing folders. Use finer subfolders such as `source/`, `figures/`, `tables/`, `assets/`, `exports/`, `packages/`, or `docs/` as appropriate.

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

## License

MIT. See [LICENSE](LICENSE).
