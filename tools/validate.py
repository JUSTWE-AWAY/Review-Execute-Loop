#!/usr/bin/env python3
"""Read-only validation for the toolkit distribution or an initialized project."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path


DISTRIBUTION_FILES = (
    "README.md",
    "README.zh-CN.md",
    "LICENSE",
    "VERSION",
    "starter/.workflow/WORKFLOW.md",
    "starter/.workflow/PROJECT_BRIEF.md",
    "starter/.workflow/REFERENCE_PLAN.md",
    "starter/.workflow/WORKFLOW_STATE.md",
    "starter/.workflow/STEP_LOG.md",
    "starter/incoming/README.md",
    "starter/deliverables/README.md",
    "starter/AGENTS.md.example",
    "templates/REVIEWER_START.md",
    "templates/EXECUTOR_START.md",
    "templates/PROJECT_SETUP_START.md",
    "templates/STEP0_START.md",
    "templates/WEB_REVIEW_PACKET.md",
    "templates/WEB_REVIEW_RETURN.md",
    "templates/WORKFLOW_UPDATE_START.md",
    "templates/PRO_REVIEW_PACKET.md",
    "templates/PRO_FEEDBACK_TEMPLATE.md",
    "templates/EXECUTION_PROMPT.md",
    "templates/STEP_RESULT.md",
    "profiles/generic.md",
    "profiles/research.md",
    "profiles/software.md",
    "profiles/writing.md",
    "adapters/codex/AGENTS_BLOCK.md",
    "adapters/codex/DIRECT_LOOP_SETUP.md",
    "adapters/manual-web/MANUAL_RELAY_SETUP.md",
    "adapters/generic/SYSTEM_PROMPT.md",
    "examples/research-example/README.md",
    "examples/software-example/README.md",
    "tools/init.py",
    "tools/review_packet.py",
    "tools/update_project.py",
    "tools/validate.py",
    "tools/workflow_manifest.py",
    "tools/generate_release_manifest.py",
    "manifests/releases/v0.1.1.json",
    "manifests/releases/v0.2.0.json",
    "manifests/releases/v0.3.0.json",
    "manifests/releases/v0.3.1.json",
)

PROJECT_FILES_BASE = (
    ".workflow/WORKFLOW.md",
    ".workflow/PROJECT_BRIEF.md",
    ".workflow/WORKFLOW_STATE.md",
    ".workflow/STEP_LOG.md",
    ".workflow/PROFILE.md",
    ".workflow/templates/REVIEWER_START.md",
    ".workflow/templates/EXECUTOR_START.md",
    ".workflow/templates/PROJECT_SETUP_START.md",
    ".workflow/templates/EXECUTION_PROMPT.md",
    ".workflow/templates/STEP_RESULT.md",
)

PROJECT_FILES_V02 = (
    ".workflow/REFERENCE_PLAN.md",
    ".workflow/templates/PRO_REVIEW_PACKET.md",
    ".workflow/templates/PRO_FEEDBACK_TEMPLATE.md",
)

PROJECT_FILES_V03 = PROJECT_FILES_V02 + (
    ".workflow/templates/STEP0_START.md",
    ".workflow/templates/WEB_REVIEW_PACKET.md",
    ".workflow/templates/WEB_REVIEW_RETURN.md",
    ".workflow/templates/WORKFLOW_UPDATE_START.md",
)

PRIVATE_PATH_PATTERNS = (
    re.compile(r"\b[A-Za-z]:[\\/](?:Users|Documents and Settings)[\\/](?!<|your)[^\\/\s]+", re.IGNORECASE),
    re.compile(r"(?<![\w<])/home/(?!<|your)[^/\s]+", re.IGNORECASE),
)

LINK_PATTERN = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


def markdown_files(root: Path):
    yield from root.rglob("*.md")


def configured_private_markers() -> tuple[str, ...]:
    """Load optional local-only markers without publishing private literals."""
    raw = os.environ.get("REVIEW_EXECUTE_PRIVATE_MARKERS", "")
    return tuple(marker.strip() for marker in raw.split(",") if marker.strip())


def parse_state(path: Path) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        match = re.match(r"^([A-Z][A-Z0-9_]*)=(.*)$", line.strip())
        if match:
            fields[match.group(1)] = match.group(2).strip()
    return fields


def validate_links(root: Path) -> list[str]:
    issues: list[str] = []
    for source in markdown_files(root):
        text = source.read_text(encoding="utf-8-sig")
        for raw_target in LINK_PATTERN.findall(text):
            target = raw_target.strip().strip("<>").split("#", 1)[0]
            if not target or "://" in target or target.startswith("mailto:"):
                continue
            resolved = (source.parent / target).resolve()
            if not resolved.exists():
                issues.append(
                    f"broken local link: {source.relative_to(root)} -> {raw_target}"
                )
    return issues


def validate_distribution(root: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    for relative in DISTRIBUTION_FILES:
        if not (root / relative).is_file():
            errors.append(f"missing distribution file: {relative}")

    if errors:
        return errors, warnings

    version = (root / "VERSION").read_text(encoding="utf-8-sig").strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        errors.append(f"VERSION is not semantic version text: {version!r}")

    required_tokens = {
        "starter/.workflow/WORKFLOW.md": (
            "### Setup Facilitator / Executor Candidate",
            "### Reviewer / Orchestrator",
            "### Executor",
            "### Pro Reviewer / Deep Reviewer (Optional)",
            "### DIRECT",
            "### MANUAL",
            "## Reading And Recovery",
            "## File Safety",
            "## Optional Pro Review",
            "## External Web Review Packets",
            "## Final Deliverables",
        ),
        "templates/EXECUTION_PROMPT.md": (
            "PROMPT_ID=",
            "STEP_KIND=",
            "PARENT_STEP_ID=",
            "PRO_REVIEW_SOURCE=",
            "DELIVERABLE_TARGET=",
            "RETURN_TARGET=",
            "## Acceptance Checks",
            "## Early Stop",
        ),
        "templates/STEP_RESULT.md": (
            "STATUS=<COMPLETED-or-PARTIAL-or-BLOCKED>",
            "## Checks",
            "## Completion Receipt",
        ),
        "templates/PROJECT_SETUP_START.md": (
            "Executor Candidate",
            "Do not begin substantive project work",
            "SETUP_CONFIRMED",
        ),
        "templates/STEP0_START.md": (
            "STEP_ID=step0",
            "EXECUTOR_STATUS=CANDIDATE",
            "incoming/",
        ),
        "templates/WEB_REVIEW_PACKET.md": (
            "REVIEW_PACKET_ID=",
            "You are the independent Reviewer / Orchestrator",
            "NEXT_EXECUTION_PROMPT",
        ),
        "templates/WEB_REVIEW_RETURN.md": (
            "REVIEW_PACKET_ID=",
            "NEXT_PROMPT_APPROVED=",
            "EXECUTOR_PROMOTION=",
        ),
        "templates/WORKFLOW_UPDATE_START.md": (
            "--check",
            "--prepare",
            "--apply",
            "Never overwrite",
        ),
        "templates/PRO_REVIEW_PACKET.md": (
            "PRO_REVIEW_ID=",
            "REVIEW_KIND=",
            "PRO_DRAFT_PROMPT",
        ),
        "templates/PRO_FEEDBACK_TEMPLATE.md": (
            "PRO_REVIEW_ID=",
            "## Final Recommendation",
            "PRO_DRAFT_PROMPT",
        ),
    }
    for relative, tokens in required_tokens.items():
        text = (root / relative).read_text(encoding="utf-8-sig")
        for token in tokens:
            if token not in text:
                errors.append(f"missing required token in {relative}: {token}")

    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {
            ".md",
            ".txt",
            ".py",
            ".yml",
            ".yaml",
        }:
            continue
        # The validator contains its own generic path-detection patterns.
        if path.resolve() == Path(__file__).resolve():
            continue
        text = path.read_text(encoding="utf-8-sig")
        for pattern in PRIVATE_PATH_PATTERNS:
            if pattern.search(text):
                errors.append(
                    f"private user path in {path.relative_to(root)}"
                )
        for marker in configured_private_markers():
            if marker.lower() in text.lower():
                errors.append(
                    f"configured private marker in {path.relative_to(root)}"
                )

    for relative in (
        "manifests/releases/v0.1.1.json",
        "manifests/releases/v0.2.0.json",
        "manifests/releases/v0.3.0.json",
        "manifests/releases/v0.3.1.json",
    ):
        try:
            manifest = json.loads((root / relative).read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError) as error:
            errors.append(f"invalid release manifest {relative}: {error}")
            continue
        if not isinstance(manifest.get("managed_files"), dict):
            errors.append(f"release manifest has no managed_files map: {relative}")

    errors.extend(validate_links(root))
    return errors, warnings


def validate_project(root: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    for relative in PROJECT_FILES_BASE:
        if not (root / relative).is_file():
            errors.append(f"missing project workflow file: {relative}")
    if errors:
        return errors, warnings

    workflow_text = (root / ".workflow" / "WORKFLOW.md").read_text(
        encoding="utf-8-sig"
    )
    schema_match = re.search(r"review-execute-loop/(0\.[0-9]+)", workflow_text)
    schema = schema_match.group(1) if schema_match else ""
    if schema == "0.2":
        for relative in PROJECT_FILES_V02:
            if not (root / relative).is_file():
                errors.append(f"missing v0.2 project workflow file: {relative}")
        if not (root / "deliverables").is_dir():
            warnings.append("v0.2 project has no deliverables directory")
    elif schema == "0.3":
        for relative in PROJECT_FILES_V03:
            if not (root / relative).is_file():
                errors.append(f"missing v0.3 project workflow file: {relative}")
        if not (root / "deliverables").is_dir():
            warnings.append("v0.3 project has no deliverables directory")
        if not (root / "incoming").is_dir():
            warnings.append("v0.3 project has no protected incoming directory")
        if not (root / ".workflow" / "INSTALL_MANIFEST.json").is_file():
            warnings.append(
                "v0.3 project has no install manifest; upgrades will use the release baseline"
            )
    elif schema == "0.1":
        warnings.append("project uses legacy workflow schema 0.1")
    elif schema != "0.1":
        errors.append(f"unsupported or missing workflow schema: {schema or 'MISSING'}")
    if errors:
        return errors, warnings

    state = parse_state(root / ".workflow" / "WORKFLOW_STATE.md")
    mode = state.get("MODE", "")
    phase = state.get("PHASE", "")
    if mode not in {"DIRECT", "MANUAL"}:
        errors.append(f"MODE must be DIRECT or MANUAL, found: {mode or 'MISSING'}")

    required_state = (
        "ACTIVE_BRIEF_ID",
        "ACTIVE_BRIEF_PATH",
        "CURRENT_STEP_ID",
        "ACTIVE_PROMPT_ID",
    )
    if schema == "0.2":
        required_state += (
            "ACTIVE_REFERENCE_PLAN_ID",
            "ACTIVE_REFERENCE_PLAN_PATH",
            "DELIVERABLES_ROOT",
            "ACTIVE_PRO_REVIEW_ID",
            "ACTIVE_PRO_REVIEW_PATH",
        )
    elif schema == "0.3":
        required_state += (
            "TOOLKIT_VERSION",
            "ACTIVE_REFERENCE_PLAN_ID",
            "ACTIVE_REFERENCE_PLAN_PATH",
            "DELIVERABLES_ROOT",
            "EXECUTOR_TASK_LINK",
            "EXECUTOR_STATUS",
            "REVIEWER_TASK_LINK",
            "RETURN_TARGET_TASK_LINK",
            "ACTIVE_PROMPT_PATH",
            "ACTIVE_REVIEW_PACKET_ID",
            "ACTIVE_REVIEW_PACKET_PATH",
            "ACTIVE_PRO_REVIEW_ID",
            "ACTIVE_PRO_REVIEW_PATH",
        )
    for key in required_state:
        if not state.get(key):
            errors.append(f"missing state field: {key}")

    if mode == "DIRECT":
        executor = state.get("EXECUTOR_TASK_ID", "")
        reviewer = state.get("REVIEWER_TASK_ID", "")
        return_target = state.get("RETURN_TARGET_TASK_ID", "")
        executor_link = state.get("EXECUTOR_TASK_LINK", "")
        reviewer_link = state.get("REVIEWER_TASK_LINK", "")
        pending = any("PENDING" in value or not value for value in (executor, reviewer, return_target))
        if pending:
            message = "DIRECT mode role IDs are not fully bound"
            if phase in {"SETUP", "WAITING_FOR_REVIEWER_BINDING"}:
                warnings.append(message + "; complete binding before routine dispatch")
            else:
                errors.append(message)
        elif executor == reviewer:
            errors.append("DIRECT mode Executor and Reviewer IDs must differ")
        elif return_target != reviewer:
            warnings.append("RETURN_TARGET_TASK_ID normally equals REVIEWER_TASK_ID")
        if schema == "0.3" and phase not in {"SETUP", "WAITING_FOR_REVIEWER_BINDING"}:
            if not executor_link or "PENDING" in executor_link:
                warnings.append("DIRECT mode Executor deep link is not recorded")
            if not reviewer_link or "PENDING" in reviewer_link:
                warnings.append("DIRECT mode Reviewer deep link is not recorded")

    if schema == "0.3":
        executor_status = state.get("EXECUTOR_STATUS", "")
        if executor_status not in {"CANDIDATE", "ACTIVE", "PAUSED", "CLOSED"}:
            errors.append(
                "EXECUTOR_STATUS must be CANDIDATE, ACTIVE, PAUSED, or CLOSED"
            )
        install_manifest = root / ".workflow" / "INSTALL_MANIFEST.json"
        if install_manifest.is_file():
            try:
                manifest = json.loads(install_manifest.read_text(encoding="utf-8-sig"))
            except (OSError, json.JSONDecodeError) as error:
                errors.append(f"invalid INSTALL_MANIFEST.json: {error}")
            else:
                if manifest.get("workflow_schema") != "0.3":
                    warnings.append("install manifest does not identify workflow schema 0.3")

    brief_text = (root / ".workflow" / "PROJECT_BRIEF.md").read_text(
        encoding="utf-8-sig"
    )
    if "Status: `DRAFT`" in brief_text or "Last approved by user: `NOT_APPROVED`" in brief_text:
        warnings.append("project brief is still draft/unapproved")

    step_id = state.get("CURRENT_STEP_ID", "")
    if step_id not in {"setup", "NONE"} and not re.fullmatch(
        r"step(?:0|[1-9][0-9]*)(?:[a-z])?(?:\.[1-9][0-9]*)?(?:-r[1-9][0-9]*)?(?:-[a-z0-9]+(?:-[a-z0-9]+)*)?",
        step_id,
    ):
        warnings.append(f"CURRENT_STEP_ID does not follow the recommended convention: {step_id}")
    return errors, warnings


def report(errors: list[str], warnings: list[str]) -> int:
    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"VALIDATION_FAILED: {len(errors)} error(s), {len(warnings)} warning(s)")
        return 1
    print(f"VALIDATION_PASSED: 0 errors, {len(warnings)} warning(s)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--distribution", type=Path, help="Toolkit repository root")
    group.add_argument("--project", type=Path, help="Initialized project root")
    args = parser.parse_args()

    root = (args.distribution or args.project).expanduser().resolve()
    if not root.is_dir():
        print(f"ERROR: directory does not exist: {root}")
        return 1
    if args.distribution:
        return report(*validate_distribution(root))
    return report(*validate_project(root))


if __name__ == "__main__":
    raise SystemExit(main())
