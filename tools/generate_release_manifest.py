#!/usr/bin/env python3
"""Generate a historical release checksum manifest from an extracted source tree."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from workflow_manifest import sha256_file


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    source = args.source.resolve()
    version = (source / "VERSION").read_text(encoding="utf-8-sig").strip()
    workflow = source / "starter" / ".workflow" / "WORKFLOW.md"
    text = workflow.read_text(encoding="utf-8-sig")
    match = re.search(r"review-execute-loop/(0\.[0-9]+)", text)
    schema = match.group(1) if match else "unknown"
    managed: dict[str, dict[str, str]] = {
        ".workflow/WORKFLOW.md": {
            "source": "starter/.workflow/WORKFLOW.md",
            "sha256": sha256_file(workflow),
        }
    }
    for template in sorted((source / "templates").glob("*.md")):
        managed[f".workflow/templates/{template.name}"] = {
            "source": f"templates/{template.name}",
            "sha256": sha256_file(template),
        }
    profiles = {
        profile.stem: {
            "source": profile.relative_to(source).as_posix(),
            "sha256": sha256_file(profile),
        }
        for profile in sorted((source / "profiles").glob("*.md"))
    }
    manifest = {
        "format": 1,
        "toolkit_version": version,
        "workflow_schema": schema,
        "managed_files": managed,
        "profile_hashes": profiles,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
