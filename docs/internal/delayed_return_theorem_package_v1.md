# Delayed-Return Theorem Package v1

## Final theorem statement
For `K` in `bounded_return_full_core_delayed_gate_subclass`,
\[
\dim_H K = s_* \quad \text{where } P_{\mathrm{ind}}(s_*) = 0.
\]

This package freezes the closed delayed-return theorem branch. The pressure side and the lower-transfer side are both closed in the note/package sense, but only after narrowing from the broader delayed-return working class to the full-core closure class.

## Closed class
- `bounded_return_full_core_delayed_gate_subclass`

## Selected routes
- Lower route: `induced_cylinder_premeasure`
- Pressure route: induced return-block pressure / induced Bowen root

## Proof dependencies used
- `docs/internal/proof_dependency_induced_pressure_v1.json`
- `docs/internal/proof_dependency_lower_transfer_v1.json`
- `docs/internal/proof_dependency_delayed_return_v1.json`
- `docs/internal/delayed_return_theorem_assumptions_v1.json`

## Assumptions used
- `delayed_return_core_exists`
- `bounded_return_times`
- `stationary_local_admissibility`
- `local_domain_compatibility`
- `induced_alphabet_control`
- `bounded_bridge_property`
- `feedback_free_admissibility`
- `core_return_coverage`
- `nontrivial_induced_structure`
- `strict_return_contraction`
- `full_core_induction`
- `uniform_entry_exit_bound`
- `usable_overlap_control`

## Witness families
- `frontier.fw_delayed_return_gate_a3`
- `frontier.fw_delayed_return_gate_a1`
- `frontier.fw_delayed_return_gate_a2`

## Included families
- `frontier.fw_delayed_return_gate_a3`
- `frontier.fw_delayed_return_gate_a1`
- `frontier.fw_delayed_return_gate_a2`

## Excluded families
- `contextual_local.domain_gated_two_map_local_ifs`
- `contextual_local.prefix_memory_last_digit_rule`
- `contextual_local.prefix_memory_no_22_base3`

## Not claimed families
- `countable_state_delayed_return_local_domain_class`
- the broader `bounded_return_delayed_gate_subclass` before narrowing

## Proof status
- `closed_in_note`

## Notes
- The theorem is closed on the narrowed full-core delayed-gate subclass, not on the broader working class.
- The package is useful, but the class is still the sort of thing that can be encoded as a finite-state renewal-like control model on the supported witnesses.
