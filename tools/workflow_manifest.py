"""Shared manifest helpers for Review-Execute Loop initialization and upgrades."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


REPOSITORY = "https://github.com/JUSTWE-AWAY/Review-Execute-Loop"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def toolkit_version(repo_root: Path) -> str:
    return (repo_root / "VERSION").read_text(encoding="utf-8-sig").strip()


def workflow_schema(repo_root: Path) -> str:
    text = (repo_root / "starter" / ".workflow" / "WORKFLOW.md").read_text(
        encoding="utf-8-sig"
    )
    marker = "review-execute-loop/"
    start = text.index(marker) + len(marker)
    return text[start:].split("`", 1)[0].split()[0]


def managed_sources(repo_root: Path, profile: str) -> dict[str, Path]:
    sources: dict[str, Path] = {
        ".workflow/WORKFLOW.md": repo_root / "starter" / ".workflow" / "WORKFLOW.md",
        ".workflow/PROFILE.md": repo_root / "profiles" / f"{profile}.md",
    }
    for source in sorted((repo_root / "templates").rglob("*")):
        if source.is_file():
            relative = source.relative_to(repo_root / "templates").as_posix()
            sources[f".workflow/templates/{relative}"] = source
    return sources


def build_manifest(repo_root: Path, project_root: Path, profile: str) -> dict[str, object]:
    managed: dict[str, dict[str, str]] = {}
    for destination, source in managed_sources(repo_root, profile).items():
        installed = project_root / Path(destination)
        if installed.is_file():
            managed[destination] = {
                "source": source.relative_to(repo_root).as_posix(),
                "sha256": sha256_file(installed),
            }
    return {
        "format": 1,
        "toolkit_version": toolkit_version(repo_root),
        "workflow_schema": workflow_schema(repo_root),
        "profile": profile,
        "source_repository": REPOSITORY,
        "installed_at_utc": utc_now(),
        "managed_files": managed,
        "unresolved_conflicts": [],
    }


def write_manifest(path: Path, manifest: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8-sig"))
