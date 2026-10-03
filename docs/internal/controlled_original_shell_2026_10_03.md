# All-time controlled carrier for the original 20-state loop

This supplies previously missing support for the lawful-shell and
strict-extension obligations. It uses the original pilot parameters and
the exact-real interpretation of the existing outer-loop formulas. No
minorization operator, enlarged hysteresis, altered income scale, or
retained-memory dynamics is introduced. The paper is untouched.

There are three different scope questions. We now construct an invariant
controlled carrier satisfying the operational shell bounds. We do not prove
that the seeded floating-point experiments enter it, or that it is invariant
under every independently drawn innovation word. The original paper never
specified its shell or base object completely; identifying those names with
the explicit carrier and descriptor below remains an editorial/mathematical
definition obligation. The original conditional-pressure theorem is not
reported as proved.

## Source restriction and validated arithmetic

Partition the physical indices into A={0,...,4}, B={5,...,9}, C={10,...,19},
with sizes n=(5,5,10). Represent a kernel by a stochastic 3-by-3 aggregate
matrix M and diagonal excesses h_a:

    K_ij = c_ab + h_a 1_(i=j),
    c_ab = (M_ab - h_a 1_(a=b))/n_b,      i in a, j in b.

This is a restriction of the full 20-state source, not a different Markov
model. The P1 target, P2 gating and fallback, Frobenius variations, and all
P4/P5 candidate scores are computed with their actual multiplicities.
Physical cluster packaging still uses the two contiguous halves A+B and C;
completion cluster packaging still uses singleton cells. These two
constructors are not identified with each other.

Every pair type in the row-similarity computation has at least ten pairs:
10, 10, 45 within classes and 25, 50, 50 across classes. Thus its top-ten
average is exactly the maximum of the six pair-type cosines. Its grouping
algorithm still returns singleton cells, which physical P5 compresses into
the two halves. This justifies the reduced similarity score and grouping.

The finite stationary INFORMANT is iterated from group masses n_a/20 with
the source's 80-step cap and exact stopping condition

    max_a |p_next[a]-p[a]|/n_a <= 10^-12.

The full normalization is exactly the identity at every step because the
represented kernel and iterate are stochastic. This is not substitution of
the invariant distribution for the finite informant. For a parameter box,
all possibly stopped iterates are enclosed until stopping is forced. The
selected radius below additionally certifies one stopping count per phase;
no informant stopping surface is crossed on the cyclic kernel family.

Arithmetic uses rational endpoints rounded OUTWARD to the grid 10^-25.
Square-root bounds use integer square roots. Logarithms use range reduction
to [1,2] and the series

    log y = 2 sum_(k>=0) t^(2k+1)/(2k+1),  t=(y-1)/(y+1).

The 60-term remainder is bounded by
`2 t^121/[121(1-t^2)]`, with interval arithmetic accounting for every
rounding operation. Exponentials used in the pressure calculation have a
rational Taylor remainder after reduction to [0,1], then repeated squaring.
No floating transcendental routine supplies certificate endpoints.

## Explicit cyclic targets and the Cantor parameter

`configs/mathematics/original_controlled_cycle.json` gives twelve rational
targets K_k. They were scouted numerically, then rounded with exact row mass
preservation. Their mathematical status comes from the subsequent interval
checks, not their numerical origin or a convergence plot.

At phase k allow

    K_k(lambda) = (1-lambda) K_k + lambda J,
    0 <= lambda <= r=10^-14,       J_ij=1/20.

For a Cantor kernel coordinate restrict lambda to the scaled ternary Cantor
set `r sum_(m>=1) 2 a_m/3^m`, a_m in {0,1}. These are genuinely different
real kernels because each K_k differs from J. The certificates cover the
whole interval, hence also the Cantor subset. Next-step parameters may be
chosen independently of the current parameter. This supplies a continuous
kernel family and a symbolic future-target input carrier; it is not a
claim of global smoothness for all hybrid source branches or diagnostic
bookkeeping fields.

