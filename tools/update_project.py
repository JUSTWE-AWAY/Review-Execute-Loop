#!/usr/bin/env python3
"""Safely check, prepare, or apply a Review-Execute Loop project upgrade."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from workflow_manifest import (
    build_manifest,
    load_json,
    managed_sources,
    sha256_file,
    toolkit_version,
    utc_now,
    workflow_schema,
    write_manifest,
)


def stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def parse_state(path: Path) -> dict[str, str]:
    return {
        key: value.strip()
        for key, value in re.findall(
            r"^([A-Z][A-Z0-9_]*)=(.*)$", read_text(path), re.MULTILINE
        )
    }


def detect_schema(project: Path) -> str:
    text = read_text(project / ".workflow" / "WORKFLOW.md")
    match = re.search(r"review-execute-loop/(0\.[0-9]+)", text)
    return match.group(1) if match else "unknown"


def require_project(project: Path) -> Path:
    project = project.expanduser().resolve()
    if not (project / ".workflow" / "WORKFLOW.md").is_file():
        raise FileNotFoundError(f"Not an initialized project: {project}")
    return project


def legacy_version_for_schema(schema: str) -> str:
    return {"0.1": "0.1.1", "0.2": "0.2.0", "0.3": "0.3.1"}.get(
        schema, "unknown"
    )


def load_baseline(
    repo: Path, project: Path, profile: str
) -> tuple[str, dict[str, object]]:
    installed = project / ".workflow" / "INSTALL_MANIFEST.json"
    if installed.is_file():
        manifest = load_json(installed)
        return str(manifest.get("toolkit_version", "unknown")), manifest
    schema = detect_schema(project)
    version = legacy_version_for_schema(schema)
    baseline_path = repo / "manifests" / "releases" / f"v{version}.json"
    if baseline_path.is_file():
        baseline = load_json(baseline_path)
        profile_hashes = baseline.get("profile_hashes", {})
        managed = baseline.get("managed_files", {})
        if isinstance(profile_hashes, dict) and isinstance(managed, dict):
            profile_entry = profile_hashes.get(profile)
            if isinstance(profile_entry, dict):
                managed[".workflow/PROFILE.md"] = profile_entry
        return version, baseline
    return version, {
        "toolkit_version": version,
        "workflow_schema": schema,
        "managed_files": {},
    }


def compare(repo: Path, project: Path) -> dict[str, object]:
    state = parse_state(project / ".workflow" / "WORKFLOW_STATE.md")
    profile = state.get("PROFILE", "generic")
    old_version, baseline = load_baseline(repo, project, profile)
    baseline_files = baseline.get("managed_files", {})
    if not isinstance(baseline_files, dict):
        baseline_files = {}
    actions: list[dict[str, str]] = []
    for destination, source in managed_sources(repo, profile).items():
        local = project / Path(destination)
        new_hash = sha256_file(source)
        local_hash = sha256_file(local) if local.is_file() else "MISSING"
        baseline_entry = baseline_files.get(destination, {})
        expected_hash = (
            str(baseline_entry.get("sha256", "UNKNOWN"))
            if isinstance(baseline_entry, dict)
            else "UNKNOWN"
        )
        if not local.exists():
            action = "SAFE_ADD"
        elif local_hash == new_hash:
            action = "ALREADY_CURRENT"
        elif expected_hash != "UNKNOWN" and local_hash == expected_hash:
            action = "SAFE_REPLACE"
        else:
            action = "CONFLICT"
        actions.append(
            {
                "action": action,
                "destination": destination,
                "source": source.relative_to(repo).as_posix(),
                "local_sha256": local_hash,
                "expected_old_sha256": expected_hash,
                "new_sha256": new_hash,
            }
        )
    return {
        "format": 1,
        "project": str(project),
        "source_toolkit": str(repo),
        "from_version": old_version,
        "from_schema": detect_schema(project),
        "to_version": toolkit_version(repo),
        "to_schema": workflow_schema(repo),
        "profile": profile,
        "created_at_utc": utc_now(),
        "actions": actions,
    }


def summary(plan: dict[str, object]) -> Counter[str]:
    actions = plan.get("actions", [])
    return Counter(
        str(item.get("action", "UNKNOWN"))
        for item in actions
        if isinstance(item, dict)
    )


def print_summary(plan: dict[str, object]) -> None:
    counts = summary(plan)
    print(f"FROM_VERSION={plan['from_version']}")
    print(f"TO_VERSION={plan['to_version']}")
    for action in ("SAFE_ADD", "SAFE_REPLACE", "ALREADY_CURRENT", "CONFLICT"):
        print(f"{action}={counts[action]}")
    for item in plan["actions"]:
        if item["action"] != "ALREADY_CURRENT":
            print(f"{item['action']} {item['destination']}")


def prepare(repo: Path, project: Path) -> int:
    plan = compare(repo, project)
    upgrade_id = (
        f"UPGRADE_{plan['from_version']}_TO_{plan['to_version']}_{stamp()}"
        .replace("/", "-")
        .replace(" ", "-")
    )
    upgrade_dir = project / ".workflow" / "upgrades" / upgrade_id
    incoming = upgrade_dir / "incoming"
    incoming.mkdir(parents=True)
    for item in plan["actions"]:
        if item["action"] == "ALREADY_CURRENT":
            continue
        source = repo / Path(item["source"])
        destination = incoming / Path(item["destination"])
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    plan["upgrade_id"] = upgrade_id
    plan["status"] = "PREPARED"
    (upgrade_dir / "plan.json").write_text(
        json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    counts = summary(plan)
    rows = "\n".join(
        f"| `{item['destination']}` | {item['action']} |"
        for item in plan["actions"]
        if item["action"] != "ALREADY_CURRENT"
    ) or "| None | ALREADY_CURRENT |"
    report = f"""# Workflow Upgrade Plan

