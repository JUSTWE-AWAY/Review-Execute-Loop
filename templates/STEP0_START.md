# Step 0 Start Prompt

You are the Executor Candidate performing the fixed setup inventory. This is not authorization for substantive implementation, experimentation, rewriting, publication, deployment, or cleanup.

```text
SCHEMA=review-execute-loop/0.3
STEP_ID=step0
STEP_KIND=INVENTORY
PARENT_STEP_ID=NONE
BASELINE_STEP_ID=setup
EXECUTOR_STATUS=CANDIDATE
USER_APPROVAL=<reference-approving-step0>
RESULT_PATH=.workflow/step_records/step0_<timestamp>/STEP_RESULT.md
```

## Required Inputs

- `.workflow/WORKFLOW.md`
- `.workflow/WORKFLOW_STATE.md`
- `.workflow/PROJECT_BRIEF.md`
- active optional `.workflow/REFERENCE_PLAN.md`
- `.workflow/PROFILE.md`
- project-root `incoming/`
- existing project files explicitly approved for inventory

## Immutable Incoming Rule

Everything under `incoming/` is read-only user source material. Do not edit, rename, move, overwrite, quarantine, or delete it. Do not run untrusted executable content from `incoming/`. Derived inventories, hashes, extracted text, converted files, cleaned data, and analysis must be written under the Step 0 result directory or another explicitly approved derived-work path.

## Step 0 Work

1. Inventory supplied materials and relevant existing project structure.
2. Identify file types, apparent versions, duplicates, missing dependencies, large or unreadable items, and protected/sensitive material without exposing secrets.
3. Record what can and cannot currently be opened or validated.
4. Compare observed materials with the approved brief and optional reference plan.
5. List factual gaps, route assumptions that need revision, and decisions for independent review.
6. Propose, but do not execute, the smallest sensible `step1` scope.

## Required Outputs

- `STEP_RESULT.md`
- `MATERIALS_INVENTORY.md`
- optional machine-readable inventory such as `MATERIALS_INVENTORY.csv`
- one `STEP0_COMPLETED` log event
- in Manual mode, one flat review packet and zip using the Web review templates
- in Direct mode, one concise receipt containing the result path, key files, candidate task ID/link, and intended Reviewer return target

## Stop

Stop after packaging Step 0 for independent review. Keep `EXECUTOR_STATUS=CANDIDATE`. Do not generate `step1`, edit incoming materials, or promote yourself to active Executor.