Use budgets 3<=b<=12. For pre-phase k set

    .6 <= tau <= .6+.0132*((k-1) mod 4).

The maximal upper bound is .6396, well inside the original [.55,1.05]
operational rectangle. Incumbents and their last history entries are those
from the preceding phase. Protocol is exactly the source P3 protocol.
All six primitive flags are enabled.

The exhaustive certificates cover eighteen budget cells and four timescale
cells at each of the twelve phases. They establish:

* spectral/cluster selection at phases 0..3, similarity/return at 4..7,
  audit/budget at 8..11;
* lens and packaging gaps greater than .03, beating the actual .017/.012
  hysteresis and the .03 tie band;
* return core A+B and budget core A, with the actual finite informant and
  diagonal guards;
* every P2 row uses its actual viability fallback, with viability below .18;
* actual income minus cost exceeds .01 everywhere;
* the required innovation has entrywise magnitude below .001, with the
  largest certified cyclic bound about .000217;
* all target entries exceed .01.

The exact rational bounds are in
`results/controlled_original_shell/report.json`; these rounded decimal
summaries are not the certificate itself.

## Return through the unmodified update

Let W(x) be the actual pre-noise P1/P2 operator at a certified state. For
any chosen next target prescribe

    N_ij = K_(k+1)(lambda_next)_ij - W(x)_ij.

The source permits innovations in [-sigma,sigma], with sigma>=.0025.
Our bound .001 is strictly smaller. The corrected entries equal a positive
stochastic target, so clipping and every subsequent normalization return
that target EXACTLY. No extra projection is performed by F. The controller
is a way to choose a legal innovation word, not a change to the formula
for F. It has no asserted positive probability under an independent-noise
law and no asserted realization by the seeded PRNG.

Actual P3 satisfies, for nonnegative pre-noise variation v,

    tau_next <= max(.6,tau+.0132).

At phases 0,4,8 both selectors switch, imposing the actual .07+.05=.12
penalty. If tau<=.6396 then tau+.0132-.12<.6, so P3 resets tau EXACTLY
to .6. Between these resets the three-step bound above proves the next
phase interval. We do not set variation to zero or substitute final
post-noise variation for the pre-noise variation used by P3.

Positive income-cost implies
`b <= clamp_[0,12](b+income-cost) <= 12`.
It increases b strictly until the cap; after the cap, the nonzero ledger
flows and noise mechanism remain part of P6. This is not a claim that a
bounded capped budget changes strictly forever.

These returns prove forward invariance by induction for compatible
augmented states containing their future legal innovation words. Equivalently,
one can parameterize them by current state and future target parameters and
compute the compatible innovations recursively. The source's unused cache
counters are not substituted for physical state. The actual full diagnostic
history can be lifted consistently along every constructed orbit.

The phase-8 to phase-9 change of entry K_00 exceeds .02 uniformly over both
independent parameter choices. It recurs once every twelve steps, providing
persistent operator variation without a probabilistic noncollapse premise.

## Six mechanisms are mathematically nonredundant

At cyclic phase 0, tau=.6, b=3, use the same STANDARDIZED random-input word under each
counterfactual knockout. Do NOT recompute a compensating word for the
knockout. Exact intervals and source algebra give positive scalar changes:

* P1: a cross-half kernel entry changes by more than .00130;
* P2: that entry changes by more than .01151;
* P4: that entry changes by more than .000085;
* P5: a row's total A-core mass changes by more than .1567;
* P3: the phase advances under P3 and stays fixed when it is disabled; this
  changes the ACTUAL budget cost, giving a budget difference .01728;
* P6: at b=3 the actual budget increases by more than .187, whereas disabling
  P6 leaves it at 3 and omits the innovation mechanism.

For P4 knockout the informant support is halved, its incumbent audit score
is zero, and cluster remains the isolated actual packaging winner. The
all-core fallback remains valid. Its smaller rewrite coefficient and audit
diagonal shift give the displayed kernel difference. For P5 knockout the
ACTUAL fallback packaging has core A and score zero, with the spectral lens
unchanged; its rewrite and gate/fallback increase A-core mass. These are
not proofs from deleted flags or missing records.

