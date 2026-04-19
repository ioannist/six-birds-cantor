# Frontier Witness Search v1

## Question
Can a small stationary local-domain search family beat `contextual_local.domain_gated_two_map_local_ifs` by keeping a nontrivial induced return-block structure instead of collapsing to a size-1 finite-state core?

## Templates searched
- Template A: delayed-return domain-gated families with one exit, one holding branch, and one return branch.
- Template B: three-map gated renewal families with two exits from the core into a shared waiting region.
- Template C: nested-domain ladder families with a two-stage waiting hierarchy before return.

## Best candidates
- `fw.delayed_return_gate_a3`: `promising`; induced core `countable_state_candidate`, return regime `growing_but_tight`, effective alphabet regime `finite_state_renewal_like`.
- `fw.delayed_return_gate_a1`: `promising`; induced core `countable_state_candidate`, return regime `growing_but_tight`, effective alphabet regime `finite_state_renewal_like`.
- `fw.delayed_return_gate_a2`: `promising`; induced core `countable_state_candidate`, return regime `growing_but_tight`, effective alphabet regime `finite_state_renewal_like`.

## What failed
- The nested-ladder candidates kept hierarchical return words, but induced truncation stayed too large to treat them as clean next targets.
- The three-map renewal candidates improved on the old domain-gated baseline, but they still read more like finite-state renewal systems than a genuinely new local-domain frontier class.

## Decision
- `promising_frontier_witness_found`

## Why this is or is not a real frontier signal
- Yes, we found candidates better than the current `domain_gated_two_map_local_ifs` baseline: the delayed-return designs no longer collapse to a trivial induced size-1 core.
- The best candidates are not merely the old finite-state collapse in disguise; they show nonconstant return lengths and induced alphabet growth across the checked cap.
- The best signal is still exploratory rather than finished theory. The induced alphabet currently behaves like a plausible countable-state/local-domain target, but the observed finite-cap alphabet regime is still close enough to finite-state renewal behavior that a formal target class needs careful wording.

## Recommended next theorem branch
- `FW-T2 — Formalize the new frontier target class`
