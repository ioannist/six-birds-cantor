# Delayed-Return Theorem Assumptions v1

## Target class
- Working class: `bounded_return_delayed_gate_subclass`
- Stretch comparison class: `countable_state_delayed_return_local_domain_class`

## Why this is different from the old domain-gated family
- The old `contextual_local.domain_gated_two_map_local_ifs` only became tractable after induction by collapsing to a size-1 core with constant return time `1`.
- The frozen delayed-return witnesses keep explicit gate/hold/return structure, nonconstant observed return lengths, and nontrivial induced alphabet growth on the checked cap.
- So the working class is built around delayed-return structure that survives induction instead of disappearing under it.

## Objects
- **Delayed-return core** `C`: the explicit source interval from which the gate branches leave the core and to which the return branch re-enters.
- **Return block**: a first-return word `w` whose image sends `C` back into `C`, with no earlier prefix already returning.
- **Induced alphabet**: the set of return blocks used in the induced coding on `C`.
- **Bridge proxy**: the finite-cap defect proxy checking whether induced return blocks compose with bounded logarithmic loss.

## Assumptions
- `delayed_return_core_exists`: an explicit core interval and gate/hold/return decomposition can be read off from the family.
- `bounded_return_times`: first-return lengths stay within a finite checked cap and do not collapse to a single trivial return.
- `stationary_local_admissibility`: map domains and admissibility law are fixed in time.
- `local_domain_compatibility`: return blocks respect the local domains strongly enough to define an induced coding on the chosen core.
- `induced_alphabet_control`: induced alphabet growth is controlled on the checked cap and does not explode immediately.
- `bounded_bridge_property`: induced return blocks show a bounded-bridge / concatenation proxy compatible with a pressure argument.
- `usable_overlap_control`: overlap/packaging behavior is controlled well enough that the induced return coding is meaningful.
- `feedback_free_admissibility`: no runtime protocol/lens/packaging feedback changes admissibility.
- `strict_return_contraction`: each return block contracts strictly, so induced weights decay as `s` increases.
- `core_return_coverage`: the induced core captures a nontrivial, theorem-relevant portion of the branch mass.
- `full_core_induction`: every surviving branch is represented by the delayed-return core up to uniformly bounded entry/exit correction.
- `uniform_entry_exit_bound`: the entry/exit correction lengths are uniformly bounded across the class.
- `nontrivial_induced_structure`: the induced system is not a size-1 trivial collapse.

## Witness families
- `frontier.fw_delayed_return_gate_a3`: primary witness; best current delayed-return candidate.
- `frontier.fw_delayed_return_gate_a1`: reserve witness with the same structure and slightly milder scaling.
- `frontier.fw_delayed_return_gate_a2`: reserve/stress witness with stronger holding behavior.
- Comparison tags:
  - `contextual_local.domain_gated_two_map_local_ifs`
  - `contextual_local.prefix_memory_no_22_base3`

## Failure modes
- Trivial induced collapse: size-1 induced core or constant one-step return only.
- Excess truncation: the induced core loses too much mass to carry a theorem.
- Bridge failure: concatenation compatibility looks good only for isolated return words, not uniformly.
- Fake frontier signal: induced alphabet growth is visible only because the cap is short, while the regime is still effectively finite-state renewal-like.

## What would still be needed for a theorem
- A structural argument that the delayed-return core and first-return coding exist uniformly for the class, not just on the frozen witnesses.
- A real bounded-return or bounded-tail theorem input replacing the finite-cap observation.
- A proof-quality bridge/concatenation lemma on return blocks.
- A clean statement of how induced truncation is controlled strongly enough for pressure transfer.
- A final decision on whether the working class remains finite-state-renewal-like or genuinely widens beyond it.