- Upgrade ID: `{upgrade_id}`
- From: `{plan['from_version']}` / schema `{plan['from_schema']}`
- To: `{plan['to_version']}` / schema `{plan['to_schema']}`
- Safe additions: {counts['SAFE_ADD']}
- Safe replacements: {counts['SAFE_REPLACE']}
- Already current: {counts['ALREADY_CURRENT']}
- Conflicts requiring review: {counts['CONFLICT']}

No project-owned file has been changed. `--apply` will install only `SAFE_ADD` and `SAFE_REPLACE` items, back up replacements, add missing structured state fields, and leave every conflict untouched.

| Managed path | Classification |
|---|---|
{rows}

Project briefs, plans, logs, prompts, results, review packets, Pro packets, `AGENTS.md`, `incoming/`, `deliverables/`, code, and data are not overwritten.
"""
    (upgrade_dir / "00_UPGRADE_PLAN.md").write_text(report, encoding="utf-8")
    print_summary(plan)
    print(f"UPGRADE_ID={upgrade_id}")
    print(f"UPGRADE_PLAN={upgrade_dir / '00_UPGRADE_PLAN.md'}")
    return 0


def update_state_fields(path: Path, target_version: str, target_schema: str) -> None:
    text = read_text(path)
    text = re.sub(
        r"Schema: `review-execute-loop/0\.[0-9]+`",
        f"Schema: `review-execute-loop/{target_schema}`",
        text,
        count=1,
    )
    fields = parse_state(path)
    mode = fields.get("MODE", "MANUAL")
    current_step = fields.get("CURRENT_STEP_ID", "setup")
    latest_result = fields.get("LATEST_RESULT_PATH", "NONE")
    link_default = "NOT_APPLICABLE" if mode == "MANUAL" else "PENDING_ID_CAPTURE"
    executor_status = (
        "CANDIDATE" if current_step == "setup" and latest_result == "NONE" else "ACTIVE"
    )
    additions = {
        "TOOLKIT_VERSION": target_version,
        "EXECUTOR_TASK_LINK": link_default,
        "EXECUTOR_STATUS": executor_status,
        "REVIEWER_TASK_LINK": link_default,
        "RETURN_TARGET_TASK_LINK": "MANUAL" if mode == "MANUAL" else link_default,
        "ACTIVE_REVIEW_PACKET_ID": "NONE",
        "ACTIVE_REVIEW_PACKET_PATH": "NONE",
    }
    lines = text.splitlines()
    output: list[str] = []
    remaining = dict(additions)
    for line in lines:
        match = re.match(r"^([A-Z][A-Z0-9_]*)=(.*)$", line.strip())
        if match and match.group(1) == "TOOLKIT_VERSION":
            output.append(f"TOOLKIT_VERSION={target_version}")
            remaining.pop("TOOLKIT_VERSION", None)
        else:
            output.append(line)
            if match:
                remaining.pop(match.group(1), None)
    if remaining:
        closing = next((i for i, line in enumerate(output) if line.strip() == "```" and i > 4), None)
        if closing is None:
            raise RuntimeError("Cannot locate WORKFLOW_STATE field block")
        output[closing:closing] = [f"{key}={value}" for key, value in remaining.items()] + [""]
    path.write_text("\n".join(output) + "\n", encoding="utf-8")


def append_update_event(project: Path, status: str, upgrade_id: str, result_path: str) -> None:
    log = project / ".workflow" / "STEP_LOG.md"
    block = f"""

