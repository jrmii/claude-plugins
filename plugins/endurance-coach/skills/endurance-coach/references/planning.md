# Planning a week (and adjusting one)

Usually done in Claude Code with the coach-state repo checked out; chat can propose and
record notes/overrides but doesn't edit plan structure.

## Before planning week N+1
0. Connector check (references/connectors.md): has the Peloton first-party surface changed?
1. **Reconcile week N first** into its `actuals:` (Garmin activities vs plan; the engine
   does this once deployed). Unexplained divergence → a pending question.
   Then `search_positions("review")`: for any position that names data to collect and a
   review date, add that week's figures as a note (show the arithmetic); on or after the
   review date, raise the review with the athlete.
   Close constraints and open items the week's decisions ended (e.g. a nutrition phase).
   **Log Claude's errors:** for every claim Claude (chat or Claude Code) made this week and
   later withdrew, add a row to `retractions.md`: next number, date of the claim, the claim
   (with its note SHA), why it was withdrawn, who caught it (athlete, chat self-correction,
   reconcile, validation), and the correcting note/commit. Find them in the week's notes:
   `supersedes_note`, "CORRECTION", "withdrawn", "was wrong", and claims the athlete
   corrected in chat. Not every correction counts: a changed plan, or a fact the athlete
   updated, isn't a retraction. If the fix shipped (skill, MCP), cite that commit too.
