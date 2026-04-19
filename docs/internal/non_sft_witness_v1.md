# Non-SFT Witness v1

## Question being tested
Does the T19 Bowen-formula class `narrow_hybrid_affine_cylinder_class` already contain at least one family that is genuinely outside the paper's standard finite-state/SFT control setup?

## Relevant theorem class
The target class is the T19 class `narrow_hybrid_affine_cylinder_class`, not the reduced T20 thermodynamic core.

## Standard finite-state/SFT control setup being ruled out
For this project, a family counts as standard finite-state/SFT-like if there is a stationary finite-state symbolic presentation with finitely many continuation types / contexts that reproduces the admissible cylinders and the cylinder geometry used in the T19 theorem.

## Candidate families considered
- `contextual_local.domain_gated_two_map_local_ifs`
- `toy.local_ifs.nested_three_map_local_ifs`
- `contextual_local.prefix_memory_no_22_base3`
- `contextual_local.prefix_memory_last_digit_rule`

## Selected witness or blocker
- Decision: `impact_blocker_confirmed`
- Closest candidate: `contextual_local.prefix_memory_no_22_base3`

## Reason the witness is in-class
`contextual_local.prefix_memory_no_22_base3` is already included in `docs/internal/bowen_class_v1.json` and was the contextual witness used to justify the T19 theorem class. It satisfies the narrowed assumptions: finite-memory stationary admissibility, feedback-free geometry, exact cylinder packaging, and disjoint cylinder geometry.

## Reason the witness is not standard finite-state/SFT
No such witness was found. The closest in-class contextual family, `contextual_local.prefix_memory_no_22_base3`, has an explicit finite-state transition table with exactly two reachable continuation types (`0` and `2`), so it falls squarely inside the project's own excluded finite-state/SFT control setup rather than outside it.

The more genuinely local/domain-driven candidates do not rescue the claim:
- `contextual_local.domain_gated_two_map_local_ifs` is currently excluded from the T19 class.
- `toy.local_ifs.nested_three_map_local_ifs` is not claimed in the T19 class.
- `contextual_local.prefix_memory_last_digit_rule` remains excluded from the T19 class and is still bounded-memory symbolic in flavor anyway.

## Impact consequence
The current T19 Bowen-formula class does not yet supply a credible non-SFT witness. That is an impact blocker for claiming that the theorem is already beyond standard finite-state/SFT machinery. The right next move is to reopen or enlarge the Bowen class in a way that honestly brings a genuinely local/non-SFT family into the proved class.
