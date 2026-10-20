# claude-plugins

Personal Claude plugin marketplace (`jrmii-plugins`).

| Plugin | What it is |
|---|---|
| [`endurance-coach`](plugins/endurance-coach/) | The coaching *method* for an endurance-training setup built on three MCP connectors: a coach-state server (plan, positions, constraints in a private git repo), Garmin Connect, and Peloton. Session start, readiness gates, strength selection with per-movement weights and post-session check-ins, Garmin/Peloton pointer-workout procedure, data traps, planning (incl. weather), meal logging. Procedures only: it carries no athlete data and is useless without those connectors |
| [`ballot-briefing`](https://github.com/jrmii/ballot-briefing) | Turns a specific US ballot (photo, list, or jurisdiction + date) into a sourced, non-partisan voter briefing as a mobile-readable HTML artifact: every candidate measured against the office's actual duties, contested claims classified rather than editorialized, and a deep-dive mode for a race the voter is still stuck on. Never recommends a candidate. Lives in its own repo, [`jrmii/ballot-briefing`](https://github.com/jrmii/ballot-briefing); the marketplace entry points there (`github` source, `skills: ["./"]`), so installs track that repo's `main` and its checks run there |

## Install

**claude.ai** (web chat, Claude Desktop Chat tab, Cowork): add a plugin from a repository,
`jrmii/claude-plugins`, then add `endurance-coach` and/or `ballot-briefing`. Plugins installed
on the account also sync to Claude Code when it's signed in.

**Claude Code:**

```sh
claude plugin marketplace add jrmii/claude-plugins
claude plugin install endurance-coach@jrmii-plugins
claude plugin install ballot-briefing@jrmii-plugins
```

Then turn on updates: `/plugin` → Marketplaces → `jrmii-plugins` → Enable auto-update
(or run `claude plugin update <plugin>@jrmii-plugins` after changes).

Plugins here don't set `version`, so installs track commits on `main`. Claude Code shows the
commit SHA as the version; claude.ai numbers its own installs (v1, v2, ...).

**After every change:** Claude Code picks it up only with auto-update on, or
`claude plugin update <plugin>@jrmii-plugins`. claude.ai: plugin settings → check
for update → Update (verified 2026-10-07: d28f8a1 arrived as v2). Whether claude.ai checks
on its own is not yet known; until it does, force the check after important changes.

## Develop

```sh
python3 scripts/check_skills.py              # frontmatter, links, size, forbidden patterns
(cd scripts && python3 -m unittest)          # checker self-tests
claude plugin validate . && for p in plugins/*/; do claude plugin validate "$p"; done
```

CI runs all three on every push. `plugins/<name>/.forbidden-patterns` lists regexes that
must never appear in a plugin's files (personal identifiers, account-specific IDs); this
repo is public.
