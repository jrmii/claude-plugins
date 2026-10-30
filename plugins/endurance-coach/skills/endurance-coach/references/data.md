# Data discipline: recurring traps

The authoritative, dated list is coach-state `data-defects.md` (`get_file`). Check it
before trusting a metric you haven't used recently. Summary of the traps that recur:

## Power: two scales, never compared
- Garmin/Assioma (pedals) and Peloton (bike) read differently, intensity-dependent; each
  has its own FTP (coach-state `athlete.yaml` → `power`). Compare Assioma power only with
  Assioma FTP and zones, Peloton with Peloton. No conversion coefficient.
- Peloton class zone/target figures (`why_scale: peloton_class_targets`) are prescriptions
  on the Peloton scale, not measurements, and never comparable to Garmin zone time.

## Peloton device types (`workouts_list` / workout detail)
- `home_tread` = Tread, `home_bike_v1` = Bike (gen 1), `t21n8m2` = Guide (camera; strength,
  display name "Guide"), `garmin_connect` = synced in from Garmin (not a Peloton record).

## Garmin vs Peloton for the same session
- HR: the same strap broadcasts to both; Garmin is canonical.
- Tread: belt speed and incline exist only in Peloton (the watch estimates pace from
  stride and has no grade signal). Belt distance is closer to truth than the stride model;
  the watch copy is calibrated to it.
- Running power: Garmin running power and Peloton Tread output are different scales
  (as with bike power): never compare or combine them.
