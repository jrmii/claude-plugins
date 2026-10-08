# Nutrition: targets, meal logging, recommendations

Garmin's `calorieGoal` is written by us to match the coach-state target. The Garmin plan's
`weightChangeType`, `weightChangeRate` and `targetWeightGoal` are stale metadata (the API
can't change them): never compute a deficit from them.

Targets (calories, protein, deficit phases) are decisions in coach-state: read
`constraints.yaml` (current deficit phase) and `search_positions("nutrition")` /
`search_positions("protein")`. The Garmin nutrition plan's own macro split is a single
scalar on a fixed ratio; use the coach-state protein target, not Garmin's.

## Logging a meal
1. Identify each item and portion; estimate macros explicitly (show per-item numbers).
2. Prefer existing custom foods (`get_custom_foods`) so repeats stay consistent; restaurant
   items are custom foods with `brandName` = restaurant.
3. Log with intentional timestamps: Garmin buckets meals by time window (breakfast, lunch,
   dinner, snacks), so pick a time inside the intended meal's window.
4. Plain characters in names (`&`, not `&amp;`); pass every field explicitly on updates.
5. Read back the day (`get_nutrition_daily_food_log`) and give the running totals vs target.
- Logged rows copy values at log time; editing a custom food later never changes history.

## Recommending where or what to eat
1. **First pull the last ~2 weeks of food logs** (and custom foods): recent restaurants,
   rotation, what was eaten yesterday. Don't recommend last night's restaurant.
2. Ask distance and company if not obvious (solo vs family changes the answer).
3. Fit the remaining macros for the day (show the arithmetic), and the athlete's intent:
   "a treat while staying responsible" is a valid target, not something to talk down.
4. Verify menu facts (portion sizes, protein per dish) before comparing options.

## Energy balance
- Use run calories and Assioma kJ (≈ kcal) for rides; never Peloton-device or
  strength/stretch calories (inflated).
- Exclude partially logged days (low item counts) before averaging intake.
- Weight trend from Index-scale readings only (references/data.md).
