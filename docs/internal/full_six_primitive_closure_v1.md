# Full Six Primitive Closure v1

## What was wrong with the previous target choice
- We treated `generated.pg_protocol_lens` as a theorem anchor even though it never activated all six primitives.
- We also let `generated.pg_rewrite_bundle` stand in as a working target before P5 was forced to be a producer consumed by both rewrite and gating.
- The old version made P5 too close to reporting.

## Hard closure criterion
- No working target is allowed unless P1, P2, P3, P4, P5, and P6 are all causally active in the same substrate loop.
- If removing any one primitive leaves the lawful substrate essentially unchanged, that primitive is not active enough for the theorem branch.

## What counts as an active primitive in Cantor substrate generation
- A primitive is active only if changing or removing it changes the next-step lawful substrate in a mathematically relevant way.
- “Mathematically relevant” means more than a cosmetic label or summary field.
- The primitive must affect the lawful update path, not merely record it.

## Why P5 must be causally active, not observational
- P5 is packaging, so it must control which grouped return blocks survive into the next step.
- If P5 only stores summaries, then the substrate still lives on without it.
- That would be a partial-loop substrate, not a six-birds loop.

## Knockout rule
- Run the full bundle and six leave-one-primitive-out ablations.
- If a knockout leaves the stable family and induced structure essentially intact, that primitive is not causally closed.
- A six-birds target needs at least one knockout, ideally the P5 knockout, to break the loop materially.

## Revised working-target selection rule
- Only a full-loop substrate with causal P5 may be a working target.
- `generated.pg_protocol_lens` is control-only.
- `generated.pg_rewrite_bundle` is the working target only after P5 is upgraded into a producer/selector that drives P1 and P2.
- If P5 remains observational, no six-birds working target is selected.
