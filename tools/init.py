#!/usr/bin/env python3
"""Initialize Review-Execute Loop in a project without overwriting existing files."""

from __future__ import annotations

import argparse
import os
import shutil
import sys
import tempfile
from pathlib import Path


PROFILES = ("generic", "research", "software", "writing")
MODES = ("direct", "manual")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise RuntimeError(f"Initializer template is missing expected field: {label}")
    return text.replace(old, new, 1)


def initialize(target: Path, profile: str, mode: str, install_agents: bool) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    starter = repo_root / "starter" / ".workflow"
    templates_source = repo_root / "templates"
    profile_source = repo_root / "profiles" / f"{profile}.md"
    agents_source = repo_root / "starter" / "AGENTS.md.example"
    agents_block = repo_root / "adapters" / "codex" / "AGENTS_BLOCK.md"

    for required in (
        starter,
        templates_source,
        profile_source,
        agents_source,
        agents_block,
    ):
        if not required.exists():
            raise FileNotFoundError(f"Distribution file is missing: {required}")

    target = target.expanduser().resolve()
    if target.exists() and not target.is_dir():
        raise NotADirectoryError(f"Project target is not a directory: {target}")
    target.mkdir(parents=True, exist_ok=True)

    workflow_target = target / ".workflow"
    if workflow_target.exists():
        raise FileExistsError(
            f"Refusing to overwrite existing workflow directory: {workflow_target}"
        )

    temporary_root = Path(tempfile.mkdtemp(prefix=".review_execute_init_", dir=target))
    staged_workflow = temporary_root / ".workflow"
    try:
        shutil.copytree(starter, staged_workflow)
        shutil.copytree(templates_source, staged_workflow / "templates")
        shutil.copy2(profile_source, staged_workflow / "PROFILE.md")

        state_path = staged_workflow / "WORKFLOW_STATE.md"
        state = state_path.read_text(encoding="utf-8")
        state = replace_once(
            state,
            "MODE=CHOOSE_DIRECT_OR_MANUAL",
            f"MODE={mode.upper()}",
            "MODE",
        )
        state = replace_once(state, "PROFILE=generic", f"PROFILE={profile}", "PROFILE")
        if mode == "manual":
            state = state.replace(
                "EXECUTOR_TASK_ID=PENDING_OR_NOT_APPLICABLE",
                "EXECUTOR_TASK_ID=NOT_APPLICABLE",
            )
            state = state.replace(
                "REVIEWER_TASK_ID=PENDING_OR_NOT_APPLICABLE",
                "REVIEWER_TASK_ID=NOT_APPLICABLE",
            )
            state = state.replace(
                "RETURN_TARGET_TASK_ID=PENDING_OR_NOT_APPLICABLE",
                "RETURN_TARGET_TASK_ID=MANUAL",
            )
        else:
            state = state.replace(
                "PENDING_OR_NOT_APPLICABLE", "PENDING_ID_CAPTURE"
            )
        state_path.write_text(state, encoding="utf-8")

        brief_path = staged_workflow / "PROJECT_BRIEF.md"
        brief = brief_path.read_text(encoding="utf-8")
        brief = replace_once(
            brief, "Profile: `generic`", f"Profile: `{profile}`", "brief profile"
        )
        brief_path.write_text(brief, encoding="utf-8")

        os.replace(staged_workflow, workflow_target)
    finally:
        shutil.rmtree(temporary_root, ignore_errors=True)

    agents_message = "AGENTS adapter not requested."
    if install_agents:
        agents_target = target / "AGENTS.md"
        if agents_target.exists():
            snippet = workflow_target / "CODEX_AGENTS_SNIPPET.md"
            shutil.copy2(agents_block, snippet)
            agents_message = (
                "Existing AGENTS.md preserved. Review and merge "
                f"the suggested block from {snippet}."
            )
        else:
            shutil.copy2(agents_source, agents_target)
            agents_message = f"Created {agents_target}."

    print(f"Initialized Review-Execute Loop in: {target}")
    print(f"Mode: {mode.upper()} | Profile: {profile}")
    print(agents_message)
    print("Next:")
    print("1. Give .workflow/templates/PROJECT_SETUP_START.md to the first project window")
    print("2. Complete and approve .workflow/PROJECT_BRIEF.md")
    print("3. Complete role bindings in .workflow/WORKFLOW_STATE.md")
    print("4. Give .workflow/templates/EXECUTOR_START.md to the Executor")
    print("5. Give .workflow/templates/REVIEWER_START.md to the independent Reviewer")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", type=Path, help="Project directory to initialize")
    parser.add_argument("--profile", choices=PROFILES, default="generic")
    parser.add_argument("--mode", choices=MODES, default="manual")
    parser.add_argument(
        "--no-agents",
        action="store_true",
        help="Do not create AGENTS.md or a Codex merge snippet",
    )
    args = parser.parse_args()

    try:
        initialize(args.target, args.profile, args.mode, not args.no_agents)
    except (FileExistsError, FileNotFoundError, NotADirectoryError, OSError, RuntimeError) as error:
        print(f"INITIALIZATION_FAILED: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