### {utc_now()} | WORKFLOW_UPDATE_APPLIED | maintenance
PROMPT_ID=NONE
ROLE=EXECUTOR
SOURCE_ROLE=LOCAL_EXECUTOR
STATUS={status}
ONE_LINE_RESULT=Applied workflow upgrade {upgrade_id}
RESULT_PATH={result_path}
PROMPT_PATH=NONE
KEY_FILES=.workflow/INSTALL_MANIFEST.json
TARGET=NONE
RETURN_TARGET=NONE
USER_APPROVAL=RECORDED_BY_UPDATE_PROMPT
SUPERSEDES=NONE
PRO_REVIEW_ID=NONE
REVIEW_PACKET_ID=NONE
"""
    with log.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(block)


def apply_upgrade(repo: Path, project: Path, upgrade_id: str) -> int:
    upgrades_root = (project / ".workflow" / "upgrades").resolve()
    upgrade_dir = (upgrades_root / upgrade_id).resolve()
    try:
        upgrade_dir.relative_to(upgrades_root)
    except ValueError as error:
        raise ValueError("Invalid upgrade ID") from error
    plan_path = upgrade_dir / "plan.json"
    if not plan_path.is_file():
        raise FileNotFoundError(f"Prepared upgrade does not exist: {upgrade_id}")
    plan = load_json(plan_path)
    if plan.get("status") == "APPLIED":
        raise ValueError(f"Upgrade is already applied: {upgrade_id}")
    if str(plan.get("to_version")) != toolkit_version(repo):
        raise ValueError("Prepared upgrade target does not match this toolkit version")

    applied: list[str] = []
    skipped_conflicts: list[str] = []
    runtime_conflicts: list[str] = []
    for item in plan.get("actions", []):
        if not isinstance(item, dict):
            continue
        action = str(item.get("action"))
        destination_text = str(item.get("destination"))
        destination = project / Path(destination_text)
        staged = upgrade_dir / "incoming" / Path(destination_text)
        if action == "CONFLICT":
            skipped_conflicts.append(destination_text)
            continue
        if action == "ALREADY_CURRENT":
            continue
        if not staged.is_file() or sha256_file(staged) != item.get("new_sha256"):
            runtime_conflicts.append(destination_text)
            continue
        if action == "SAFE_ADD" and destination.exists():
            runtime_conflicts.append(destination_text)
            continue
        if action == "SAFE_REPLACE":
            expected = str(item.get("local_sha256"))
            if not destination.is_file() or sha256_file(destination) != expected:
                runtime_conflicts.append(destination_text)
                continue
            backup = upgrade_dir / "backup" / Path(destination_text)
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(destination, backup)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(staged, destination)
        applied.append(destination_text)

    current_workflow = project / ".workflow" / "WORKFLOW.md"
    source_workflow = repo / "starter" / ".workflow" / "WORKFLOW.md"
    core_current = (
        current_workflow.is_file()
        and sha256_file(current_workflow) == sha256_file(source_workflow)
    )
    if core_current:
        update_state_fields(
            project / ".workflow" / "WORKFLOW_STATE.md",
            str(plan["to_version"]),
            str(plan["to_schema"]),
        )
        reference_plan = project / ".workflow" / "REFERENCE_PLAN.md"
        if not reference_plan.exists():
            shutil.copy2(repo / "starter" / ".workflow" / "REFERENCE_PLAN.md", reference_plan)
        for root_name in ("incoming", "deliverables"):
            destination = project / root_name
            if not destination.exists():
                shutil.copytree(repo / "starter" / root_name, destination)

    conflicts = sorted(set(skipped_conflicts + runtime_conflicts))
    manifest = build_manifest(repo, project, str(plan.get("profile", "generic")))
    managed = manifest.get("managed_files", {})
    if isinstance(managed, dict):
        for destination in list(managed):
            source = managed_sources(repo, str(plan.get("profile", "generic"))).get(destination)
            local = project / Path(destination)
            if source is None or not local.is_file() or sha256_file(local) != sha256_file(source):
                managed.pop(destination, None)
    manifest["unresolved_conflicts"] = conflicts
    manifest["upgrade_status"] = "PARTIAL" if conflicts or not core_current else "COMPLETE"
    manifest["upgraded_at_utc"] = utc_now()
    write_manifest(project / ".workflow" / "INSTALL_MANIFEST.json", manifest)

    validation = subprocess.run(
        [sys.executable, str(repo / "tools" / "validate.py"), "--project", str(project)],
        cwd=repo,
        text=True,
        capture_output=True,
        check=False,
    )
    status = "PARTIAL" if conflicts or validation.returncode != 0 or not core_current else "COMPLETED"
    result_path = upgrade_dir / "UPGRADE_RESULT.md"
    result = f"""# Workflow Upgrade Result

