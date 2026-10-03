# Strict extension over an actual moving original-parameter history

This construction attacks the missing strict-extension witness. It uses the
original 20-state pilot parameters, the actual B Q U completion constructor,
and the full evolving kernel history. It does not add minorization or replace
the history potential with an affinity potential. It supplies an exact split
on a warm, legally controlled carrier. The subsequent construction in
`controlled_original_shell_2026_10_03.md` now supplies an all-time controlled
exact-real carrier for this pair, without changing the original pilot
parameters. Seeded reachability and the paper's unspecified base definition
remain unresolved. The original main theorem package is not yet complete.

## Exact kernels and current packaged objects

Let J be the 20-by-20 matrix with entries 1/20. Starting from J, for each
(i,j,a) below add a to the two diagonal entries and subtract a from the two
off-diagonal entries (i,j),(j,i):

```
(0,3, 1/10000), (1,3,-1/20000), (2,3,-1/40000),
(4,7, 1/12500), (5,7, 3/50000), (6,7, 1/25000).
```

Call the resulting symmetric matrix H. Add delta=1/1000000 on the directed
cycle 0→1→2→0, and subtract delta on the reverse cycle. This gives K+;
let K-=K+ transpose. Both kernels are exactly positive and doubly stochastic.
Every row gives total mass 1/2 to the first physical half, and 1/2 to the
second half. The finite stationary informant is exactly uniform after its
first iterate, including the source's early-stop rule. The diagonal, support
vector `(1/20+K_ii)/2`, and actual prototype weights are shared.

For each row i, the multiset of entries of K+ equals that of K-. For i outside
{0,1,2} they are identical. At a cycle vertex, two entries `1/20±delta` merely
swap. Symmetric tags involving vertex 3 do not change those two baselines.
Consequently, for EVERY real entry-weight function w,

```
sum_j w(K+_ij) = sum_j w(K-_ij)             for each labelled row i.
```

The three cycle vertices have distinct diagonal tags; transposition has not
just renamed indistinguishable cycle vertices while preserving all the
retained diagonal information.

Set tau=3/5 and the current lens to audit. The actual completion audit core
is {0,4,5,6,7}. The B Q U operators have shared reinstatement U but different
unique fixed probability vectors p+ and p-. The exact constructor verifies
stationarity, positivity, mass one, and idempotence/absorption of the limiting
closures. A displayed nonzero coordinate difference is

```
p+_0-p-_0 =
390467997745347846870000 / 120131948909489644812213124707327077.
```

This is about 3.25×10^-12; its nonzeroness is rational arithmetic, not a
floating separation claim. Saturation follows from the strict positive floor
of each actual completion, using the already proved contraction theorem.
The audit transport has a nonzero macro lumpability defect 101/3906250.

The spectral lens takes all states as its core. Its all-cell reinstatement
has the same unique fixed object p_spec for both kernels, different from both
audit objects. The cluster-completion lens retains singleton cells, so its
completion is the lazy transport with common uniform fixed object u. Therefore
even the UNORDERED full current three-lens families

```
{p+,p_spec,u}  and  {p-,p_spec,u}
```

are different. Audit-to-spectral completion feedback is material at the SAME
current kernel and tau. Keeping the family is essential: the final spectral
fixed object alone is shared and does not witness strict extension.

## Original outer-loop branch and legal joining noise

Use precisely `continuous_full_loop_kernel_shell.json` pilot parameters:
20 states, lens/packaging hysteresis .017/.012, income/cost scales 1.08/.96,
temperature shifts .045/.02, and kernel_minorization=0. Warm states have
tau=.6, budget=12, phase=0, protocol refresh, current audit/budget incumbents,
and one prior audit/budget history entry. The pilot initial tau=.88 remains
unchanged; these warm states have NOT been shown reachable from the seeded
initial condition.

The isolated selected lens is spectral, with score

```
L = .42+.05(1-.6/4) = 37/80.
```

Entropy of the uniform finite informant removes its entropy-deficit term.
An unselected similarity score is at most .32+.10-.08=.34. The audit score
is below .12. Thus the spectral challenger beats both by more than the
original hysteresis and .03 tie band. Actual P5 compresses its singleton
physical grouping into the two contiguous halves and selects cluster with

```
C = .736+.035 sqrt(3),             .79 < C < .80.
```

