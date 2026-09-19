#!/usr/bin/env python3
"""Create or import flat Manual/Web review packets for a project."""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


FIELD_PATTERN = re.compile(r"^([A-Z][A-Z0-9_]*)=(.*)$", re.MULTILINE)


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_fields(text: str) -> dict[str, str]:
    return {key: value.strip() for key, value in FIELD_PATTERN.findall(text)}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def safe_name(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-.")
    return cleaned or "item"


def require_project(project: Path) -> Path:
    project = project.expanduser().resolve()
    required = project / ".workflow" / "WORKFLOW_STATE.md"
    if not required.is_file():
        raise FileNotFoundError(f"Not an initialized project: {project}")
    return project


def ensure_inside(path: Path, root: Path) -> Path:
    expanded = path.expanduser()
    resolved = (root / expanded).resolve() if not expanded.is_absolute() else expanded.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as error:
        raise ValueError(f"Attachment must be inside the project: {resolved}") from error
    return resolved


def update_state(path: Path, updates: dict[str, str]) -> None:
    text = read_text(path)
    remaining = dict(updates)
    lines = text.splitlines()
    output: list[str] = []
    for line in lines:
        match = re.match(r"^([A-Z][A-Z0-9_]*)=(.*)$", line.strip())
        if match and match.group(1) in remaining:
            key = match.group(1)
            output.append(f"{key}={remaining.pop(key)}")
        else:
            output.append(line)
    if remaining:
        closing = next((index for index, line in enumerate(output) if line.strip() == "```" and index > 4), None)
        if closing is None:
            raise RuntimeError(f"Cannot locate state field block in {path}")
        output[closing:closing] = [f"{key}={value}" for key, value in remaining.items()] + [""]
    path.write_text("\n".join(output) + "\n", encoding="utf-8")


def append_event(
    project: Path,
    event: str,
    step_id: str,
    prompt_id: str,
    status: str,
    result: str,
    result_path: str = "NONE",
    prompt_path: str = "NONE",
    key_files: str = "NONE",
    review_packet_id: str = "NONE",
    approval: str = "NONE",
) -> None:
    log = project / ".workflow" / "STEP_LOG.md"
    block = f"""

### {utc_iso()} | {event} | {step_id}
PROMPT_ID={prompt_id}
ROLE=EXECUTOR
SOURCE_ROLE={'REMOTE_REVIEWER' if event.startswith('MANUAL_') else 'LOCAL_EXECUTOR'}
STATUS={status}
ONE_LINE_RESULT={result}
RESULT_PATH={result_path}
PROMPT_PATH={prompt_path}
KEY_FILES={key_files}
TARGET=MANUAL
RETURN_TARGET=MANUAL
USER_APPROVAL={approval}
SUPERSEDES=NONE
PRO_REVIEW_ID=NONE
REVIEW_PACKET_ID={review_packet_id}
"""
    with log.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(block)


def create_packet(args: argparse.Namespace) -> int:
    project = require_project(args.project)
    result_path = ensure_inside(args.result, project)
    if not result_path.is_file():
        raise FileNotFoundError(f"Result file does not exist: {result_path}")

    result_text = read_text(result_path)
    result_fields = parse_fields(result_text)
    step_id = result_fields.get("STEP_ID") or args.step_id
    if not step_id:
        raise ValueError("STEP_ID is missing from the result; provide --step-id")
    prompt_id = result_fields.get("PROMPT_ID", "NONE")
    stamp = utc_stamp()
    packet_id = args.packet_id or f"REVIEW-{safe_name(step_id)}-{stamp}"
    packet_root = project / ".workflow" / "review_packets"
    packet_dir = packet_root / f"{safe_name(step_id)}_{stamp}_review"
    if packet_dir.exists():
        raise FileExistsError(f"Review packet already exists: {packet_dir}")
    packet_dir.mkdir(parents=True)

    workflow = project / ".workflow"
    packet_template = read_text(workflow / "templates" / "WEB_REVIEW_PACKET.md")
    state_text = read_text(workflow / "WORKFLOW_STATE.md")
    state = parse_fields(state_text)
    brief_text = read_text(workflow / "PROJECT_BRIEF.md")
    profile_text = read_text(workflow / "PROFILE.md")
    plan_text = "NONE"
    plan_value = state.get("ACTIVE_REFERENCE_PLAN_PATH", "NONE")
    if plan_value != "NONE":
        plan_path = project / Path(plan_value)
        if plan_path.is_file():
            plan_text = read_text(plan_path)

    replacements = {
        "<unique-id>": packet_id,
        "<reviewed-step-id>": step_id,
        "<id-or-NOT_APPLICABLE>": state.get("EXECUTOR_TASK_ID", "NOT_APPLICABLE"),
        "<link-or-NOT_APPLICABLE>": state.get("EXECUTOR_TASK_LINK", "NOT_APPLICABLE"),
    }
    for old, new in replacements.items():
        packet_template = packet_template.replace(old, new)

    attachments: list[str] = []
    for index, supplied in enumerate(args.include or [], start=3):
        source = ensure_inside(supplied, project)
        if not source.is_file():
            raise ValueError(f"Attachments must be files, not directories: {source}")
        destination = packet_dir / f"{index:02d}_ATTACHMENT_{safe_name(source.name)}"
        shutil.copy2(source, destination)
        attachments.append(destination.name)

    context = f"""

# Included Project Context

Packet folder after local import: `{packet_dir.relative_to(project).as_posix()}`

## Workflow State Snapshot

{state_text}

## Selected Profile

{profile_text}

## Active Project Brief

{brief_text}

## Active Optional Reference Plan

{plan_text}

## Complete Step Result

{result_text}

## Included Attachment Files

{chr(10).join(f'- `{name}`' for name in attachments) if attachments else '- NONE'}
"""
    (packet_dir / "00_REVIEW_PACKET.md").write_text(
        packet_template.rstrip() + "\n" + context,
        encoding="utf-8",
    )
    shutil.copy2(
        workflow / "templates" / "WEB_REVIEW_RETURN.md",
        packet_dir / "01_REVIEW_RETURN_TEMPLATE.md",
    )
    shutil.copy2(
        workflow / "templates" / "EXECUTION_PROMPT.md",
        packet_dir / "02_EXECUTION_PROMPT_TEMPLATE.md",
    )

    zip_path = Path(shutil.make_archive(str(packet_dir), "zip", root_dir=packet_dir))
    relative_packet = packet_dir.relative_to(project).as_posix()
    relative_zip = zip_path.relative_to(project).as_posix()
    update_state(
        workflow / "WORKFLOW_STATE.md",
        {
            "ACTIVE_REVIEW_PACKET_ID": packet_id,
            "ACTIVE_REVIEW_PACKET_PATH": relative_packet,
            "PHASE": "AWAITING_MANUAL_REVIEW",
            "LAST_UPDATED_UTC": utc_iso(),
        },
    )
    append_event(
        project,
        "REVIEW_PACKET_CREATED",
        step_id,
        prompt_id,
        "COMPLETED",
        "Created flat Manual/Web review packet and zip",
        result_path=result_path.relative_to(project).as_posix(),
        key_files=f"{relative_packet}, {relative_zip}",
        review_packet_id=packet_id,
    )
    print(f"REVIEW_PACKET_ID={packet_id}")
    print(f"REVIEW_PACKET_PATH={packet_dir}")
    print(f"REVIEW_PACKET_ZIP={zip_path}")
    return 0


def import_review(args: argparse.Namespace) -> int:
    project = require_project(args.project)
    packet_dir = ensure_inside(args.packet, project)
    packet_root = (project / ".workflow" / "review_packets").resolve()
    try:
        packet_dir.relative_to(packet_root)
    except ValueError as error:
        raise ValueError("Packet must be under .workflow/review_packets/") from error
    packet_file = packet_dir / "00_REVIEW_PACKET.md"
    if not packet_file.is_file():
        raise FileNotFoundError(f"Packet metadata is missing: {packet_file}")

    packet_fields = parse_fields(read_text(packet_file))
    packet_id = packet_fields.get("REVIEW_PACKET_ID", "")
    reviewed_step = packet_fields.get("STEP_ID", "")
    if not packet_id or not reviewed_step:
        raise ValueError("Review packet metadata is incomplete")

    review_source = args.review_return.expanduser().resolve()
    prompt_source = args.prompt.expanduser().resolve()
    review_text = read_text(review_source)
    prompt_text = read_text(prompt_source)
    review_fields = parse_fields(review_text)
    prompt_fields = parse_fields(prompt_text)
    if review_fields.get("REVIEW_PACKET_ID") != packet_id:
        raise ValueError("REVIEW_RETURN packet ID does not match")
    if review_fields.get("STEP_ID") != reviewed_step:
        raise ValueError("REVIEW_RETURN step ID does not match")
    if review_fields.get("NEXT_PROMPT_APPROVED") != "YES":
        raise ValueError("Review return does not record an approved next prompt")
    approval = review_fields.get("USER_APPROVAL", "NONE")
    if approval == "NONE":
        raise ValueError("Review return is missing USER_APPROVAL")
    prompt_id = prompt_fields.get("PROMPT_ID", "")
    next_step = prompt_fields.get("STEP_ID", "")
    if not prompt_id or not next_step:
        raise ValueError("Next execution prompt is missing PROMPT_ID or STEP_ID")

    log_text = read_text(project / ".workflow" / "STEP_LOG.md")
    if re.search(rf"^PROMPT_ID={re.escape(prompt_id)}$", log_text, re.MULTILINE):
        raise ValueError(f"PROMPT_ID already exists in the log: {prompt_id}")

    review_target = packet_dir / "REVIEW_RETURN.md"
    prompt_target = packet_dir / "NEXT_EXECUTION_PROMPT.md"
    archive_target = project / ".workflow" / "prompts" / "review" / f"{safe_name(prompt_id)}.md"
    for target in (review_target, prompt_target, archive_target):
        if target.exists():
            raise FileExistsError(f"Refusing to overwrite imported review record: {target}")
    review_target.write_text(review_text, encoding="utf-8")
    prompt_target.write_text(prompt_text, encoding="utf-8")
    archive_target.parent.mkdir(parents=True, exist_ok=True)
    archive_target.write_text(prompt_text, encoding="utf-8")

    state_updates = {
        "CURRENT_STEP_ID": next_step,
        "ACTIVE_PROMPT_ID": prompt_id,
        "ACTIVE_PROMPT_PATH": archive_target.relative_to(project).as_posix(),
        "ACTIVE_REVIEW_PACKET_ID": "NONE",
        "ACTIVE_REVIEW_PACKET_PATH": "NONE",
        "LAST_USER_APPROVAL": approval,
        "PHASE": "READY_FOR_EXECUTION",
        "LAST_UPDATED_UTC": utc_iso(),
    }
    if (
        reviewed_step.startswith("step0")
        and review_fields.get("EXECUTOR_PROMOTION") == "APPROVE"
    ):
        state_updates["EXECUTOR_STATUS"] = "ACTIVE"
    update_state(project / ".workflow" / "WORKFLOW_STATE.md", state_updates)

    relative_review = review_target.relative_to(project).as_posix()
    relative_prompt = archive_target.relative_to(project).as_posix()
    append_event(
        project,
        "MANUAL_REVIEW_RETURNED",
        reviewed_step,
        "NONE",
        "COMPLETED",
        f"Imported external review decision {review_fields.get('REVIEW_STATUS', 'UNKNOWN')}",
        result_path=relative_review,
        key_files=relative_review,
        review_packet_id=packet_id,
        approval=approval,
    )
    append_event(
        project,
        "MANUAL_PROMPT_RECEIVED",
        next_step,
        prompt_id,
        "APPROVED",
        "Archived exact user-approved prompt from external Reviewer",
        prompt_path=relative_prompt,
        key_files=f"{relative_review}, {relative_prompt}",
        review_packet_id=packet_id,
        approval=approval,
    )
    if state_updates.get("EXECUTOR_STATUS") == "ACTIVE":
        append_event(
            project,
            "EXECUTOR_PROMOTED",
            reviewed_step,
            "NONE",
            "APPROVED",
            "External Step 0 review accepted and user confirmed Executor promotion",
            result_path=relative_review,
            review_packet_id=packet_id,
            approval=approval,
        )
    print(f"REVIEW_RETURN_PATH={review_target}")
    print(f"ACTIVE_PROMPT_PATH={archive_target}")
    print(f"NEXT_STEP_ID={next_step}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    create = subparsers.add_parser("create", help="Create a flat review packet and zip")
    create.add_argument("project", type=Path)
    create.add_argument("--result", type=Path, required=True)
    create.add_argument("--include", type=Path, action="append")
    create.add_argument("--step-id")
    create.add_argument("--packet-id")
    create.set_defaults(handler=create_packet)

    import_parser = subparsers.add_parser(
        "import", help="Import REVIEW_RETURN and approved next prompt"
    )
    import_parser.add_argument("project", type=Path)
    import_parser.add_argument("--packet", type=Path, required=True)
    import_parser.add_argument("--review-return", type=Path, required=True)
    import_parser.add_argument("--prompt", type=Path, required=True)
    import_parser.set_defaults(handler=import_review)

    args = parser.parse_args()
    try:
        return args.handler(args)
    except (FileExistsError, FileNotFoundError, OSError, RuntimeError, ValueError) as error:
        print(f"REVIEW_PACKET_FAILED: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
