# Garmin writes: pointer workouts and side-effect checks

Garmin writes happen only when the athlete asks (or has approved the plan being pushed) in
the current conversation. Every write is followed by a read-back.

## Workout naming

- Prefix `EC W<week> <Day> - `, e.g. `EC W42 Mon - Peloton: 20 min Strength for Runners (Wilpers)`.
- **Front-load the meaning.** The watch names the recorded *activity* from the scheduled
  workout at 32 characters, so the first 32 characters must identify the session.
- `OPTIONAL` goes right after the day when the session is optional.

## Peloton pointer workouts

A pointer is a Garmin workout of the matching sport (cycling / strength_training /
running) with one timed step of the class length, whose description tells the athlete
which class to take. Starting it on the watch records the session.

Description format (plain text; Garmin doesn't render links, the athlete copies it):

```
[OPTIONAL - ...] PELOTON <class title>, <instructor> (aired <Mon D YYYY>): <URL> | WEIGHTS: <movement weight; ...> | <when / context> | Start this on the watch to record it.
```

URL: `https://members.onepeloton.com/classes/<cycling|strength|running|...>?modal=classDetailsModal&classId=<ride_id>`

Prerequisite: Peloton→Garmin sync must be **off** for that discipline, otherwise the class
arrives twice (Peloton copy + watch recording). Check coach-state `data-defects.md` for the
current sync settings before creating a pointer in a new discipline.

Upload shape (strength example; cycling = sportTypeId 2 "cycling", running = 1 "running"):

```json
{"workoutName": "...", "description": "...",
 "sportType": {"sportTypeId": 5, "sportTypeKey": "strength_training"},
 "estimatedDurationInSecs": 1200,
 "workoutSegments": [{"segmentOrder": 1,
   "sportType": {"sportTypeId": 5, "sportTypeKey": "strength_training"},
   "workoutSteps": [{"type": "ExecutableStepDTO", "stepOrder": 1,
     "stepType": {"stepTypeId": 3, "stepTypeKey": "interval"},
     "endCondition": {"conditionTypeId": 2, "conditionTypeKey": "time"},
     "endConditionValue": 1200}]}]}
```

Structured run workouts: repeat groups use `RepeatGroupDTO` with an `iterations` end
condition (`conditionTypeId` 7); HR targets per the `upload_workout` docstring. Read back
the repeat count after upload.

## Replacing a workout (there is no update call)

1. `get_workout_by_id(old)` — keep the wording you aren't changing.
2. `upload_workout(new)` → `get_workout_by_id(new)`: description intact?
3. `schedule_workout(new, date)` → `get_scheduled_workouts(date, date)`: new entry present.
4. `unschedule_workout(old scheduled_workout_id)` (calendar-entry id, not workout id),
   then `delete_workout(old)`.
5. Read back the whole affected range: exactly one entry per planned session, no
   duplicates.
6. Record new workout_id / scheduled_id and what it replaced (week file `garmin.workouts`
   in Claude Code; an `add_note` from chat).

## Side effects to check after any Garmin write

- Nutrition-settings writes have created a MANUAL weigh-in equal to the plan's starting
  weight: read body composition for the day afterwards; tell the athlete; delete only
  with their OK.
- New pointer disciplines: check for a Peloton-synced duplicate after the first session.
- Generally: re-read the adjacent data the write could touch, not just the object written.
- The first call after ~1 h idle may fail with an opaque "Error occurred during tool
  execution": read back before retrying a write, so a retry can't create a duplicate.
- Never HTML-escape names (`&` stays `&`).