2. Read: `season.yaml` (this week's target long run, weekly volume, phase intent),
   `constraints.yaml` (travel, events, lodging, family), `races.yaml`, positions
   (strength placement, long-run day, PZE ride, HR caps), `questions.yaml`.
3. Read current state from Garmin: training status (acute/chronic load, ratio, load
   balance), HRV trend (2 weeks), sleep (1 week), readiness, last 1–2 weeks of activities.
   Note recent illness/travel/heat, and big on-feet days (data.md "Time on feet").
   Ask about known on-feet days in the coming week (theme parks, travel, events) and
   keep them off the day before a race or a key long run; if one can't move, lighten
   the session after it.
4. **Threshold freshness.** Read `athlete.yaml` thresholds (LTHR, threshold pace, VT1
   proxy, max HR) with their dates, and Garmin `get_lactate_threshold` /
   `get_heart_rate_zones`. Flag a value older than ~8 weeks, or one Garmin's auto-detect
   changed since it was recorded, and propose a re-test slot (TT, ramp) in the plan
   rather than quoting a stale number. A treadmill auto-detect's pace isn't adopted
   without a belt check (data.md).
5. **Consumables and gear** (positions "Consumables"): project, don't just report.
   - Fuel: `get_inventory` on hand vs need through the next restock window (long-run
     minutes / 30 = units; real food counts on the Tread), and drink mix by bottles per
     run. Name the run where stock runs out and the order-by date (allow shipping).
   - Shoes and bikes: `get_gear` distance vs retirement (shoes 400 mi), projected from the
     season's weekly volume to each race date; a race pair must be broken in before it.
   - Service items: anything `due` within the next ~4 weeks or overdue; `check_mileage`
     items against `get_gear`. Say what to do and by when.
   - New gear or a new practice (tubeless tires, a helmet, a new strap): add it to
     `inventory.yaml` in Claude Code with its interval and source, and record when it
     was last done (ask; don't guess dates).

## Building the week
- Respect the season target, then adjust for readiness and constraints. Gates only hold or
  reduce; put a `gate:` + `fallback:` on key sessions (quality and long run).
- Strength per references/strength.md and the placement position.
- **Long runs default to a plain Run**, not a structured workout: Garmin holds the
  watch's eat/drink alerts while a structured workout runs, so fuel reminders don't fire.
  If a long run needs structure (segments, a test), build in explicit fuel steps at the
  30-min slots instead, and say which the athlete is getting.
- **A test must be able to fire its own rule.** Before placing a test or check inside a
  session (a ramp, a nasal-breathing threshold check, a strap test), write its decision
  rule ("if X happens, then Y") and confirm the session's caps, alerts, venue and duration
  let X happen. A check whose signal appears above the session's HR cap can't run under
  that cap: lift the cap for that segment, move the check to a session without one, or
  drop it. (2026-10-26..28: a nasal threshold check was placed inside capped easy runs
  three times, and the athlete caught it.)
- One `days:` entry per date: `sport`, `session`, caps/bands (`hr_cap`), `gate`,
  `fallback`, `then` (follow-on session), `optional`.
- Volume arithmetic in the week file's `targets`, with the sum shown.
- Push to Garmin without waiting for a go-ahead (SKILL.md rule 8; references/garmin-writes.md),
  then report what was pushed; record IDs
  in `garmin.workouts`, picks in `peloton:` with `why`, `prescription`, `check_in`.
- Commit with trailers: `Trigger`, `Actor`, `Model`, `Via` (coach-state README).

## Sick days
The criteria are the athlete's position "Sick-day procedure" (`search_positions("sick")`):
quote them, don't improvise. In order:
1. Ask about symptoms (one question): fever, aches, chest, stomach, or only above the neck.
2. Any rest criterion (fever, whole-body, chest, GI): rest; record an override for the
   planned session.
3. Above the neck only: the objective check (waking resting HR vs its 7-day baseline;
   HRV). Before counting a rise or drop, check the week's notes and constraints for a
   known cause (travel, short sleep, alcohol, heat, yesterday's hard session): name it
   and let the symptoms and the 10-minute test decide. With no known cause, the check
   stands.
4. Easy session with the 10-minute test; no intensity, long runs or heavy strength until
   symptoms are gone. Stop signs (chest pain, palpitations, HR out of line with effort,
   dizziness, disproportionate breathlessness) end the session: tell the athlete to get
   checked.
5. Return per the position; missed volume isn't made up. Note each sick day's symptoms
   and decision with `add_note`.

## Weather for outdoor key sessions (all year)
- Use coach-state `get_forecast(date, from_hour, to_hour)`: NWS hourly with temperature,
  **dew point**, RH, wind, precipitation probability and a `thunder` flag. It defaults to
  the athlete's home; when traveling, pass the trip location's `lat`/`lon` (US only).
  Times come back local to the location; cite the `updated` time.
- Only if that tool is unavailable: NWS `https://api.weather.gov/points/<lat>,<lon>` →
  `forecastHourly`, with coordinates from `athlete.yaml` → `weather.home` and the
  User-Agent from `weather.user_agent` (a fixed project string). **Never put the athlete's
  email, name or any personal identifier in a request header or URL.**
- Outside the hot months the same read covers cold, wind, rain and darkness (sunrise for
  early starts).
- **Long-run venue** follows the athlete's position "Long-run venue: outdoor vs Tread"
  (standing rule 2026-11-01): outdoors by default, never a dew-point lookup.
  - **Danger is the coach's call**, made unprompted with the reason: lightning (the
    `thunder` flag, rising thunderstorm probability in the window), any NWS warning or
    watch for the window (tropical storm, hurricane, tornado, high wind, flood, extreme
    heat), flooding or debris on the route, dense fog on dark roads, or an air-quality
    alert. Go indoors, move the start, or shorten. `get_forecast` (coach-state-mcp
    v0.1.12) returns active NWS `alerts` with `in_window`; alerts are what's active now,
    so read again the day before and the morning of. This applies to **every** outdoor
    session (easy runs and rides too), not only long runs: session-start check
    `weather-alerts`.
  - Heat changes how, not where: at dew point ≥ 70 °F raise fluid, set a slower expected
    pace at the same effort, plan cooling and an early start. Heat index ≥ 103 °F for
    most of the window: start earlier or go indoors.
  - Write the bail rule into the day entry: Tread at a house stop if nasal breathing
    breaks at easy feel, or on heat signs.
  - The athlete may pick the Tread on the day without a reason: record the swap
    (`record_override`) and adjust fuel. His Tread dislike is a real cost in every call.
- Thunderstorm probability rising through any outdoor session window is a safety call,
  not a training one: move indoors or shorten.
- Check the alternative day before proposing a swap; cite the forecast issue time.

## Mid-week review ("should I continue as planned?")
0. Connector check (references/connectors.md): has the Peloton first-party surface changed?
1. `get_today`; the remaining days' plan entries.
2. Garmin: HRV trend (2 weeks), sleep (1 week), readiness today, training status,
   activities since Monday (and last week for context); `get_activity` for key sessions
   (training effect, load, the athlete's feel/RPE).
3. Volume so far vs target, with arithmetic; what the remaining days add.
4. Weather for remaining outdoor sessions.
5. Answer: continue / adjust, with small, specific changes; don't restructure without a
   signal. State what you did and didn't check.

## Race plan and retrospective
- **Plan (T-14d, Claude Code):** `races/<race-id>-pace-plan.md` in coach-state (pace bands,
  course and terrain sections, fuel slots, contingencies); the race-day `days:` entry quotes
  its summary and names the file. From chat, read the whole plan with
  `get_file("races/<race-id>-pace-plan.md")` (coach-state-mcp v0.1.15; races/ and
  evidence/ are read-only from chat) before answering about pacing: the day entry carries
  only the one-line summary.
- **Retrospective (T+2d):** gather from Garmin (`get_activity`, splits, HR, weather, fuel
  actually taken) and ask the athlete how it went (one question at a time). In chat, record
  it with `add_note` on the **race date**, the text starting `RACE RETRO <race-id>:`
  (result, splits against the plan's bands, what held and what broke, fuel and GI, what
  changes next time). There is no race-file write tool, by design.
- **Reconcile (Claude Code):** at the weekly reconcile, write each `RACE RETRO` note into
  `races/<race-id>-retrospective.md` (citing the note's `recorded_at`), add the result to
  `races.yaml`, and carry any lesson into positions or the next race's plan. The note stays
  in the week file.
