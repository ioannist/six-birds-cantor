# External Witness Import v1

## Question
Which external literature-backed family should replace the blocked in-repo redesign language as the next theorem target?

## External source families examined
- Foundations of local iterated function systems (arXiv:2601.07804): Gives the repo-language bridge: local admissibility, extended shift, and examples not modeled by SFT.
- The dimension spectrum of graph directed Markov systems (arXiv:1802.01125): Countable-state GDMS with topological pressure estimates and explicit countable alphabet dynamics.
- Hausdorff dimension of Kuperberg minimal sets (arXiv:1801.04034): Pseudo-Markov system over a countable alphabet, a genuine step beyond finite-state renewal-like control.
- Geometry of measures in random systems with complete connections (arXiv:2202.07335): Countable conformal IFS with overlaps and exact dimensional stationary measures, useful as a geometric pressure target.

## What counts as a usable imported witness
- It must be beyond finite-state-renewal-like control in the theorem-relevant sense.
- It must be concrete enough to anchor a repo-ready candidate family or config skeleton.
- It must be materially better than the closed delayed-return branch, which is theorem-closed but still finite-state-renewal-like on audit.

## Top imported candidates
- `external.countable_gdms_countable_alphabet` from `countable_gdms_dimension_spectrum`: `promising`; countable-state signal `strong`, local-domain signal `medium`, route fit `countable_state_pressure`.
- `external.pseudo_markov_countable_alphabet` from `kuperberg_pseudomarkov_minimal_sets`: `promising`; countable-state signal `strong`, local-domain signal `medium`, route fit `countable_state_pressure`.
- `external.local_ifs_non_sft_bridge` from `local_ifs_foundations`: `promising`; countable-state signal `medium`, local-domain signal `strong`, route fit `bounded_overlap`.

## Why they are better than current in-repo families
- The current delayed-return package is closed but finite-state-renewal-like only.
- The imported countable-GDMS and pseudo-Markov candidates are explicitly countable-alphabet systems, so they are not trapped in the finite-state-renewal regime.
- The local IFS bridge is the best repo-language anchor because it keeps the admissible-composition viewpoint while escaping the old toy redesign collapses.

## Decision
- `external_witness_imported`

## Next theorem branch enabled
- A countable-state pressure / local-domain bridge branch anchored in an imported witness family.