- Peloton HR zones are its own %max model: never use them; use Garmin zones.
- `workouts_performance` splits are pace-normalised (don't sum them); sample times are
  `seconds_since_pedaling_start`.

## Calories
- Inflated (never use for energy balance or "eating back"): calories **recorded by a
  Peloton device** (Peloton's own figure for a Bike or Tread session, ~1.8–2×) and Garmin
  **strength/stretch** calories (~1.5–2×).
- Credible: **run calories recorded by the watch**, including runs done on the Tread (the
  watch's figure, not Peloton's). It's the recording device that matters, not where the
  run happened.

## Weight and body composition
- Source of truth: Garmin Index scale via Garmin Connect. Never Apple Health.
- Exclude MANUAL weigh-ins equal to the nutrition plan's starting weight, or identical to an
  Index reading within 3 days (artifacts). Body fat/muscle only from INDEX_SCALE rows.
- Post-run Index readings are unusable for body composition.

## Activities
- Activity lists: unfiltered and paginated. Sub-type filters (e.g. `indoor_cycling`) error
  or miss data; a filtered query is not a census.
- Duplicates (watch + synced copy) can exist; device_manufacturer (from `get_activity`)
  tells them apart: keep the GARMIN copy.
- Peloton stretch classes arrive as `strength_training` (since Aug 2026; `mobility`
  before): don't count ≤15-min "Stretch" entries as strength sessions.
- The watch truncates activity names created from workouts at 32 characters (Connect
  itself takes long names; rename afterwards, references/garmin-writes.md).
- Activity temperature: if coach-state records an external temperature sensor (e.g. a
  Garmin Tempe, data-defects.md), activity temps come from it, not the wrist sensor; read
  where it was mounted before calling them ambient. The weather card in `get_activity` is a
  nearby station (often an airport), not the athlete's sensor.
- Treadmill runs: "Save & Calibrate" on the watch corrects the total distance only; lap
  distances and paces stay the uncalibrated accelerometer estimate. Use Peloton belt data
  for pace within a Tread run.
- Late uploads happen: a day isn't complete until the device's last upload is after it.

## Readiness inputs
- Wake readiness = the `AFTER_WAKEUP_RESET` entry of `get_training_readiness`.
- HRV: single nights are noisy; use status + weekly average (`get_hrv_trend`). The number in
  a feedback code (`HRV_BALANCED_8`) is a message code, not a count of nights: count the
  streak from the daily statuses.
- A low sleep score with a known logistics cause (late pickup, travel) is not a recovery
  signal: check notes.

## FIT-only data (`get_activity_fit_messages`)
The curated endpoints (`get_activity`, splits, HR zones) don't carry everything the devices
record. Before saying a signal is "not available", check the FIT file.
- `record` messages, 1 Hz: `heart_rate` is the merged HR (strap, falling back to wrist
  when the strap drops). Undocumented fields, mapped 2026-10-30 against Connect on 3-6
  activities each, on the athlete's watch and strap (models and firmware in coach-state
  data-defects). The connector returns the raw names until the upstream garmin_mcp release
  adds aliases:

  | Raw field | Meaning | Confidence |
  |---|---|---|
  | `unknown_144` | strap-only HR (gaps mark strap dropouts) | confirmed |
  | `unknown_136` | wrist optical HR (equals `heart_rate` when no strap) | likely |
  | 108 (`enhanced_respiration_rate`) | breathing rate × 100, br/min; strap only | FIT SDK |
  | `unknown_143` | Body Battery (last − first = activity Body Battery impact) | confirmed |
  | `unknown_137` | potential stamina % | confirmed |
  | `unknown_138` | available stamina % (drops below potential on hard efforts) | confirmed |
  | `unknown_90` | performance condition (Connect's chart, sample for sample) | confirmed |

  On a different watch or firmware, re-check before relying on a mapping. A step in
  breathing rate at a steady stage is a ventilatory-threshold marker; flat breathing rate
  while HR climbs at a steady pace points to heat drift, not rising intensity.
- **Strap test** (post-session, any run with a strap): count records where `heart_rate`
  equals `unknown_144`. Near 100% means the strap supplied HR throughout. Zero
  `unknown_144` samples means wrist HR only.
- Running dynamics in `record` (ground contact time, ground contact balance % left,
  vertical ratio) need a strap or pod. Compare left/right balance only within one surface
  (treadmill vs outdoor differ).
- `device_info`: firmware per device (watch, sensor hub, wrist HR, strap), battery, and
  sensor announcements. A clean run announces each sensor at the start and end only, so
  0 reconnects. Count announcements per serial and source (BLE vs ANT+), minus those two;
  one strap on both radios shows twice. Its second serial isn't stable between runs, so
  don't identify the strap by serial.
- Size: a 1 Hz record stream returns several KB per record, so a whole run can close the
  connection. Ask only for the fields you need if the tool takes a field list; otherwise
  page with `message_limit` ≤400.

## Broken or tricky tool fields
- `get_vo2max_trend` has returned the cycling series with no sport selector; running
  VO2max is in `get_training_status`. Check which sport a series is before quoting it.
- Garmin's auto-detected lactate threshold from a treadmill run uses the watch's speed
  estimate, not belt speed: check the pace against the belt before adopting it.
- `get_lactate_threshold` speed: fixed on roac; values read before the fix were 1/raw and
  are not comparable. Check a new reading against the Connect app before updating
  `athlete.yaml`.
- `get_stats_range`: 28-day cap; today is partial; `bmr_calories` is RMR.
- Peloton `workouts_list`: interleaves Garmin-synced runs (`device_type garmin_connect`);
  `device_time_created_at` is local wall time; splits are pace-normalised.
- Completed scheduled workouts disappear from `get_scheduled_workouts`.

### garmin_mcp 30324f7 (live on roac 2026-10-13)
Don't compare values read before 2026-10-13 with values read after.
- `get_morning_training_readiness` returns the full readiness record (score, level, HRV,
  sleep, recovery); recovery time that has reached zero reads 0 h.
- `get_weekly_intensity_minutes` `total_minutes` = moderate + 2 × vigorous (Garmin's goal
  count), higher than before for the same week; raw moderate/vigorous still reported.
- `get_lactate_threshold` with a date range includes HR history; passing only one of
  start/end date is an error.
- Training status / load trend / load balance name the source device.
- Laps with impossible distance (e.g. 42,949,672 m, a wrapped 32-bit counter on treadmill
  laps) come back with no distance and `distance_invalid: true` in `get_activity_splits` and
  `get_activity_fit_data`: leave them out of distance and pace calculations.

## Units and time
- Everything shown to the athlete is in their unit (`athlete.yaml` →
  `preferences.distance_unit`), including Garmin/Peloton data (convert metres/km; show the
  conversion once). Races keep conventional names (5K, Half), never "a 3.1 mi race".
- `date:` = athlete-local civil date; instants = ISO 8601 with the local offset; compare
  instants as instants.

## Evidence hygiene
- Every number gets an as-of date and its source (tool + date range).
- Don't infer a trend from two endpoints: pull the interval.
- Separate heat from fitness before attributing an HR or pace change (outdoor heat inflates
  HR markedly in the warm months; see positions).
