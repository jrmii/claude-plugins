"""Negative tests: the checker must catch each class of problem (run: python3 -m unittest)."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from check_skills import main

REPO = Path(__file__).parent.parent
SKILL = "plugins/endurance-coach/skills/endurance-coach"


class CheckSkills(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        shutil.copytree(REPO / "plugins", self.tmp / "plugins")
        self.skill = self.tmp / SKILL

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp)

    def edit(self, rel: str, old: str, new: str) -> None:
        p = self.skill / rel
        text = p.read_text()
        self.assertIn(old, text)
        p.write_text(text.replace(old, new, 1))

    def test_repo_passes(self) -> None:
        self.assertEqual(main(self.tmp), 0)

    def test_personal_data_caught(self) -> None:
        (self.skill / "references" / "data.md").write_text("Ask Jim about workout 1722982584.")
        self.assertEqual(main(self.tmp), 1)

    def test_missing_reference_caught(self) -> None:
        with (self.skill / "SKILL.md").open("a") as f:
            f.write("\nsee references/missing.md\n")
        self.assertEqual(main(self.tmp), 1)

    def test_unlinked_reference_caught(self) -> None:
        (self.skill / "references" / "orphan.md").write_text("never linked")
        self.assertEqual(main(self.tmp), 1)

    def test_reserved_name_caught(self) -> None:
        self.edit("SKILL.md", "name: endurance-coach", "name: claude-coach")
        self.assertEqual(main(self.tmp), 1)

    def test_long_description_caught(self) -> None:
        self.edit("SKILL.md", "description: ", "description: " + "x" * 1100)
        self.assertEqual(main(self.tmp), 1)


if __name__ == "__main__":
    unittest.main()


class VersionGuard(unittest.TestCase):
    """claude.ai installs a plugin update only when plugin.json's version changes."""

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        shutil.copytree(REPO / "plugins", self.tmp / "plugins")
        self.manifest = self.tmp / "plugins/endurance-coach/.claude-plugin/plugin.json"
        self.env = {
            **{k: v for k, v in os.environ.items() if not k.startswith("GIT_")},
            "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.com",
            "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.com",
            "GIT_CONFIG_GLOBAL": "/dev/null",
        }
        self.git("init", "-q", "-b", "main")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "base")
        self.git("tag", "base")

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp)

    def git(self, *args: str) -> None:
        subprocess.run(["git", *args], cwd=self.tmp, env=self.env, check=True, capture_output=True)

    def set_version(self, version: object) -> None:
        data = json.loads(self.manifest.read_text())
        data["version"] = version
        self.manifest.write_text(json.dumps(data))

    def touch_skill(self) -> None:
        with (self.tmp / SKILL / "SKILL.md").open("a") as f:
            f.write("\nA new rule.\n")

    def test_unchanged_plugin_passes(self) -> None:
        self.assertEqual(main(self.tmp, "base"), 0)

    def test_skill_change_without_bump_fails(self) -> None:
        self.touch_skill()
        self.assertEqual(main(self.tmp, "base"), 1)
        self.git("commit", "-qam", "rule")  # committed but unpushed: still caught
        self.assertEqual(main(self.tmp, "base"), 1)

    def test_skill_change_with_bump_passes(self) -> None:
        self.touch_skill()
        old = json.loads(self.manifest.read_text())["version"]
        major, minor, patch = (int(x) for x in old.split("."))
        self.set_version(f"{major}.{minor}.{patch + 1}")
        self.assertEqual(main(self.tmp, "base"), 0)

    def test_lower_or_missing_version_fails(self) -> None:
        self.touch_skill()
        self.set_version("0.0.1")
        self.assertEqual(main(self.tmp, "base"), 1)
        self.set_version(None)
        self.assertEqual(main(self.tmp, "base"), 1)

    def test_no_base_checks_presence_only(self) -> None:
        self.touch_skill()
        self.assertEqual(main(self.tmp, "no-such-rev"), 0)
        self.assertEqual(main(self.tmp, None), 0)
