from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INIT = ROOT / "tools" / "init.py"
VALIDATE = ROOT / "tools" / "validate.py"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


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
                    result = run(
                        str(INIT),
                        str(target),
                        "--profile",
                        profile,
                        "--mode",
                        mode,
                    )
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    state = (target / ".workflow" / "WORKFLOW_STATE.md").read_text(
                        encoding="utf-8"
                    )
                    self.assertIn(f"MODE={mode.upper()}", state)
                    self.assertIn(f"PROFILE={profile}", state)
                    self.assertTrue(
                        (target / ".workflow" / "templates" / "PROJECT_SETUP_START.md").is_file()
                    )
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
            result = run(str(INIT), str(target), "--mode", "manual")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(agents.read_text(encoding="utf-8"), "existing project rules\n")
            self.assertTrue((target / ".workflow" / "CODEX_AGENTS_SNIPPET.md").is_file())

    def test_reinitialization_refuses_to_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "project"
            first = run(str(INIT), str(target), "--mode", "manual")
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            state = target / ".workflow" / "WORKFLOW_STATE.md"
            before = state.read_bytes()
            second = run(str(INIT), str(target), "--mode", "direct")
            self.assertNotEqual(second.returncode, 0)
            self.assertIn("Refusing to overwrite", second.stderr)
            self.assertEqual(state.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
