# Corrected comparison for coalesced equal-scale cylinders

This note corrects Step 6 of `bounded_overlap_lemma_pack_v1.md`. It is a
mathematical repair, not an enlargement of the paper's main theorem class.

Pointwise overlap multiplicity does not bound the number of cylinders in a
connected coalesced component. For example, the N intervals
`[j/N,(j+1)/N]`, `0 <= j < N`, have pointwise multiplicity at most two,
but coalesce to one interval. Their raw sum is `N^(1-s)` and their
coalesced sum is one. Neither the claimed depth-independent comparison
nor its claimed direction for every `s >= 0` follows from multiplicity.

For distinct base-b digit cylinders of length `h=b^(-n)`, use instead the
hypothesis that each coalesced component contains at most L consecutive
grid cells, uniformly in n. A component consisting of k cells contributes
`k h^s` to the raw sum and `(k h)^s` to the coalesced sum. Their ratio is
`k^(1-s)`. Thus, for every fixed `s >= 0`,

```
L^(-|1-s|) Z_n^L(s) <= Z_n^U(s) <= L^(|1-s|) Z_n^L(s).
```

For `0 <= s <= 1` one can sharpen this to
`Z_n^L <= Z_n^U <= L^(1-s) Z_n^L`. For `s > 1` the first inequality
reverses. Taking logarithms and dividing by n gives equality of the
limsup pressures. This comparison alone supplies neither a lower
Hausdorff bound nor a consistent limiting measure.

The listed digit witnesses retain pressure coincidence. Their stationary
transition rules omit at least one of the b next digits for every parent.
For `n >= 2`, every block of b sibling grid cells therefore contains a
missing cell. A consecutive run cannot cross three parent blocks, since
the middle one would have to be full. Hence its length is at most
`2(b-1)`. At `n=1` it is at most b. The bound
`L=max(b,2(b-1))` works at every depth. In particular L=4 suffices for
`prefix_memory_last_digit_rule` and `prefix_memory_no_22_base3` in base
three. The classical separated-digit controls have the same property.

This proof uses distinct digit cylinders and exact grid adjacency. A float
coalescer with a fixed additive EPS can merge actual gaps once h becomes
smaller than EPS. Such finite computations cannot establish the
all-depth theorem. General overlapping cylinders require separate
component-size and geometry hypotheses; pointwise multiplicity alone
remains insufficient.
