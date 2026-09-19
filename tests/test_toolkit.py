from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INIT = ROOT / "tools" / "init.py"
VALIDATE = ROOT / "tools" / "validate.py"
REVIEW_PACKET = ROOT / "tools" / "review_packet.py"
UPDATE = ROOT / "tools" / "update_project.py"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def initialize(target: Path, mode: str = "manual", profile: str = "generic") -> None:
    result = run(str(INIT), str(target), "--profile", profile, "--mode", mode)
    if result.returncode != 0:
        raise AssertionError(result.stdout + result.stderr)


class ToolkitSmokeTests(unittest.TestCase):
    def test_distribution_validates(self) -> None:
        result = run(str(VALIDATE), "--distribution", str(ROOT))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_all_profile_and_mode_combinations_initialize(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            for profile in ("generic", "research", "software", "writing"):
                for mode in ("direct", "manual"):
                    target = base / f"{profile}-{mode}"
                    initialize(target, mode, profile)
                    state = (target / ".workflow" / "WORKFLOW_STATE.md").read_text(
                        encoding="utf-8"
                    )
                    self.assertIn(f"MODE={mode.upper()}", state)
                    self.assertIn(f"PROFILE={profile}", state)
                    self.assertIn("EXECUTOR_STATUS=CANDIDATE", state)
                    self.assertTrue(
                        (target / ".workflow" / "templates" / "STEP0_START.md").is_file()
                    )
                    self.assertTrue(
                        (target / ".workflow" / "templates" / "WEB_REVIEW_PACKET.md").is_file()
                    )
                    self.assertTrue((target / ".workflow" / "REFERENCE_PLAN.md").is_file())
                    self.assertTrue((target / ".workflow" / "INSTALL_MANIFEST.json").is_file())
                    self.assertTrue((target / "deliverables" / "README.md").is_file())
                    self.assertTrue((target / "incoming" / "README.md").is_file())
                    validation = run(str(VALIDATE), "--project", str(target))
                    self.assertEqual(
                        validation.returncode,
                        0,
                        validation.stdout + validation.stderr,
                    )

    def test_existing_agents_is_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "project"
            target.mkdir()
            agents = target / "AGENTS.md"
            agents.write_text("existing project rules\n", encoding="utf-8")
            initialize(target)
            self.assertEqual(agents.read_text(encoding="utf-8"), "existing project rules\n")
            self.assertTrue((target / ".workflow" / "CODEX_AGENTS_SNIPPET.md").is_file())

    def test_reinitialization_refuses_to_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "project"
            initialize(target)
            state = target / ".workflow" / "WORKFLOW_STATE.md"
            before = state.read_bytes()
            second = run(str(INIT), str(target), "--mode", "direct")
            self.assertNotEqual(second.returncode, 0)
            self.assertIn("Refusing to overwrite", second.stderr)
            self.assertEqual(state.read_bytes(), before)

    def test_existing_project_roots_are_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "project"
            deliverables = target / "deliverables"
            incoming = target / "incoming"
            deliverables.mkdir(parents=True)
            incoming.mkdir(parents=True)
            output_marker = deliverables / "existing.txt"
            source_marker = incoming / "old-paper.pdf"
            output_marker.write_text("keep output\n", encoding="utf-8")
            source_marker.write_text("keep source\n", encoding="utf-8")
            initialize(target)
            self.assertEqual(output_marker.read_text(encoding="utf-8"), "keep output\n")
            self.assertEqual(source_marker.read_text(encoding="utf-8"), "keep source\n")
            self.assertFalse((deliverables / "README.md").exists())
            self.assertFalse((incoming / "README.md").exists())

    def test_manual_review_packet_round_trip_promotes_step0(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            target = base / "project"
            initialize(target)
            result_dir = target / ".workflow" / "step_records" / "step0_demo"
            result_dir.mkdir(parents=True)
            result = result_dir / "STEP_RESULT.md"
            result.write_text(
                """# Step Result

```text
SCHEMA=review-execute-loop/0.3
PROMPT_ID=STEP0-FIXED
STEP_ID=step0
STEP_KIND=INVENTORY
STATUS=COMPLETED
```

Inventory completed.
""",
                encoding="utf-8",
            )
            created = run(
                str(REVIEW_PACKET),
                "create",
                str(target),
                "--result",
                result.relative_to(target).as_posix(),
            )
            self.assertEqual(created.returncode, 0, created.stdout + created.stderr)
            packet_match = re.search(
                r"^REVIEW_PACKET_PATH=(.+)$", created.stdout, re.MULTILINE
            )
            packet_id_match = re.search(
                r"^REVIEW_PACKET_ID=(.+)$", created.stdout, re.MULTILINE
            )
            self.assertIsNotNone(packet_match)
            self.assertIsNotNone(packet_id_match)
            packet_path = Path(packet_match.group(1))
            packet_id = packet_id_match.group(1)
            self.assertTrue(packet_path.is_dir())
            self.assertTrue(packet_path.with_suffix(".zip").is_file())

            review_return = base / "REVIEW_RETURN.md"
            review_return.write_text(
                f"""# Review Return

```text
SCHEMA=review-execute-loop/0.3
REVIEW_PACKET_ID={packet_id}
STEP_ID=step0
REVIEW_STATUS=ACCEPT
EXECUTOR_PROMOTION=APPROVE
NEXT_PROMPT_APPROVED=YES
USER_APPROVAL=user-approved-step1
```
""",
                encoding="utf-8",
            )
            prompt = base / "NEXT_EXECUTION_PROMPT.md"
            prompt.write_text(
                """# Execution Prompt

```text
SCHEMA=review-execute-loop/0.3
PROMPT_ID=PROMPT-step1-demo
STEP_ID=step1
STEP_KIND=MAIN
MODE=MANUAL
REVIEW_SOURCE=external-step0-review
```
""",
                encoding="utf-8",
            )
            imported = run(
                str(REVIEW_PACKET),
                "import",
                str(target),
                "--packet",
                f".workflow/review_packets/{packet_path.name}",
                "--review-return",
                str(review_return),
                "--prompt",
                str(prompt),
            )
            self.assertEqual(imported.returncode, 0, imported.stdout + imported.stderr)
            state = (target / ".workflow" / "WORKFLOW_STATE.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("EXECUTOR_STATUS=ACTIVE", state)
            self.assertIn("CURRENT_STEP_ID=step1", state)
            self.assertTrue((packet_path / "REVIEW_RETURN.md").is_file())
            self.assertTrue((packet_path / "NEXT_EXECUTION_PROMPT.md").is_file())
            log = (target / ".workflow" / "STEP_LOG.md").read_text(encoding="utf-8")
            self.assertIn("REVIEW_PACKET_CREATED", log)
            self.assertIn("MANUAL_REVIEW_RETURNED", log)
            self.assertIn("EXECUTOR_PROMOTED", log)

    def test_current_project_update_check_is_clean(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "project"
            initialize(target, profile="research")
            checked = run(str(UPDATE), str(target), "--check")
            self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
            self.assertIn("SAFE_ADD=0", checked.stdout)
            self.assertIn("SAFE_REPLACE=0", checked.stdout)
            self.assertIn("CONFLICT=0", checked.stdout)

    def test_manual_copy_without_install_manifest_uses_release_baseline(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "project"
            initialize(target, profile="writing")
            (target / ".workflow" / "INSTALL_MANIFEST.json").unlink()
            checked = run(str(UPDATE), str(target), "--check")
            self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
            self.assertIn("FROM_VERSION=0.3.1", checked.stdout)
            self.assertIn("SAFE_ADD=0", checked.stdout)
            self.assertIn("SAFE_REPLACE=0", checked.stdout)
            self.assertIn("CONFLICT=0", checked.stdout)

    def test_update_conflict_is_not_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "project"
            initialize(target)
            workflow = target / ".workflow" / "WORKFLOW.md"
            workflow.write_text(
                workflow.read_text(encoding="utf-8") + "\nUSER CUSTOM RULE\n",
                encoding="utf-8",
            )
            before = workflow.read_bytes()
            prepared = run(str(UPDATE), str(target), "--prepare")
            self.assertEqual(prepared.returncode, 0, prepared.stdout + prepared.stderr)
            self.assertIn("CONFLICT=1", prepared.stdout)
            upgrade_match = re.search(
                r"^UPGRADE_ID=(.+)$", prepared.stdout, re.MULTILINE
            )
            self.assertIsNotNone(upgrade_match)
            applied = run(str(UPDATE), str(target), "--apply", upgrade_match.group(1))
            self.assertEqual(applied.returncode, 2, applied.stdout + applied.stderr)
            self.assertEqual(workflow.read_bytes(), before)
            self.assertIn("UPGRADE_STATUS=PARTIAL", applied.stdout)

    def test_legacy_schema_still_validates_with_warning(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "project"
            initialize(target)
            workflow = target / ".workflow" / "WORKFLOW.md"
            workflow.write_text(
                workflow.read_text(encoding="utf-8").replace(
                    "review-execute-loop/0.3", "review-execute-loop/0.1", 1
                ),
                encoding="utf-8",
            )
            validation = run(str(VALIDATE), "--project", str(target))
            self.assertEqual(
                validation.returncode,
                0,
                validation.stdout + validation.stderr,
            )
            self.assertIn("legacy workflow schema 0.1", validation.stdout)

    def test_release_manifests_are_machine_readable(self) -> None:
        for version in ("0.1.1", "0.2.0", "0.3.0", "0.3.1"):
            path = ROOT / "manifests" / "releases" / f"v{version}.json"
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(payload["toolkit_version"], version)
            self.assertIsInstance(payload["managed_files"], dict)


if __name__ == "__main__":
    unittest.main()
