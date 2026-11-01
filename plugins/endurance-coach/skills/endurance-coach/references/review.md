# Review before reply

The athlete's standing rule (coach-state positions, "Review before reply (tiered)"): nothing
is presented as fact until it has been reviewed. The review is tiered because latency
matters to him: the full pass is reserved for the claims that need it.

## Pick the tier

| The draft... | Tier |
|---|---|
| states a number you derived (sum, average, difference, rate, projection) | full |
| states a trend, comparison, cause or interpretation ("plateau", "drift", "faster than", "because of the heat") | full |
| makes an absence or negative claim ("no data", "not scheduled") | full |
| quotes one retrieved value with its source and as-of date, or a plan value from the plan | quick |
| only asks a clarifying question, or is chit-chat | none |

One full-tier claim makes the whole reply full tier. An interpretive extra nobody asked
for meets the full bar or gets cut.

## Quick self-check

Against the tool output itself (not your memory of it): the value, its unit (converted to
`preferences.distance_unit`), its date, and which tool it came from. Then reply.

## Full review

1. **Draft** the reply, then list its claims one per line: every number, comparison,
   trend, cause and negative claim.
2. **Reviewer.** If an agent or subagent tool is available, give a fresh reviewer only:
   - the athlete's question, verbatim;
   - the draft and its claims list;
   - the raw tool outputs the claims rest on (the returned data, not your reasoning
     about it), with the tool names and date ranges;
   - the brief below.
   If no agent tool is available (claude.ai chat), do the pass yourself as a separate
   step. Re-read the raw outputs, re-derive each claim from them, and say in the reply
   that it was a self-review.
3. **Act on the verdicts.** Fix or drop every claim that fails, and re-review a fix if it
   changes a number. Never send a failed claim with a hedge attached.
4. Record anything the review caught that a later session could repeat as a retraction
   or a trap at the next reconcile.

## Reviewer brief

> You are checking a coaching reply before the athlete sees it. Assume it is wrong
> until the data shows otherwise. For each listed claim:
> 1. Re-derive it from the raw tool outputs only. Show the arithmetic.
> 2. Check it against coach-state positions and traps (search_positions, get_today
>    traps) and data-defects: a claim that contradicts a settled position or trap fails.
> 3. Try to falsify it: a missing date range, a truncated or filtered query, a unit or
>    timezone slip, the wrong power scale, heat or a deficit as an alternative cause,
>    two endpoints standing in for a trend, a manual or post-run weigh-in.
> 4. Verdict per claim: PASS, FAIL (why, plus the corrected value if derivable) or
>    UNSUPPORTED (no data given for it).
> Also flag any interpretive word ("plateau", "trend", "stalled") the data doesn't
> carry, and any claim in the draft missing from the list.
