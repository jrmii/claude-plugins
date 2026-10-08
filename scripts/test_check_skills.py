"""Negative tests: the checker must catch each class of problem (run: python3 -m unittest)."""

from __future__ import annotations

import shutil
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