The baseline innovation has row sum zero. Holding z=N/sigma fixed allows
the knockout's budget to change sigma. Since sigma remains in [.0025,.0045],
the resulting innovation change is at most .8 times the baseline correction
cap. This loss is subtracted from the displayed coordinate gaps (and five
times it from the core-mass gap). Common rescaling preserves row sum zero.
All the relevant counterfactual
rows remain positive after it: the fallback rows have an explicit positive
floor, and the P2 knockout retains a positive P1 mixture. Thus clipping or
normalization cannot erase these changes. Nonredundancy means each primitive
changes the physical law somewhere on this carrier, not every coordinate at
every state.

## The strict pair enters this SAME carrier

Use the exact original 20-state tagged/skew pair already constructed in
`original_loop_extension.py`, at tau=.6, b=3, phase 0, audit/budget incumbents.
Its genuine source score is `.736+.035 sqrt(3)` in [.79,.80]. Let R be the
half-row average target constructed at rational parameter 159/200. Prescribe
noise `R-W(K+,C)` and `R-W(K-,C)` at the ACTUAL score C. Affine endpoint
checks bound these corrections by .0006, below the minimum legal .0025.
The rational construction parameter is not substituted for the source score.

R is the same positive doubly stochastic half-block kernel for both worlds.
Pre-noise variations and all selector/action inputs agree; final Frobenius
variations agree because R annihilates the skew support in its inner product.
Both original q definitions therefore agree at the joining step.

The next 24 rational targets are constructed and certified in the receipt.
The first eight pre-states are EXACTLY doubly stochastic with equal
diagonals. Consequently the finite informant is exactly uniform after one
iterate, the return core is ALL twenty states, and the first budget core is
the first five indices by the source's stable tie order. Independent entry
rounding would destroy this fact; the constructor instead preserves the
two-half symmetry and exact diagonal ties. After that budget step, the
three-class return/budget guards are strict.

Every transition has the original isolated selectors, positive income-cost,
and a required innovation below .001; the largest prefix bound is about
.000270. At the last step it enters the cyclic phase-1 family. This proves
all-time membership for the split pair and its common continuation on the
DECLARED controlled carrier. Floating quantile ties may differ from these
exact real ties; binary-float replay is not misrepresented as this proof.

The first weighted matrices differ only in columns {0,1,2}, have equal
weighted row sums for every real parameter, and the second matrix has equal
rows on those indices. Thus A0+ A1=A0- A1, and every later ordered product
agrees. Horizon-one row norms and initial-law partitions agree as well.
The current B Q U completion objects and unordered three-lens families
remain exactly different. Saturation and material frozen-input feedback are
as established in the original-loop construction. This is a strict extension
for the explicitly declared scalar-history base, now with an all-time
applicability construction. It does not prove non-factorization through a
base retaining the complete labelled K or the literal innovation word.

## Original-potential pressure on the carrier

All prefix, cyclic, and warm-pair entries exceed .01. This is DERIVED from
the controlled targets; no minorization operation was added. The existing
original physical-carrier argument supplies
`log(5/4) <= q <= log(10)` for both source observable definitions, separately.
Hence `1/1000 <= exp(-q) K_ij <= 4/5` on this carrier.

The moving-matrix supremum pressure exists. Uniform entry bounds give

    -(t-s) log(1000) <= P(t)-P(s) <= -(t-s) log(5/4), 0<=s<=t.

It is globally Lipschitz on [0,infinity), strictly decreasing, and continuous
at zero. Positive full support gives P(0)=log(20). Stochasticity gives
P(1)<=-log(5/4)<0. Moreover

    P(1/3) >= log(20)-(1/3)log(1000) = log(2)>0.

Thus the unique positive root lies in (1/3,1). This improves the sparse
physical-carrier root anchor (1/32,1) for this constructed shell and avoids
the earlier unsupported zero-endpoint regularity assumption.

## Same-potential pressure separation: necessary support, not a fiber law

