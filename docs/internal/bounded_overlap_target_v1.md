# Bounded Overlap Target v1

## What is being tested
Whether the T19 coincidence step can be enlarged by replacing disjoint cylinder geometry with a bounded cylinder multiplicity hypothesis, so that literal equality of upper/lower sums is weakened to a bounded-ratio comparison.

## Candidate enlarged class
Finite-memory affine families satisfying the T19 fixed assumptions, plus exact cylinder packaging, but replacing `disjoint_cylinder_geometry` by a depth-uniform bounded cylinder multiplicity condition.

## Multiplicity notion
At depth `n`, let `M_n` be the maximum number of raw depth-`n` cylinder pieces covering any single point of the attractor approximation. The bounded-overlap route is plausible only if `M_n` appears uniformly bounded in `n` on the main candidate family.

## Ratio notion
At a family-level root proxy `s`, compute `R_n(s) = Z_n^U(s) / Z_n^L(s)` whenever both sides are defined. The overlap route is plausible if `R_n(s)` stays uniformly bounded across checked depths.

## Families evaluated
- `contextual_local.prefix_memory_last_digit_rule`
- `contextual_local.prefix_memory_no_22_base3`
- `contextual_local.domain_gated_two_map_local_ifs`
- `toy.local_ifs.nested_three_map_local_ifs`
- controls: `classical.middle_thirds`, `classical.restricted_digits_base5_024`

## Decision rule for the sprint
Advance to overlap lemmas only if `contextual_local.prefix_memory_last_digit_rule` looks at least promising and the bounded-overlap picture is not obviously false on the main candidate family. Stop otherwise.

## Initial recommendation
Advance to the overlap-lemma sprint.

Reason: `contextual_local.prefix_memory_last_digit_rule` shows depth-uniform overlap multiplicity `M_n = 2` on checked depths `[4, 6, 8, 10]`, with ratio proxies staying close to `1`. `contextual_local.prefix_memory_no_22_base3` behaves as the disjoint control, and `contextual_local.domain_gated_two_map_local_ifs` is not immediately obstructive. The nested three-map local-IFS toy is currently a blocker for this branch, but it is exploratory rather than the main target family.

The fixed assumptions from T15/T19 remain in force: finite memory, stationary admissibility, bounded distortion / affine control, feedback-free geometry, fixed lens/packaging, and lower-pressure packaging admissibility. The new ingredient that would need proof later is a geometric overlap-counting lemma yielding a depth-uniform multiplicity bound `M` for the enlarged class.
