# Strength: selection, prescription, check-in, progression

Placement rules (how many per week, which days, relation to the long run) are standing
decisions: read them with `search_positions("strength")`. Equipment is in coach-state
`athlete.yaml` → `equipment` (home dumbbells; travel lodging in `constraints.yaml`).

## Selecting a Peloton class

1. Candidates: `classes_filters(browse_category="strength")` gives class-type IDs
   (Bodyweight, Core, Upper Body, Lower Body, Full Body, Strength for Sport...).
   `classes_search(browse_category="strength", content_format="video", class_type_id=...,
   duration=<seconds>, has_workout=false)` lists untaken classes.
   `has_workout` is tri-state: omitted ≠ false.
2. **Inspect the structure of every candidate before picking.** The full response exceeds
   the tool budget; always narrow it:
   `classes_structure(ride_id, select="ride.title,ride.duration,segments.segment_list.name,segments.segment_list.length,segments.segment_list.subsegments_v2.display_name,segments.segment_list.subsegments_v2.length")`
3. Classify the work: seconds of single-leg lower body, bilateral lower body, upper push,
   upper pull, core; any jumping; floor space needed.
4. Fit to the day:
   - Day after a long run: upper/core, light legs.
   - Within ~48 h before a long run: cap lower-body load (first leg session after a layoff
     → bodyweight or light). Never the day before the long run.
   - Travel/small rooms: no jumping, mat-sized footprint, bodyweight.
5. Interval format matters: 20 s on / 10 s off is conditioning; for building muscle
   (progressive overload) prefer longer sets or rep-based work where heavier weights are
   usable. Repeating a known class with heavier weights measures progress better than
   always picking a new class.
6. Record why: structure summary, why it fits the day, and rejected candidates with the
   reason. Peloton zone or score figures quoted from a class are Peloton-scale targets:
   tag them (`why_scale`).

## Prescription (required for every strength assignment)

- A weight for **every movement**, from the athlete's actual equipment ("bodyweight" is a
  prescription). Per hand for paired dumbbells; say "goblet" for a single dumbbell.
- Include the escape hatch: when to drop to bodyweight or a lighter weight (form, joint
  complaint, residual soreness).
- Include the progression trigger for next time (e.g. "if all sets feel RPE ≤ 6, next
  weight step").
- Put it in the week file's peloton pick as `prescription:` (Claude Code), and in the
  Garmin pointer workout description (references/garmin-writes.md).

## Check-in (after every strength session)

Ask, conversationally, one at a time if needed:
1. Did you use the prescribed weights, or adapt (heavier, lighter, bodyweight, fewer reps,
   skipped a movement)?
2. How did it feel: overall RPE 1–10, hardest movement, any pain or niggle?
3. Next morning: any soreness, and where?

Record the answers with `add_note` (date = session date). They set the next prescription.

## Progression rules of thumb

- All sets RPE ≤ 6 with clean form → next dumbbell step for that movement next time.
- Adapted down, pain, or soreness lasting into the next key run → hold or reduce.
- Change one variable at a time (weight *or* class), so the check-in is interpretable.
- Exercise sets recorded by the watch (`get_activity_exercise_sets`) can confirm reps and
  weights when the athlete logs them.