Its return competitor is .32+.42/20+.12 L+.12(.6/4)=.4145. Its budget
competitor is below .5201 with the declared refresh protocol, so selection
is isolated. The physical cluster core is ALL states. This is
different from the completion audit core above, and the construction does
not conflate them.

The actual P1 target has common denominator

```
D=1.7+.02 L,
T(K)_ij = [(K_ij+.1 if i,j in same half, else .4 K_ij)
             +.02 L 1_(i=j)] / D.
eta=.092+.05 C.
```

Both T(K) and the P1 output respect transposition. Every actual P2 row
viability is between .08 and .18. Because the physical core is all states,
its row factor cancels during normalization, and its fallback is uniform.
The pre-noise operator is exactly

```
W(K)=.65[(1-eta)K+eta T(K)]+.35 J.
```

For every real C in [.79,.80], prescribe noise `N(K)=J-W(K)`. W is affine in
C, so the exact rational endpoint checks bound each coordinate throughout
the interval. The noise magnitude is below .0039 < .0045, the ORIGINAL legal
noise amplitude at budget 12. All corrected entries are positive 1/20 and
their rows already have mass one. No clipping or hidden renormalization
changes the intended common output J.

The Frobenius variation before noise is below .08, since each of the 400
coordinate differences is below .08/20. Selected scores, P1 target-distance,
P2 viability statistics and that variation agree under transposition.
The two historical selector switches charge .07+.05 to P3, which clamps tau
to .6. P6 income is at least

```
1.08(.24*.79+.12*(37/80)+.08*.92)=.344196,
```

and cost is at most `.96(.06+.018+.04*.08)+.06=.137952`. Budget stays 12.
Thus after one legal original update both physical states have J, tau=.6,
budget=12, phase=1, spectral/cluster selectors and common protocol. The
retained actual P5 payload also agrees: support and physical grouping agree.
The older previous-kernel/signature bookkeeping can still differ. It is not
read by the physical update, and the next step overwrites that difference.
This distinction is explicit, rather than falsely asserting immediate equality
of every Python state field.

The action-weight softmax takes only the six listed shared primitive scores
and shared temperature. Final variation `||J-K±||_F` is the same. Consequently
the ACTUAL selector observable `_observable(step)` in the pressure-closure
runner agrees for the two first transitions, as does the differently weighted
`_observable_value` in the pressure-existence/restoration runner. These two
source observables are not identified with one another. A shared subsequent legal input
stream makes all future physical kernels and selector observables agree.

This is legal control of the simulator's continuous random-input coordinates,
not a claim that a seeded PRNG emits the prescribed exact real word with
positive probability. A deterministic state map F requires the future input
stream in the carrier; the two initial streams differ only in the joining
noise block and then have a common tail.

## Full evolving pressure profile equality

For the explicitly declared restored branch potential
`A_s(x)_ij=(exp(-q(x)) K(x)_ij)^s`, using q from the actual selector observable
(and any shared clamping used in the pressure model), the first two matrices
are A0±(s) and a shared A1(s). The pointwise row-multiset identity makes
the first-step weighted row sums identical for every real s. Since the common
kernel after the first transition is J, A1(s) has identical rows.

For ANY matrices A,B with equal row sums and ANY rank-one matrix R whose rows
are r, `A R=B R`: coordinate (i,j) is `(sum_h A_ih) r_j`. Hence the full
ordered history products agree as entire labelled matrices at every horizon
n≥2, with an arbitrary shared evolving tail. At n=1 their labelled row-sum
vectors and row-sum operator norms agree; at n=0 both are identity.

The generic bridge is mechanized in `LoopExtension.lean`. It does not freeze
the future matrices or substitute the completion operator as the cocycle.
Equality holds for ALL real parameters and ALL horizons, not just the
integer examples in the rational tests. These kernels are strictly positive,
so absent-edge conventions at s=0 do not affect the construction.

We can therefore define a coarse pi_0 retaining tau, current lens, current
forget/reinstate map and support, original pilot parameters, budget/phase,
and the entire actual scalar history-growth profile. That exact pi_0 collides
on this pair, while the full current packaged families split. This establishes
nonfactorization on a carrier containing the two warm controlled states.
If pi_0 instead retains the entire labelled first matrix/kernel, this split
does not apply; the paper has yet to fix its exact pi_0. No arbitrary choice
of a weaker pi_0 is being represented as its resolved original definition.

