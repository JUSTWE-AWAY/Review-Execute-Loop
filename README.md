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
Executor -> one flat review ZIP -> user -> Web Reviewer
Executor <- review return + approved prompt <- user <- Web Reviewer
```

Each completed step gets one self-contained flat packet under `.workflow/review_packets/`. The Web Reviewer reads only that packet, discusses the decision with the user, and returns `REVIEW_RETURN.md` plus one complete next prompt after approval. The local Executor imports those exact files so the project log retains the external review decision. Both modes use the same prompt and result contracts; only transport changes.

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

The initializer never overwrites an existing `.workflow/` directory, `AGENTS.md`, `incoming/`, or `deliverables/` directory. If the project already has `AGENTS.md`, it leaves it untouched and writes a suggested Codex block under `.workflow/`.

Put prior papers, records, data, models, code, and other supplied starting material under project-root `incoming/`. Its contents are immutable source material: the workflow may inspect and copy them, but never edits, renames, moves, quarantines, or deletes them. Derived work belongs elsewhere.

### Option B: Manual Setup

1. Copy `starter/.workflow/` into the project root.
2. Copy `starter/incoming/` into the project root only when `incoming/` does not already exist.
3. Copy `starter/deliverables/` into the project root only when the project does not already have a final-output directory.
4. Copy `templates/` to `.workflow/templates/`.
5. Choose one file from `profiles/` and copy it to `.workflow/PROFILE.md`.
6. For Codex, adapt `starter/AGENTS.md.example` into project-root `AGENTS.md`; preserve existing project instructions.
7. Give `.workflow/templates/PROJECT_SETUP_START.md` to the first project task.
8. After the brief and Step 0 scope are approved, run `.workflow/templates/STEP0_START.md` in that same task.
9. Give `.workflow/templates/REVIEWER_START.md` to an independent reviewer only after the Step 0 result exists.

For Direct Loop, record both distinct task IDs and their deep links when the platform exposes them. For Manual Relay, task IDs and links may stay `NOT_APPLICABLE`.

## First Project Cycle

1. Place supplied starting materials in `incoming/` and give the first task `PROJECT_SETUP_START.md`.
2. That task is a Setup Facilitator and Executor Candidate. It discusses the brief, optional reference plan, output structure, transport mode, and bounded Step 0 scope; it does not perform substantive work.
3. After explicit user approval, the same candidate runs the fixed `STEP0_START.md` inventory and stops with a result.
4. Open a distinct local Reviewer in Direct mode, or create a flat Web review packet in Manual mode.
5. The independent Reviewer checks Step 0 and discusses corrections with the user. Only accepted review plus user confirmation promotes the candidate to active Executor.
6. After approval, Reviewer writes one complete `EXECUTION_PROMPT.md`. Direct mode dispatches it to the recorded Executor task; Manual mode returns it with `REVIEW_RETURN.md` for exact local import.
7. Executor performs only that prompt, writes one `STEP_RESULT.md`, appends one completion event, and stops.
8. Reviewer checks the result and repeats the cycle only after another user decision.

A truly empty, simple project may skip Step 0 only with explicit user approval and independent setup review. The initial task never reviews or promotes itself.

## Runtime Files

Four files form the human-readable core:

| File | Purpose |
|---|---|
| `.workflow/WORKFLOW.md` | Stable roles, safety rules, recovery, and loop behavior |
| `.workflow/PROJECT_BRIEF.md` | Active goal, scope, constraints, and acceptance criteria |
| `.workflow/WORKFLOW_STATE.md` | Mode, role bindings, active prompt, and return target |
| `.workflow/STEP_LOG.md` | Append-only transition log with pointer-only paths |

`.workflow/REFERENCE_PLAN.md` is optional. It records a tentative route, decision points, fallbacks, and assumptions without freezing exploration or authorizing execution.

`.workflow/INSTALL_MANIFEST.json` records only toolkit-managed file hashes for safe future updates. It does not claim ownership of project files. `incoming/` preserves user-supplied source material, and `deliverables/` holds approved final outputs.

Each task adds only:

- one complete prompt under `.workflow/prompts/review/`;
- one result record under `.workflow/step_records/`;
- the actual task outputs.

Direct mode needs no mandatory handoff package. Manual mode adds one flat review packet per completed step because the external Reviewer cannot read the project directly. There is no mandatory separate status-flags file, evidence ledger, or complete-history reread.

## Steps, Retries, And Plan Changes

- `step0`: fixed setup inventory before Executor promotion;
- `step1`, `step2`: main progression;
- `step2a`, `step2b`: sibling substeps;
- `step2a.1`: deeper substep;
- `step2a.1-r1`: reviewed retry or recovery;
- an optional short suffix may follow the structural ID.

A technical fault may be repaired within the approved prompt budget. A later retry uses a new prompt and ID. When evidence changes the preferred route but preserves the final goal and boundaries, create a new reference-plan version. When the goal or protected boundary changes, create a new project-brief version. Preserve failed results and superseded plans rather than rewriting history.

## Manual Web Review

After a Manual-mode result, create a packet from the project root:

```bash
python /path/to/Review-Execute-Loop/tools/review_packet.py create . --result .workflow/step_records/<step>/STEP_RESULT.md --include <important-project-file>
```

Give the generated ZIP to the Web Reviewer. After discussion and approval, save its two returned files and import them:

```bash
python /path/to/Review-Execute-Loop/tools/review_packet.py import . --packet .workflow/review_packets/<packet-folder> --review-return /path/to/REVIEW_RETURN.md --prompt /path/to/NEXT_EXECUTION_PROMPT.md
```

Attachments must be project-local files and are copied into the flat packet with numbered names. Do not attach entire projects, secrets, or unrelated history.

## Updating An Existing Project

Keep the toolkit clone separate from the project. After pulling a newer release, ask the local Executor to use `WORKFLOW_UPDATE_START.md`, or run:

```bash
python /path/to/Review-Execute-Loop/tools/update_project.py /path/to/project --check
python /path/to/Review-Execute-Loop/tools/update_project.py /path/to/project --prepare
python /path/to/Review-Execute-Loop/tools/update_project.py /path/to/project --apply <approved-upgrade-id>
```

`--check` is read-only. `--prepare` creates an upgrade plan without changing the project. `--apply` installs only unchanged toolkit-managed files and safe additions, backs up replacements, and leaves conflicts untouched. It never overwrites project briefs, plans, logs, prompts, results, review packets, `AGENTS.md`, `incoming/`, `deliverables/`, code, data, or user outputs.

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