A second legal periodic continuation uses
`(1-1/100) K_k + (1/100) J` at every phase. Both continuations have b=12,
the actual P3 timescale resets, original selectors, and legal compensating
innovations. The pressure calculation evaluates every source quantity,
including the actual P1 target distance, P2 mean viability, six-action
softmax entropy, and final (post-noise) variation. It does not use an
affinity or KL-modified path potential.

At s=1 stochasticity makes the history row norm
`exp(-sum_t q_t)`, so a twelve-periodic orbit has pressure `-mean(q)`.
Exact outward intervals give approximately:

| Source observable | Original cyclic targets | Targets mixed 1% toward J |
| --- | ---: | ---: |
| closure-check q | -0.5474563504855236 | -0.5463065886368166 |
| pressure-check q | -0.6041176534979362 | -0.6030214349100136 |

The pressure differences exceed .001 for both ORIGINAL observables. A
genuine equal-weight TWO-WORLD law over exactly these continuations would
therefore have a weighted gap greater than .0005, by the mechanized
max-pressure law and quantified equal-weight gap lemma. The reference law and conditioning would have to be
specified; they are not supplied by this computation.

This is missing-support work toward theoremlet four, not its completion.
These two continuations have DIFFERENT full scalar-history profiles. They
cannot be presented as one fiber of a base retaining those profiles. Nor
does assigning different completion fixed vectors as INITIAL microstate
laws separate the pressure of a common continuation: that interpretation
still has exactly zero gap. The next obligation is an actual packaged fiber
law, compatible with a precisely declared common base, that realizes the
proved separation without changing the original history potential. Strict
object extension alone does not imply that law or a positive gap.

There is a substantive choice at this last bridge. Keeping the full
scalar-history base makes ordinary conditioning on current packaged worlds
have zero gap: on a fixed base fiber their history norms agree, and uniform
positive first-step entries compare every initial-law partition to that
common norm by constants independent of the horizon. Recovering a positive
world-conditioned gap therefore needs a coarser precisely defined base and
a genuinely object-indexed conditional law realizing separated futures.
It cannot be obtained by renaming arbitrary future-control labels as
completion fibers. Alternatively, conditioning entire microhistories would
require a measurable history-fiber map actually supplied by the packaging
construction; conditioning initial completion vectors alone still gives zero.

Thus the options are to construct that missing conditional law and its base
compatibility, or to retain the stronger base and replace the last claim
with the zero-gap theorem. The first three constructions do not establish
the original generic implication from strictness to positive pressure gap.
No paper downgrade or claim of a completed fourth theorem has been made.

## Mechanization, validation, and self-review

`ControlledShell.lean` proves exact clipping/normalization return, P3 reset
and step bounds, budget invariance/increase, all-iterate induction, and the
strengthened root endpoint from explicit secants. `LoopExtension.lean` now
proves the restricted-common-row product bridge. The interval dataset and
original score formulas are computational/analytic support, not Lean terms.
No claim of fully mechanized simulator correspondence is made.

Tests compare the reduced formulas with the UNMODIFIED source, compare the
exact reduced finite informant with full 20-state rational iteration, verify
transcendental enclosures independently at high precision, reproduce all
interval cells, exercise actual same-standardized-input primitive knockouts, and replay
both periodic q profiles through the original simulator.

Self-review checked the finite-informant stopping rule, return-core ties,
physical versus completion groupings, pre/post-noise variation, pre/post
phase in the budget cost, actual pilot hysteresis, signed innovation bounds,
real versus floating scope, global-pressure norm convention, and exact base
coverage. The all-time return is an induction over verified transitions,
not extrapolation of a sampled trajectory. This pass has no independent
reviewer. The remaining original fiber-law/base-definition obligations are
kept explicit in all receipts.

Current validation: the expanded targeted mathematical suite passes 134
tests; `lake build` and the 174-declaration transitive axiom audit pass using
only standard Lean axioms (or no axioms). No project axiom or `sorryAx` is
used. The receipt generator is rerun after the final source changes.