- Upgrade ID: `{upgrade_id}`
- Status: `{status}`
- Applied managed files: {len(applied)}
- Unresolved conflicts: {len(conflicts)}
- Core workflow current: {'YES' if core_current else 'NO'}
- Project validation return code: {validation.returncode}

## Applied

{chr(10).join(f'- `{path}`' for path in applied) if applied else '- NONE'}

## Unresolved Conflicts

{chr(10).join(f'- `{path}`' for path in conflicts) if conflicts else '- NONE'}

## Validation

```text
{validation.stdout}{validation.stderr}
```

Conflicts were not overwritten. Backups of replaced managed files are under `backup/`. Project-owned files were not replaced.
"""
    result_path.write_text(result, encoding="utf-8")
    plan["status"] = "APPLIED"
    plan["applied_at_utc"] = utc_now()
    plan["result"] = result_path.name
    plan_path.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    append_update_event(
        project,
        status,
        upgrade_id,
        result_path.relative_to(project).as_posix(),
    )
    print(f"UPGRADE_STATUS={status}")
    print(f"UPGRADE_RESULT={result_path}")
    return 0 if status == "COMPLETED" else 2


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--prepare", action="store_true")
    mode.add_argument("--apply", metavar="UPGRADE_ID")
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    try:
        project = require_project(args.project)
        if args.check:
            print_summary(compare(repo, project))
            return 0
        if args.prepare:
            return prepare(repo, project)
        return apply_upgrade(repo, project, args.apply)
    except (FileExistsError, FileNotFoundError, OSError, RuntimeError, ValueError) as error:
        print(f"WORKFLOW_UPDATE_FAILED: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