## Conditional-pressure implication and remaining applicability

With a shared initial microstate law, every finite partition also agrees.
Giving the two warm starting worlds positive prior weights supplies a genuine
two-world finite disintegration of the SAME branch potential. Its two
conditional partitions and its mixture partition agree identically. Whenever
the common limiting pressure exists, the weighted conditional-pressure gap
is zero despite the packaged-family split. Unlike the earlier initial-law
countermodel, this can condition which hybrid starting world/package was used.
It still does not prove that the paper's unspecified conditional law is this
one, or that this pair is in its original audited shell.

Thus strict extension alone remains insufficient to obtain positive
disintegration gap; an actual pressure-separation input is required. Conversely
this pair is constructive support for the strict-extension theorem once the
original exact coarse base and original-shell applicability are supplied.

A exploratory unmodified-source warm replay from the common J successor,
using seed 7 for 2000 later transitions, found no rectangle or .01-margin
exits: tau ranged from .6 to .6146659794133994, budget was always 12. This
FINITE FLOATING check suggests a viable shell route, but does not establish
an invariant class, ideal seeded reachability, or an infinite lawful history.
An infinite-time trapping or validated periodic-orbit proof is the next
substantive missing bridge. It cannot be replaced by this sample.

## Current verification

The targeted combined suite passed 118 tests, including eight tests for this
construction. Its exact certificates check actual 20-state completion
stationarity, limiting-closure absorption and the distinct unordered families.
The unmodified-source replay checks joining noise legality and subsequent
physical coalescence, without claiming exact floating observable equality as
a mathematical certificate. The exact row-moment/rank-one derivation supplies
the all-real/all-horizon result.

`lake build` passed; the combined current audit covers 160 declarations using
only standard Lean axioms. The new 20-state dataset has not been imported as
Lean terms. Self-review is recorded in the sparse-pressure follow-up; this
pass has not had an independent reviewer. The paper remains untouched.

## Next original-shell construction route

The next attempt can remove the large-budget requirement of the J join.
The kernels differ only in entries whose column indices are in {0,1,2}.
Instead of making the entire next kernel rank one, replace only rows 0,1,2
of W by their mean; keep every other row unchanged. Averaging these rows
annihilates the skew cycle, so the two resulting kernels R agree. Column
sums are preserved, and the three rows on the cycle are identical. Thus
`(A0+-A0-) A1=0` still holds for EVERY entry weight and parameter: their
difference is supported on those three columns and each difference row has
sum zero. Arbitrary common evolving tails then give the same full-history
collision as before.

Exact rational endpoint checks at C=.79 and .80 found maximum compensation
`1433092297/4102200000000` and `19970353/56975000000`, respectively, both
below .000351. Affine dependence on C returns this bound to the real source score.
This is below even the minimum original noise amplitude .0025, so warm
budget 3 can be used. The selected spectral/cluster branch is still isolated
there: the unselected similarity score is at most .40, below L=.4625.
Final Frobenius variations also agree exactly: R's equal cycle rows are
orthogonal to the skew cycle, while H is symmetric. The income/cost bounds
above now give an actual budget increase rather than saturation at 12.

An even simpler common continuation averages ALL rows within each physical
half of W. Both tag and skew perturbations have zero summed columns within
that half, so this gives the same doubly stochastic, two-half block-constant
R as averaging W(J). Every cycle-index row is again identical. Endpoint
compensation is below .000535, still far below .0025. Its unforced continuation
under zero legal noise stays in a small exchangeable-class matrix family;
the first budget phase splits it into classes of sizes 5,5,10. This offers
a reduced-dimensional route to a validated twelve-phase trapping argument.
The class/rank choices and trapping estimates are not yet established.

The next pass persisted the half-row constructor, the restricted-common-row
Lean bridge, and a fixed rational half target with legal compensation for
the actual irrational source score. It then certified a 24-step entry route
and an all-time cyclic Cantor kernel family; see the 2026-10-03 note and
`results/controlled_original_shell/report.json`. That is a controlled
exact-real carrier, not seeded or uncontrolled-noise invariance. It preserves
the original parameters, current completion family and history potential.
