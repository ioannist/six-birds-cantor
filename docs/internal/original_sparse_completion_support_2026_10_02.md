# Original sparse completion and full-history conditioning support

This pass repairs a missing applicability step for the original completion
operators. It does not change the outer update, add kernel minorization, alter
the path potential, or edit the paper. It also strengthens the pressure
obstruction from frozen matrices to the actual nonautonomous history form.
The original four-theorem package is **not complete**.

## Why the positive-kernel argument did not cover the original pilot

A fresh replay with the original configurations and `kernel_minorization=0`
finds zero kernel entries in 988 of the 1000 original 16-state steps and 12
of the 600 original 20-state steps. The final 16-state kernel still has zeros;
the final 20-state kernel has minimum entry about `0.005259550855364394`.
These are floating replay facts, not an all-time theorem.

Thus strict positivity of every original one-step kernel cannot simply be
imported from the optional repaired variant. For the 16-state singleton-cell
completion, E itself has zeros. Its square has a positive floor, so the correct
argument uses a contractive BLOCK of steps.

## Constructed stationary existence and primitive saturation

Let M be any finite nonnegative stochastic matrix. Assume some finite power
`M^m` has every entry positive, with `m>0`. Let

```
epsilon = min_ij (M^m)_ij > 0,
c = 1-d epsilon,  0 <= c < 1.
```

The old positive-operator formalization required a checked stationary vector
as an input. `PrimitiveCompletion.lean` now derives existence:

1. Start from the uniform probability vector u and iterate the positive block
   `N=M^m`. Differences of equal-mass vectors contract in l1 by c.
2. Successive increments obey
   `||u N^(n+1)-u N^n||_1 <= c^n ||u N-u||_1`.
3. The geometric bound makes every coordinate a Cauchy sequence. Completeness
   of the reals supplies a limit p. Finite sums and the linear update commute
   with these limits, giving mass one and `p N=p`.
4. Positivity gives `p_j >= epsilon`. The stationary vector of N is unique.
5. N commutes with M. Therefore p M is another mass-one stationary vector of
   N, and uniqueness forces `p M=p`.

The full-iteration estimate is

```
||mu M^n-p||_1 <= c^floor(n/m) ||mu-p||_1.
```

Its remainder steps use nonexpansiveness of stochastic M. A convergent block
subsequence alone would not establish full convergence; this step is included
in the mechanization. Hence EVERY real mass-one initial vector converges to
the same p. The probability simplex is included, without finite-start sampling.

The rank-one limiting closure C with rows p satisfies `C^2=C`, `M C=C`,
`C M=C`. Lean derives these properties from constructed saturation. It does
not assert that the one-step M is idempotent.

Principal exports are `positive_completion_stationary_exists`,
`primitive_completion_saturates`, `primitive_completion_unique`,
`primitive_completion_error`, and `primitive_completion_idempotent_limit`.
All these live in namespace `CantorAudit`.

## Return to the actual B Q U constructor

For the actual lazy transport B and block-prototype lift U, the completion is
E=B U. If every finite informant coordinate is positive, then U has positive
diagonal entries. Write `beta=min_j U_jj>0`. Nonnegativity gives

```
E_ij >= B_ij U_jj >= beta B_ij,
(E^m)_ij >= beta^m (B^m)_ij.
```

Thus primitive transport implies primitive completion. This return is proved
in `primitive_transport_completion_saturates`; it does not assume a
stationary completion object or convergence as a premise.

The finite informant starts uniformly. If each kernel column has a positive
entry, then every finite iterate is strictly positive: in each new coordinate
there is a positive summand. Any early stop among those iterates preserves
this property. Lean proves this as `completionIterate_positive_columns`.
The `.55` finite-informant term then makes every prototype weight positive.
The support and diagonal terms are nonnegative. Any nonempty partition has a
stochastic, nonnegative lift with positive diagonal. This works for the actual
finite estimate; no exact-stationary substitution has been introduced.

## Exact support witnesses on the original recorded snapshots

`completion_support.py` constructs finite paths in the lazy-transport and
completion support graphs. It never inserts a missing edge into K. Each
path certificate records its adjacency and, for every ordered pair (i,j), a
length-m path with the prescribed endpoints and positive edges. Verification
uses Boolean/finite-index assertions, not floating convergence. The generic
positive-path implication is also proved in Lean as
`matrix_power_positive_of_path`.

For the freshly replayed original snapshots:

| Configuration | Lazy transport | Recorded spectral / cluster / audit completion |
| --- | --- | --- |
| original 16-state | positive power 2 | powers 1 / 2 / 1 |
| original 20-state | positive power 1 | powers 1 / 1 / 1 |

Both kernels have an incoming positive entry in every column. Consequently
the generic B Q U theorem applies, for every nonempty partition, to their
mathematical real completion models. In particular changing an initial
distribution cannot create multiple exact fixed objects of the SAME operator.

**Exact data interpretation and coverage.** Stored floating kernels can have
row sums differing slightly from one when their binary values are interpreted
as exact real numbers. We explicitly use

```
K_ij = v_ij / sum_j v_ij
```

for the mathematical probability row associated with recorded table v.
This normalization preserves its support. Certificates report the exact
binary-rational row-mass discrepancy and a hash of every hexadecimal input
value. The full report retains the input table; the compact receipt retains
support and path witnesses plus the full-report hash. This is an explicitly
declared real interpretation of fixed recorded data, not a proof that the
ideal real seeded F^n produces exactly that table, nor a certificate of
floating iteration. Original global audited-shell membership remains open.

