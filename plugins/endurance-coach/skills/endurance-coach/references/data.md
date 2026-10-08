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
- Peloton-device calories (~1.8–2×) and Garmin strength/stretch calories (~1.5–2×) are
  inflated: never use them for energy balance or "eating back". Run calories are credible.

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
- The watch truncates activity names created from workouts at 32 characters.
- Late uploads happen: a day isn't complete until the device's last upload is after it.

## Readiness inputs
- Wake readiness = the `AFTER_WAKEUP_RESET` entry of `get_training_readiness`.
- HRV: single nights are noisy; use status + weekly average (`get_hrv_trend`).
- A low sleep score with a known logistics cause (late pickup, travel) is not a recovery
  signal: check notes.

## Broken or tricky tool fields
- `get_lactate_threshold` speed: wrong (1/raw instead of raw×10, inverts trends) until the
  upstream fix is on roac. Take LT pace from the Connect app (`athlete.yaml`); LT HR is fine.
- `get_stats_range`: 28-day cap; today is partial; `bmr_calories` is RMR.
- Peloton `workouts_list`: interleaves Garmin-synced runs (`device_type garmin_connect`);
  `device_time_created_at` is local wall time; splits are pace-normalised.
- Completed scheduled workouts disappear from `get_scheduled_workouts`.

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
