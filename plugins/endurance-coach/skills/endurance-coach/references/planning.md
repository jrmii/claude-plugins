# Planning a week (and adjusting one)

Usually done in Claude Code with the coach-state repo checked out; chat can propose and
record notes/overrides but doesn't edit plan structure.

## Before planning week N+1
0. Connector check (references/connectors.md): has the Peloton first-party surface changed?
1. **Reconcile week N first** into its `actuals:` (Garmin activities vs plan; the engine
   does this once deployed). Unexplained divergence → a pending question.
2. Read: `season.yaml` (this week's target long run, weekly volume, phase intent),
   `constraints.yaml` (travel, events, lodging, family), `races.yaml`, positions
   (strength placement, long-run day, PZE ride, HR caps), `questions.yaml`.
3. Read current state from Garmin: training status (acute/chronic load, ratio, load
   balance), HRV trend (2 weeks), sleep (1 week), readiness, last 1–2 weeks of activities.
   Note recent illness/travel/heat.

## Building the week
- Respect the season target, then adjust for readiness and constraints. Gates only hold or
  reduce; put a `gate:` + `fallback:` on key sessions (quality and long run).
- Strength per references/strength.md and the placement position.
- One `days:` entry per date: `sport`, `session`, caps/bands (`hr_cap`), `gate`,
  `fallback`, `then` (follow-on session), `optional`.
- Volume arithmetic in the week file's `targets`, with the sum shown.
- Push to Garmin only when the athlete approves (references/garmin-writes.md); record IDs
  in `garmin.workouts`, picks in `peloton:` with `why`, `prescription`, `check_in`.
- Commit with trailers: `Trigger`, `Actor`, `Model`, `Via` (coach-state README).

## Weather for outdoor sessions (hot/humid months)
- NWS: `https://api.weather.gov/points/<lat>,<lon>` → `forecastHourly` URL; read
  temperature, **dew point**, RH, wind, precipitation probability for the session window.
- Dew point in the mid-70s °F with air in the high 70s means little evaporative cooling:
  an HR-capped outdoor session turns into heavy walking; prefer the treadmill.
- Thunderstorm probability rising through the session window is a safety call, not a
  training one: move indoors or shorten.
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
