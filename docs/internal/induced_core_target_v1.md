# Induced Core Target v1

## What is being tested
Whether the blocked direct coding for `contextual_local.domain_gated_two_map_local_ifs` becomes viable after passing to an explicit induced core / return-block coding.

## Candidate induced-core route
Choose a conservative recurrent core `C`, define first-return blocks up to cap `L_max = 4`, and compare original versus induced quasi-multiplicative / bridge defects. The route is viable only if induction materially repairs the defect picture without catastrophic mass loss.

## Core set / return-block definition
In this repo, an induced core is an explicit recurrent component selected from the family dynamics. A return block is a finite word whose image sends the core back into itself in the selected return sense. For the local-IFS target family, the implemented induced core is the highest-mass recurrent one-step image component; for the symbolic controls, the induced core is the recurrent symbolic core itself.

## Diagnostics
- original normalized QM defect and bridge defect
- induced normalized QM defect and bridge defect
- induced truncation defect
- return-time summary
- induced alphabet growth summary

## Families evaluated
- `contextual_local.domain_gated_two_map_local_ifs`
- `toy.local_ifs.nested_three_map_local_ifs`
- `contextual_local.prefix_memory_no_22_base3`
- `classical.middle_thirds`
- `contextual_local.prefix_memory_last_digit_rule`

## Decision rule
Advance only if `contextual_local.domain_gated_two_map_local_ifs` is at least promising and induction clearly improves the defect picture relative to the original coding.

## Initial recommendation
- Decision: `advance_to_induced_pressure`

Reason: the target family is `promising` after induction. Its original normalized QM defect is about `0.173`, while the induced defect drops to about `1.388e-17`. Its original bridge defect is about `0.693`, while the induced bridge defect drops to about `1.110e-16`. The retained-core loss is a constant-factor truncation defect of `0.5`, not an exploding loss, and return times stay bounded at `1` on the checked cap.

`contextual_local.domain_gated_two_map_local_ifs` is the key target because it was the first genuinely local-domain family blocked by the direct QM route. If induction regularizes it enough, that points to a different frontier theorem architecture than the failed direct packaging-based route.
