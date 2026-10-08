# Connector surfaces: baseline and change check

Peloton's own MCP connector ("Peloton First Party") is new and expected to change quickly.
**At every weekly planning session and mid-week review**, compare the tools you can see
against the baseline below. If anything differs (a tool added or removed, parameters
changed, a gap closed), tell the athlete in one or two lines, re-evaluate what it enables,
and update this file (plugin repo) with the new baseline and date. If nothing changed, say
nothing.

The other connectors (Garmin Connect, Peloton on roac, coach-state) run pinned code and
change only by deliberate pin bumps, so they need no polling.

## Peloton First Party — baseline 2026-10-07

| Tool | Parameters | Notes |
|---|---|---|
| `search` | `query` (natural language; up to 3 comma-separated), `limitPerQuery` (≤ 15) | Results carry Peloton's class `id` (= ride id) and the connector's own `index`. Query words steer discipline: "for runners" returned only Tread runs; "<instructor> strength" found the Strength for Runners classes. Match on `id`, never on title |
| `fetch` | `index`, `locale` | Air date, equipment tags, muscle-group percentages (quick leg-load screen). **No structure** (`segments` empty, `duration` 0) |
| `schedule` | `classes: [{index, startTime}]` | Writes to the athlete's Peloton schedule. Returns per-class success/failure only |
| `create-training-plan` | `plan: [{date, index? , isRestDay?}]` (≤ 14 days), `title` | Interactive chat widget; not useful for automation |

**Gaps that block using `schedule`:** no tool reads the athlete's schedule (so no
duplicate check and no read-back) and no tool unschedules (a changed plan leaves stale
entries). Until both exist, don't call `schedule`: delivery stays the Garmin pointer
workout with the class URL, and the athlete schedules on Peloton himself.

**Use now:** `fetch` muscle-group percentages as a second leg-load check next to the
structure inspection (references/strength.md). Class selection, structure and workout
history stay with the roac Peloton connector.
