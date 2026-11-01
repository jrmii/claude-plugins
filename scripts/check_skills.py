"""Validate every skill in every plugin of this marketplace.

    python3 scripts/check_skills.py [ROOT]

Per skill (plugins/*/skills/*/SKILL.md): frontmatter per the Agent Skills spec (name
1-64 chars of lowercase letters, digits and hyphens, no reserved words, matching its
directory; description 1-1024 chars; no XML tags in either); every references/*.md linked
from SKILL.md exists and every reference file is linked (no unreachable files); body
within a word budget (~5k-token guidance). Per plugin: a skill may declare forbidden
patterns in <plugin>/.forbidden-patterns (one regex per line, # comments) — used to keep
personal data out of a public repo. Per plugin, version guard: .claude-plugin/plugin.json
has a semver "version", and when any file in the plugin differs from the base revision
(default origin/main; CHECK_BASE or --base=REV to override), the version must be higher
than the base's. claude.ai installs a plugin update only when the version changes: without
it, a week of skill pushes (2026-10-25..11-01) never reached a chat. Exit 1 with one line
per problem.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

BODY_WORD_BUDGET = 3500


def frontmatter(text: str) -> tuple[dict[str, str], str] | None:
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        return None
    fields = {}
    for line in m.group(1).splitlines():
        key, sep, value = line.partition(":")
        if sep:
            fields[key.strip()] = value.strip()
    return fields, m.group(2)


def forbidden_patterns(plugin: Path) -> list[re.Pattern[str]]:
    f = plugin / ".forbidden-patterns"
    if not f.exists():
        return []
    lines = [ln.strip() for ln in f.read_text(encoding="utf-8").splitlines()]
    return [re.compile(ln) for ln in lines if ln and not ln.startswith("#")]


def check_skill(skill: Path, patterns: list[re.Pattern[str]], root: Path) -> list[str]:
    rel = skill.relative_to(root)
    problems: list[str] = []
    text = (skill / "SKILL.md").read_text(encoding="utf-8")
    parsed = frontmatter(text)
    if parsed is None:
        return [f"{rel}/SKILL.md: missing YAML frontmatter"]
    fm, body = parsed
    name, desc = fm.get("name", ""), fm.get("description", "")
    if not re.fullmatch(r"[a-z0-9-]{1,64}", name):
        problems.append(f"{rel}: name {name!r} must be 1-64 lowercase letters/digits/hyphens")
    if re.search(r"anthropic|claude", name):
        problems.append(f"{rel}: name contains a reserved word")
    if name and name != skill.name:
        problems.append(f"{rel}: name {name!r} doesn't match directory {skill.name!r}")
    if not desc or len(desc) > 1024:
        problems.append(f"{rel}: description must be 1-1024 chars (is {len(desc)})")
    if re.search(r"<[^>]+>", name + desc):
        problems.append(f"{rel}: XML tags in name/description")
    if (words := len(body.split())) > BODY_WORD_BUDGET:
        problems.append(f"{rel}: SKILL.md body {words} words > budget {BODY_WORD_BUDGET}")

    linked = set(re.findall(r"references/[\w.-]+\.md", text))
    present = {f"references/{p.name}" for p in (skill / "references").glob("*.md")}
    problems += [f"{rel}: SKILL.md links missing {r}" for r in sorted(linked - present)]
    problems += [f"{rel}: {r} is never linked from SKILL.md" for r in sorted(present - linked)]

    for path in sorted(skill.rglob("*")):
        if not path.is_file():
            continue
        content = path.read_text(encoding="utf-8", errors="replace")
        for pat in patterns:
            if hit := pat.search(content):
                problems.append(
                    f"{path.relative_to(root)}: forbidden {hit.group(0)!r} ({pat.pattern})"
                )
    return problems


def _git(root: Path, *args: str) -> str | None:
    try:
        r = subprocess.run(
            ["git", "-C", str(root), *args], capture_output=True, text=True, check=False
        )
    except OSError:
        return None
    return r.stdout if r.returncode == 0 else None


def _semver(value: object) -> tuple[int, int, int] | None:
    m = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", str(value or ""))
    return (int(m[1]), int(m[2]), int(m[3])) if m else None


def check_version(plugin: Path, root: Path, base: str | None) -> list[str]:
    rel = plugin.relative_to(root)
    manifest = plugin / ".claude-plugin" / "plugin.json"
    if not manifest.exists():
        return [f"{rel}: missing .claude-plugin/plugin.json"]
    version = json.loads(manifest.read_text(encoding="utf-8")).get("version")
    if _semver(version) is None:
        return [f"{rel}/.claude-plugin/plugin.json: version {version!r} must be semver X.Y.Z"]
    if not base or _git(root, "rev-parse", "--verify", "--quiet", f"{base}^{{commit}}") is None:
        return []  # no base to compare (not a git checkout, first push): presence only
    changed = _git(root, "diff", "--name-only", base, "--", str(rel))
    untracked = _git(root, "ls-files", "--others", "--exclude-standard", "--", str(rel))
    if not (changed or "").strip() and not (untracked or "").strip():
        return []
    old = _git(root, "show", f"{base}:{rel}/.claude-plugin/plugin.json")
    try:
        old_version = json.loads(old).get("version") if old else None
    except ValueError:
        old_version = None
    old_v = _semver(old_version)
    if old_v is not None and _semver(version) <= old_v:
        return [
            f"{rel}: files changed since {base} but version {version} isn't above "
            f"{old_version}: bump .claude-plugin/plugin.json (claude.ai won't update otherwise)"
        ]
    return []


def main(root: Path, base: str | None = None) -> int:
    problems: list[str] = []
    skills = 0
    for plugin in sorted((root / "plugins").iterdir()):
        if not plugin.is_dir():
            continue
        patterns = forbidden_patterns(plugin)
        problems += check_version(plugin, root, base)
        for skill_md in sorted(plugin.glob("skills/*/SKILL.md")):
            skills += 1
            problems += check_skill(skill_md.parent, patterns, root)
    if skills == 0:
        problems.append("no skills found under plugins/*/skills/*/SKILL.md")
    for p in problems:
        print(f"FAIL: {p}")
    if not problems:
        print(f"ok: {skills} skill(s) valid")
    return 1 if problems else 0


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--base=")]
    flags = [a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--base=")]
    root_arg = Path(args[0]) if args else Path(__file__).parent.parent
    sys.exit(main(root_arg, flags[-1] if flags else os.environ.get("CHECK_BASE", "origin/main")))