The source-to-prototype and normalization bridge is the analytic derivation
above; the general saturation and positive-path implications are mechanized.
The Python support witnesses have not been imported as Lean dataset terms.

## Actual error diagnostics and forcing evidence

The correct a posteriori estimate uses the BLOCK residual:

```
||mu-p||_1 <= ||mu M^m-mu||_1 / (d epsilon).
```

Lean proves this in `primitive_completion_stationary_error`. The diagnostic
now searches for a positive power, up to eight steps, and computes the actual
block image before using its residual. Failure of that finite search is
inconclusive, including for an absorbing operator with a unique boundary
stationary law. Reducible identity matrices receive no uniqueness claim.
False-target tests cover both situations.

On the current original reports, all 18 pre-completion and all 18
post-completion runs in each configuration converge numerically. All 18 per
configuration have separated candidate objects after the stationary-error
estimate is subtracted. Previously the original 16-state report could
recognize only six of these changes because the one-step minorization gave no
error estimate for the singleton completion. No underlying operator was
changed to obtain the stronger evidence.

These separation bounds are FLOATING estimates, with
`materiality_certified=False` and `error_bound_certified=False`. Exact
fixed-input mixing is not an interval certificate for the sizes of the object
changes. The previously mechanized exact 4-state split remains a separate
instance; original-shell strict extension is still unproved.

## What the old descriptor witness can and cannot establish

The old audited descriptor includes family/config id, tau, active lens and
pressure/growth scalars. Within that historical panel generator, each config
has ONE recorded kernel. Config, tau and lens already determine its completion
operator. Primitive saturation gives one exact completed object for that
operator, independent of the sampled initial distribution.

`primitive_completion_readout_factorizes` proves the general implication:
if the exact base descriptor determines a primitive completion operator, then
every mass-one fixed completed readout factors through the descriptor.
Therefore discrepancies among rounded transient completions in these panels
cannot prove exact strict extension. Post-forcing objects can still differ
from pre-forcing objects: the operator has changed. That comparison does not
supply two shell states with the SAME exact pi_0 and different pi_1.

To recover the original global strict-extension claim we still need a precisely
specified coarse pi_0 and an exact collision witness lying in the original
invariant shell. The existing pressure-only 4-state witness is useful
constructor support, but does not discharge this applicability requirement.

## Full-loop history conditioning obstruction

The earlier constant-matrix no-gap result is now strengthened. Let C_n be ANY
sequence of nonnegative history matrices, including the actual product along
a moving hybrid state/noise/selector history. For a fixed full-support
probability law p and `c=min_i p_i>0`,

```
c ||C_n||_infinity <= p C_n 1 <= ||C_n||_infinity.
```

Thus whenever the original norm pressure limit exists, the initial-law
conditioned limit is the same. No future strict-positive-entry hypothesis,
frozen kernel, autonomous completion channel, or uniform row comparability
is required. `HistoryConditioning.lean` proves the comparison and limit step.

There is a stronger exact endpoint at s=1. The ORIGINAL weighted stochastic
matrix is `A_1(x)=exp(-q(x)) K(x)`. Its row sum is `exp(-q(x))`. For any
full-loop F, the rows of the product have common sum

```
product_(t<n) exp(-q(F^t x)).
```

Every probability initial law, even one with zero coordinates, gives exactly
this partition. It equals the row-sum operator norm at EVERY horizon. Taking
a shell supremum also preserves equality when only the initial laws change
and the SAME hybrid-state/history carrier is used. Therefore fixed-law
conditioning cannot yield a strictly positive gap at the working-grid point
s=1. `stochastic_cocycle_initial_law_independent` mechanizes this for arbitrary
moving kernels and q, with explicit matrix typing and the row-sum norm.

This is not a theorem about restricting hybrid states or conditioning a
persistent history event. Those alternatives remain logically possible, but
need an actual fiber map, reference law, normalized weights, finite-horizon
disintegration and a proved pressure separation. Neither the original
synthetic moment correction nor the finite-start panel supplies them.

## Remaining original obligations

1. Construct a nonempty invariant realization of the original smaller shell;
   its rectangular predicate is already disproved as a general invariant.
2. Populate the original cocycle pressure's shell applicability and parameter
   bridges on that SAME domain, without importing optional minorization.
3. Specify the exact original pi_0 and construct an original-shell split pair.
   Saturation and forcing alone do not establish this collision.
4. Specify a genuine conditional law for the ORIGINAL history potential and
   prove its pressure separation. Fixed-law conditioning cannot be that law;
   the positive affinity comparison is not a disintegration substitute.

## Fresh validation and self-review

`lake build` passed. The current axiom audit covers 139 exported declarations:
two need no axioms and the remainder use only `propext`, `Classical.choice`,
and `Quot.sound`. The selected regression suite passed all 92 tests, including
the sparse-cycle, reducible-identity, absorbing-boundary and moving-history
controls. These are current receipts; older commits' validation remains
historical.

All six recorded completion certificates were recomputed from the retained
input tables and checked against their paths, raw support, config hashes,
source/verifier hashes and full-report hash. Original obstruction and downstream
closure/conditional reports were regenerated. Their global theorem certificates
remain false. No paper file was edited.

Self-review checked the positive-block existence construction, the remainder
steps in full-sequence convergence, preservation of the finite informant, and
the exact support-to-real-data interpretation. This is self-review, not an
independent review. The principal unresolved bridge is still membership in the
original infinite-time shell; fixed recorded tables do not establish it.
