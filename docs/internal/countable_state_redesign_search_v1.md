# Countable-State Redesign Search v1

## Question
Can a new stationary local-domain witness family beat the delayed-return branch, meaning: avoid finite-state-renewal collapse and keep induced return structure genuinely expanding?

## Templates searched
- Template A: ladder-gate families with nested waiting windows and multiple return branches.
- Template B: reset-and-hold families with a buffer region and a distinct reset map.
- Template C: multi-return three-map families with two return itineraries back to the core.
- Template D: stacked window families with several admissibility windows before return.

## Best candidates
- `cs.reset_hold_b2` (reset_and_hold): `blocked`; induced core `trivial_finite_state`, return regime `bounded_constant`, alphabet regime `unknown`.
- `cs.reset_hold_b1` (reset_and_hold): `blocked`; induced core `trivial_finite_state`, return regime `bounded_constant`, alphabet regime `unknown`.
- `cs.multi_return_c2` (multi_return_three_map): `blocked`; induced core `trivial_finite_state`, return regime `unknown`, alphabet regime `unknown`.

## Why the delayed-return witnesses are no longer enough
- They closed as a theorem package, but the audit said they still looked finite-state renewal-like.
- The new search must therefore look for induced return structure that does not collapse so quickly.

## Decision
- `design_space_blocked`

## What kind of theorem branch this supports next
- The small template language did not produce a credible next witness.
- A different family language or an imported external witness family is needed before more theorem work.

The main distinction is whether the induced coding keeps growing in a way that resists finite-state compression on the checked cap.
