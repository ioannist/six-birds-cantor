# Frontier Target Class v1

## Question being decided
After the witness search, what delayed-return local-domain class should the project actually try to prove next: a bounded-return delayed-gate subclass, a finite-state renewal local-domain subclass, or the broader countable-state delayed-return local-domain class?

## Witness candidates being frozen into the repo
- Primary witness: `frontier.fw_delayed_return_gate_a3` in [fw_delayed_return_gate_a3.json](/home/repos/six-birds-cantor/configs/experiments/frontier/fw_delayed_return_gate_a3.json). Best search-ranked delayed-return candidate; nonconstant observed return lengths `2,3,4,5` and induced alphabet growth `1,2,3,4` across the checked cap.
- Reserve witness: `frontier.fw_delayed_return_gate_a1` in [fw_delayed_return_gate_a1.json](/home/repos/six-birds-cantor/configs/experiments/frontier/fw_delayed_return_gate_a1.json). Same structural pattern as `a3`, slightly lower direct defects, useful as a robustness cross-check.
- Reserve witness: `frontier.fw_delayed_return_gate_a2` in [fw_delayed_return_gate_a2.json](/home/repos/six-birds-cantor/configs/experiments/frontier/fw_delayed_return_gate_a2.json). Same delayed-return shape, but stronger loop makes it the most likely candidate to drift back toward finite-state-renewal behavior if the cap is increased.

## Candidate frontier classes
1. `bounded_return_delayed_gate_subclass`
   Stationary local-domain families with an explicit delayed-return gate, bounded checked return lengths, no trivial induced size-1 collapse, and a finite return-block cap already visible in diagnostics.

2. `finite_state_renewal_local_domain_subclass`
   Local-domain families whose induced coding keeps nontrivial return blocks but still looks effectively finite-state renewal-like on the current cap.

3. `countable_state_delayed_return_local_domain_class`
   The stretch class where delayed-return induction supports genuinely countable-state/local-domain behavior rather than merely a bounded-return renewal picture.

## Selected working theorem class
- Working class: `bounded_return_delayed_gate_subclass`

Reason:
- The frozen witnesses do better than the old `contextual_local.domain_gated_two_map_local_ifs` baseline because induction no longer collapses to a one-symbol core.
- But current evidence is still finite-cap evidence: observed return lengths are bounded on the checked window, and the effective alphabet regime is still described by the search as `finite_state_renewal_like`.
- So the honest next theorem target is the narrow delayed-return class where the gating pattern is explicit and the bounded-return structure can be diagnosed mechanically from configs and induced data.

## Stretch class
- Stretch class: `countable_state_delayed_return_local_domain_class`

Reason:
- The delayed-return witnesses are the first local-domain candidates in the repo that produce growing induced return structure instead of immediate size-1 collapse.
- That is enough to keep the countable-state delayed-return route alive as the frontier ambition.
- It is not enough to make it the working class yet, because the search still reports `effective_alphabet_regime = finite_state_renewal_like` on the checked cap.

## Why this is better than the old domain-gated family
- `contextual_local.domain_gated_two_map_local_ifs` improved only by collapsing to a trivial finite-state induced core with return time `1` and induced alphabet size `1`.
- The new delayed-return witnesses retain nonconstant return lengths and induced alphabet growth under induction.
- That means the new family language is a better frontier target even before any proof work: it preserves nontrivial return-block structure instead of simplifying away the local-domain phenomenon.

## What still blocks a theorem
- The current evidence is still diagnostic, not structural proof: bounded return and induced growth are observed up to a finite cap, not proved uniformly.
- Induced truncation remains substantial, so any theorem route has to control how much mass is lost when passing to the delayed-return core.
- The cap-limited induced alphabet still looks close to finite-state renewal behavior, so the countable-state stretch claim is not yet ready to carry the proof program.

## Immediate next theorem task
- Build a delayed-return assumptions and diagnostics pack for the `bounded_return_delayed_gate_subclass`, with explicit tags for core interval choice, return-block admissibility, bounded return cap, and induced truncation control.
