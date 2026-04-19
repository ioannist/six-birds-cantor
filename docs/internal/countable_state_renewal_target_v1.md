# Countable-State Renewal Target v1

## Question being decided
After ID-T1, what induced theorem target should the project actually pursue: a trivial finite-state induced core, a finite-state renewal subclass, or a genuinely countable-state renewal/local-domain class?

## Evidence from ID-T1
- `contextual_local.domain_gated_two_map_local_ifs` improved strongly under induction.
- But the current induced core is a single recurrent component with return times bounded at `1` and induced alphabet size stabilizing at `1`.
- `toy.local_ifs.nested_three_map_local_ifs` also collapses to a one-symbol induced core, but with truncation loss too large to count as a credible frontier signal.
- The prefix-memory controls remain symbolic / finite-state after induction as expected.

## Candidate theorem classes
1. `finite_state_induced_core_subclass`
   Induction works, but only by collapsing to a small stationary finite-state core.

2. `finite_state_renewal_subclass`
   Induced coding uses return blocks / renewal structure, but still has finite effective alphabet or bounded return regime.

3. `countable_state_renewal_local_domain_class`
   Induced coding has genuinely nontrivial return structure / countable-state flavor and is not just a finite-state collapse.

## What counts as a genuine frontier target
For this project, a genuine frontier induced target must show more than defect improvement. It should exhibit nontrivial return structure: non-constant bounded returns, or growing return support, or an induced alphabet that does not collapse to size `1`. A one-symbol, one-step recurrent core is not enough.

## Decision
- Decision: `advance_finite_state_induced_only`
- Selected target class: `finite_state_induced_core_subclass`

Interpretation of `contextual_local.domain_gated_two_map_local_ifs`: `trivial_finite_state_collapse`.

The induced-core success is mathematically useful, but it is not yet a meaningful countable-state or renewal frontier signal. The current evidence says the route is worth studying only as a finite-state induced simplification, not as a genuine non-SFT/countable-state theorem target.

## Why the rejected targets are not the default now
- `finite_state_renewal_subclass` is not selected because the current target family does not show nontrivial return-time variation or a genuinely renewal-like induced alphabet; the observed return regime is constant `1`.
- `countable_state_renewal_local_domain_class` is rejected because no current family exhibits countable-state behavior, unbounded return candidates, or nontrivial induced alphabet growth after the induced-core construction.
