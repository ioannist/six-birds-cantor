# Quasimultiplicative Target v1

## What is being tested
Whether the current theorem program could replace packaging-coincidence by an almost-additive / bounded-bridge pressure route of the form
`|log Z_(n+m)(s) - log Z_n(s) - log Z_m(s)| <= C`
or a bounded-bridge variant.

## Candidate quasi-multiplicative class
Stationary finite-memory or local-domain families with bounded distortion and usable separation, where upper partition sums admit a bounded-defect concatenation law after at most a short bridge window.

## Defect metrics
- raw and normalized quasi-multiplicativity defects
- bounded-bridge defect with bridge window `B_max = 2`
- domain truncation defect `1 - Z_admissible / Z_formal`
- depth-stability summary from defect drift across the tested split set

## Families evaluated
- `classical.middle_thirds`
- `classical.restricted_digits_base5_024`
- `contextual_local.prefix_memory_no_22_base3`
- `contextual_local.prefix_memory_last_digit_rule`
- `contextual_local.domain_gated_two_map_local_ifs`
- `toy.local_ifs.nested_three_map_local_ifs`
- `finite_state.adjacency_no_consecutive_2_base3`

## Decision rule
Advance only if `contextual_local.domain_gated_two_map_local_ifs` is at least promising or strong inconclusive and at least one nontrivial local/contextual family beyond the symbolic controls looks plausibly quasi-multiplicative. Otherwise stop the branch.

## Initial recommendation
- Decision: `stop_qm_branch`

Reason: the key stress-test family `contextual_local.domain_gated_two_map_local_ifs` is `blocked` on the current diagnostic window. Its normalized defect is about `0.173`, its bridge defect is about `0.693`, and its domain truncation defect is about `0.992`. The clean controls behave as expected, but the domain-gated local family does not currently look bridgeable by a short bounded-bridge correction.

The assumptions held fixed from T15/T19/Bowen-v2 are the stationary finite-memory geometric assumptions already in the project; the new ingredient explored here is a bounded-bridge / almost-additive pressure law on upper partition sums. `contextual_local.domain_gated_two_map_local_ifs` is the key stress test because it is the simplest genuinely local-domain candidate near the frontier and therefore the first place where a true quasi-multiplicative rescue should succeed if the route is viable.
