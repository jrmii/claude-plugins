# claude-plugins

Personal Claude plugin marketplace (`jrmii-plugins`).

| Plugin | What it is |
|---|---|
| [`endurance-coach`](plugins/endurance-coach/) | The coaching *method* for an endurance-training setup built on three MCP connectors: a coach-state server (plan, positions, constraints in a private git repo), Garmin Connect, and Peloton. Session start, readiness gates, strength selection with per-movement weights and post-session check-ins, Garmin/Peloton pointer-workout procedure, data traps, planning (incl. weather), meal logging. Procedures only: it carries no athlete data and is useless without those connectors |

## Install

**claude.ai** (web chat, Claude Desktop Chat tab, Cowork): add a plugin from a repository,
`jrmii/claude-plugins`, then add `endurance-coach`. Plugins installed on the account also
sync to Claude Code when it's signed in.

**Claude Code:**

```sh
claude plugin marketplace add jrmii/claude-plugins
claude plugin install endurance-coach@jrmii-plugins
```

Then turn on updates: `/plugin` → Marketplaces → `jrmii-plugins` → Enable auto-update
(or run `claude plugin update endurance-coach@jrmii-plugins` after changes).

Plugins here don't set `version`, so installs track commits on `main`. Claude Code shows the
commit SHA as the version; claude.ai numbers its own installs (v1, v2, ...).

**After every change:** Claude Code picks it up only with auto-update on, or
`claude plugin update endurance-coach@jrmii-plugins`. claude.ai: plugin settings → check
for update → Update (verified 2026-10-07: d28f8a1 arrived as v2). Whether claude.ai checks
on its own is not yet known; until it does, force the check after important changes.

## Develop

```sh
python3 scripts/check_skills.py              # frontmatter, links, size, forbidden patterns
(cd scripts && python3 -m unittest)          # checker self-tests
claude plugin validate . && claude plugin validate plugins/endurance-coach
```

CI runs all three on every push. `plugins/<name>/.forbidden-patterns` lists regexes that
must never appear in a plugin's files (personal identifiers, account-specific IDs); this
repo is public.
