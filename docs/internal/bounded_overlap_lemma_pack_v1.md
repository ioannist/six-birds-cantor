> Historical proof proposal, superseded by the [2026-10-01 mathematical review](mathematics_review_2026_10_01.md). Closure labels below are workflow provenance, not mathematical certification. Consult the review and restoration notes for valid statements and outstanding hypotheses.

# Bounded Overlap Lemma Pack v1

## Target subclass
- Subclass ID: `bounded_overlap_equal_scale_prefix_memory_subclass`
- Concrete subclass handled here: stationary finite-memory affine equal-scale digit families with exact cylinder packaging, usable separation, bounded cylinder multiplicity, and no runtime lens/packaging feedback into admissibility.
- In practice this covers the bounded-memory prefix families with base-`b` digit cylinders, where every depth-`n` cylinder has diameter exactly `b^{-n}` and the lower-side packaged family is the coalesced union of those same depth-`n` cylinders.

## Witness families
- `contextual_local.prefix_memory_last_digit_rule`
- `contextual_local.prefix_memory_no_22_base3`
- `classical.middle_thirds`

Diagnostic support from S1-T1:
- `contextual_local.prefix_memory_last_digit_rule`: `M_n = 2` on checked depths `4, 6, 8, 10`, ratio proxy about `1.15–1.21`.
- `contextual_local.prefix_memory_no_22_base3`: disjoint control with `M_n = 1` and ratio proxy `~1`.
- `classical.middle_thirds`: classical disjoint control with `M_n = 1` and ratio proxy `~1`.

## Multiplicity notion
For each depth `n`, let `C_n` be the raw depth-`n` cylinder family and let `U_n` be the packaged/coalesced depth-`n` interval family. Define
`M_n = sup_x # {I in C_n : x in I}`.
The overlap hypothesis for this subclass is that there exists `M < infinity` with `M_n <= M` for all depths `n`.

## Main bounded-overlap theoremlet
For the subclass `bounded_overlap_equal_scale_prefix_memory_subclass`, the T19 coincidence step can be replaced by bounded-ratio coincidence: there exists `M < infinity` such that for every depth `n` and every `s >= 0`,
`Z_n^L(s) <= Z_n^U(s) <= M Z_n^L(s)`.
Consequently the upper and lower pressures agree,
`P^L(s) = P^U(s)`,
and the T19 Bowen-formula conclusion goes through on this enlarged subclass.

## Proof route
1. Use the digit-transition finite-memory description to reduce overlap patterns to finitely many continuation types.
2. Use stationarity of admissibility to show those overlap patterns do not proliferate with depth: the same finite set of local overlap configurations repeats at each scale.
3. Use affine equal-scale geometry to note that every depth-`n` cylinder contributing to a given packaged interval has the same diameter `b^{-n}`.
4. Use usable separation to rule out overlap cascades from geometrically remote cylinders: any overlap can only come from a bounded neighborhood of continuation types.
5. Conclude a depth-uniform multiplicity bound `M_n <= M`.
6. For each packaged interval `J` in `U_n`, the sum of `|I|^s` over cylinders `I` contributing to `J` is at most `M |J|^s`, while the lower sum counts `|J|^s` once. Summing over `J` gives the bounded-ratio lemma.
7. Divide `log Z_n^U - log Z_n^L` by `n`, use `log M / n -> 0`, and obtain pressure coincidence.

## Where multiplicity comes from
- `finite_memory_bound`: gives only finitely many continuation types / last-symbol contexts, so only finitely many local overlap templates need be controlled.
- `stationary_admissibility_rule`: guarantees those templates recur identically across depths instead of changing with stage.
- `equal_scale_cylinders`: at fixed depth all cylinders have the same geometric scale, so overlap counting is purely multiplicity counting and does not mix sizes.
- `usable_separation`: prevents a cylinder from overlapping an unbounded cascade of far-away cylinders; overlap can only occur among a bounded set of neighboring templates.
- `exact_cylinder_packaging`: ensures the lower object is the coalesced family generated from the same depth-`n` cylinders, so the multiplicity estimate compares the right two sums.

## What this changes in the T19 coincidence step
T19 used literal equality `Z_n^L = Z_n^U` on the disjoint-cylinder subclass. On the present subclass, that equality is replaced by the bounded-ratio estimate
`Z_n^L <= Z_n^U <= M Z_n^L`.
This is enough because the pressure is defined after dividing by depth: the bounded multiplicative constant disappears in the limit, so the coincidence theorem still closes.

## Outside the subclass
This theoremlet does not cover:
- stage-dependent / nonstationary admissibility;
- feedback families where lens or packaging affects admissibility;
- local-domain families without equal-scale cylinders;
- local-domain families where overlap can cascade through geometry instead of being controlled by finitely many symbolic continuation types.

In particular, `contextual_local.domain_gated_two_map_local_ifs` remains outside this lemma pack. The overlap diagnostics did not obstruct it immediately, but the current proof route here depends on equal-scale symbolic cylinder geometry, not general domain-gated local-IFS geometry.
