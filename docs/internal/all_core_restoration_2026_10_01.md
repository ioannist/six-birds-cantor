# Constructive attempts at all four core claims

The paper is unchanged. This note distinguishes the original stronger shell
from an explicitly declared repaired carrier. It does not close the old ledger.
The new work uses real arithmetic with legal noise streams; exact rational
certificates check algebraic instances, while float replays check the connection
to source operations without certifying exact float equalities.

## Carrier and operational changes

For fixed d>=4 and 0<epsilon<1, use row-stochastic kernels with entries at
least epsilon/d, budget in [0,12], tau in [3/5,4], and phase in {0,...,11}.
Include the selector names, their previous labels, fixed pilot parameters,
valid finite bookkeeping histories, and the legal future input stream.
The stream provides the random choices and each entry's noise in [-sigma,sigma].
The ideal probabilistic version uses independent fresh uniform draws. It is
distinct from an infinite theorem about Python's finite-state seeded generator.

Two changes are explicit in the implementation:

* `kernel_minorization=epsilon` blends the final noisy stochastic kernel
  with the uniform kernel, and also minorizes the initialized kernel. Its
  default is zero, preserving the historical update. This is a repaired variant
  of F, not an assertion that the old clipping update had a positive floor.
* `retained_packaging` stores the actual P5 object selected before P1/P2/noise.
  Previously only its name survived. `complete_retained_packaging` completes
  that actual object against the current kernel. The legacy lens-reconstructed
  completion panel remains a separately named operation.

Valid positive warm starts are allowed in the mathematical carrier. The
recoupling starts below are not claimed to have been produced by the historical
seed-only initializer or to belong to the old smaller shell. The initial
package memory can be absent; the split memories below are genuinely produced
by an update, rather than freely added to a pair of states.

## 1. Invariance, persistent variation, and causal necessity

P1 forms normalized nonnegative targets and convexly blends stochastic rows.
P2 multiplies by positive column weights and normalizes; its fallback is a
convex blend of stochastic rows. Both preserve stochasticity. Clipping noise
preserves nonnegativity; the normalization's zero-total branch is uniform.
For d sigma<1, even the ordinary denominator is positive: each clipped entry
is at least K_ij-sigma, so the row total is at least 1-d sigma>0.
Here sigma<=9/2000, so this estimate covers the actual d=8 and d=16 cases.
The explicit final minorization gives K'_ij>=(epsilon/d), with row sums one.
P3 and P6 clamp tau and budget to their displayed intervals, and P3 advances
phase modulo twelve. Induction gives these invariants for every legal stream
and every time. Initialization supplies a nonempty instance. This box supplies
uniform estimates independently of a sampled trajectory.

There is also a genuine infinite-time noncollapse theorem, for enabled P6 and
ideal fresh uniform noise. Let sigma_min=1/400, sigma_max=9/2000 and

```
c=(1-epsilon)/(d (1+d sigma_max)^2),
r=c sigma_min/4,   p=2^(-(d+1)).
```

Condition on all decisions before the final entry noises. In one pre-noise
stochastic row choose a maximizing coordinate a, so K_a>=1/d, and j!=a.
Consider the event that every entry noise other than j is nonnegative,
of conditional probability 2^(-(d-1)). For j's noise u in [0,sigma],
write S for the sum of the other noisy coordinates and y for K_j.
Then S>=1/d, all totals are at most 1+d sigma_max, and its final coordinate is

```
f(u)=(1-epsilon)(y+u)/(S+y+u)+epsilon/d.
```

For v>=u its exact difference is
`(1-epsilon) S (v-u)/((S+y+v)(S+y+u)) >= c(v-u)`.
For any old coordinate value, the inverse image of its closed r-neighborhood
has length at most 2r/c=sigma_min/2<=sigma/2. At least sigma/2 of [0,sigma]
therefore lies outside it. Since j's fresh uniform draw has total range 2sigma,
the conditional chance of a jump greater than r is at least p.
The probability of avoiding such a jump for N successive steps is at most
(1-p)^N, by successive conditioning. Consequently there are infinitely many
jumps exceeding r almost surely. The kernel cannot converge or become frozen.
This theorem also holds for the original unminorized rule, with epsilon=0.
It does not imply persistent lens switching, or selector margins bounded away
from zero. Exceptional deterministic legal streams remain allowed.

All six operations are essential to the update as FUNCTIONS on the new carrier,
in the existential counterfactual sense: each has a legal input on which removing
it changes the output. A common warm start proves this constructively. Take d=8,
all rows p=(.01,.01,.01,.01,.24,.24,.24,.24), phase 4, tau=.6, budget=12,
incumbent cluster lens and cluster package, hysteresis values 1, income scale 10,
cost scale 1. Choose equal positive legal noise u=.00225 in every entry.
The full lens score L lies in [.74,.84] and the cluster package score is
C=.395+.32L in [.6318,.6638]. The actual cluster package has the two contiguous
four-state cells and core=all. Set eta=.092+.05C and a=.03C.

* Removing P1 leaves high-row coordinate 0 equal to .01 before noise, while
  the full rewrite gives `.01[(1-eta)+.4 eta/(1.376+a)]<.01`. High rows do not
  enter P2's fallback. Equal positive noise and minorization preserve the strict
  difference because both row totals are one.
* Removing P2 omits low-row fallback. Their first-cell P1 mass is at most
  `.04+.18*.96<.5`, and the full fallback moves it strictly toward .5.
* Removing P3 leaves phase 4; the full update has phase 5.
* Removing P4 sets the selected lens score to zero and halves support.
  The cluster package score becomes .395. High-row viability is still
  `.296*.62=.18352>.18`, so neither version uses fallback there. The function
  `1-eta(C)+.4 eta(C)/(1.376+.03C)` is strictly decreasing in C, proving that
  high-row coordinate 0 changes.
* Removing P5 uses fallback core {0,1}. Every row then enters the P2 fallback,
  whose coordinate 0 is 2/7. A high row's coordinate 0 after P2, before P6, is
  at least `.65*.01+.35*(2/7)>.1`, whereas the full version is <.01.
  Equal positive noise and minorization preserve this difference.
* Removing P6 omits the positive noise, which moves every nonuniform row
  toward uniform: `(W_j+u)/(1+d u)`. The warm-start high rows are nonuniform.
  P6 also changes the income record.

These arguments establish nonredundancy of the six operations. They do not
assert that each operation changes every state at every step. The smaller
original budget/tau/margin shell is still not established. The new box and
almost-sure noncollapse are proposed rigorous substitutes for that obligation.

## 2. Genuine pressure on the full repaired loop

Use the actual selector-potential formula from the history diagnostic, clamped
to q in [1/20,10]. Since the next step's selected data depend on the next
input draws, include that input stream in x; q(x) is a well-defined observable
of the extended deterministic state. With the actual repaired K(x), define
`A_s(x)_ij=(exp(-q(x)) K_ij(x))^s` and multiply these matrices along F.

The full proof in `cocycle_pressure_restoration_2026_10_01.md` now has a supplied
instance for its positivity and boundedness hypotheses: kappa=epsilon/d,
q_min=1/20, q_max=10, and the invariant carrier above. It gives existence and
finiteness of the shell-supremum pressure, global Lipschitz continuity for
s>=0, strict decrease, and a unique zero in (0,1). It genuinely uses the full
loop's kernel/selector history. It does not require the old stronger margin
shell. There is no Hausdorff-dimension conclusion without a geometric bridge.

`PressureRegularity.lean` derives Lipschitz continuity, strict decrease, and
the unique zero from the exact secant bounds and endpoint signs, rather than
assuming those three conclusions. The secant bounds' matrix-to-pressure bridge
is proved analytically; the complete matrix instance is not fully mechanized.

## 3a. Full-future cocycle split from ACTUAL retained P5 memory

This witness goes beyond a scalar descriptor collision. Use the warm carrier
above, epsilon=1/25, and two pre-kernels with identical rows

```
p0=(.01,.01,.01,.01,.24,.24,.24,.24),
p1=p0+delta(e0-e1),   delta=1/1000000.
```

Their finite stationary informants are exactly p0 and p1: uniform maps to p
at its first iterate, and the next iterate is unchanged. Their diagonals are p,
so their actual P5 support vectors are p. The n=8 cluster routine compresses
its singleton groups into {0,1,2,3},{4,5,6,7}. Its core is all states. All rows
have row-similarity one. Thus the SAME actual phase-4 lens score L, package score
C, eta, and diagonal addition a occur on both inputs. Hysteresis retains these
incumbents at this first step: candidate scores cannot beat them by 1.

For either input, the low-row target denominator is .824+a and the high-row
denominator is 1.376+a; transferring mass within the first cell does not change
either denominator. Low-row viability is less than .18, high-row viability
greater than .18, on both inputs. Since the core is all states, P2's row-constant
viability multiplier cancels upon normalization. Hence pre-noise kernels W0,W1
depend AFFINELY on p, with

```
W1_ij-W0_ij = lambda_i delta (1_(j=0)-1_(j=1)),
lambda_low=.65[(1-eta)+eta/(.824+a)],
lambda_high=(1-eta)+.4 eta/(1.376+a),
0<lambda_i<1.22.
```

Low-row first-cell mass after fallback is at least `.65*.04+.35*.5=.201`.
Compared to its input .04, each low row changes cell mass by at least .161.
Cauchy--Schwarz on the two four-state cells gives Frobenius variation at least
sqrt(2)*.161>.12. P3 therefore clamps BOTH outputs to tau=.6 and phase 5.
P6's income is at least `10(.24*.6318+.12*.74)>2`, and its cost is at most
`.06+.018*5+.04*4=.31`, since stochastic-kernel variation is at most sqrt(2d)=4.
It therefore clamps BOTH budgets to 12. Consequently sigma=9/2000 on both.

Let R=(W0+W1)/2. Choose each state's legal noise as e_z=R-W_z.
Every entry has magnitude less than `.61 delta<1/1000000<sigma`.
The noisy rows are EXACTLY R, already stochastic, so normalization does not
alter them. The optional minorization gives the common current kernel
`K*=(1-epsilon)R+epsilon J`. Both next states have the same tau, budget, phase,
protocol, lens/package names, primitive flags, pilot parameters, and previous
selector labels. They retain different actual P5 support vectors p0 and p1.

Inspect the update's read set: the next kernel, selector choices/scores and
potential depend on current K,tau,budget,phase,protocol, incumbent names,
previous selector labels, pilot parameters and fresh input draws. Retained
P5 contents are consumed only by the new completion readout. Old income,
action weights, informant cache, previous kernel and diagnostic histories are
overwritten or only affect bookkeeping counters; they do not feed these
kernel/selector computations. With a common future input stream, induction
therefore gives the SAME entire future kernel/selector cocycle on both states.

Define pi0 to retain this whole future cocycle and the current lower coordinates
just listed. Explicitly omit the actual past P5 support record. Define pi1 to
adjoin the frozen-current-kernel completion closure of the retained package.
This is an exact domain and pair of maps; it is not a rounded descriptor.

Both current completion operators are strictly positive, with unique positive
fixed probability vectors. Write their common-current-kernel prototype base
as `b_j=.55 pi_hat(K*)_j+.20 K*_(j,j)`. Their actual prototypes are
`w_zj=b_j+.25 p_zj`. In the first cell, sum_j w_zj is the same on both inputs,
w_02=w_12>0, and w_10-w_00=.25 delta>0. Every stationary completed distribution
has within-cell ratios equal to its prototype ratios, since its image lies
in the reinstatement range. Thus the two positive fixed distributions cannot
agree. `completion_stationary_ratio` and `retained_prototype_split` mechanize
this readout argument, while the source-level recoupling bridge is analytic.

This is also more than a relabelling artifact. The shared K* has distinct,
unique diagonal tags on states 0 and 1: their difference is
`(1-epsilon)lambda_low delta>0`; the other low diagonals have the intermediate
value and the high diagonals are separated from them. A kernel automorphism
must fix state 0. The common transport is strongly lumpable on the two cells;
the stationary first-cell mass is therefore the same positive m on both
completions. The prototype cell sums agree, so the difference in stationary
coordinate 0 is exactly `m*.25 delta/sum_(j<4) w_zj>0`.
No base-preserving relabelling removes that distinction.

Exact rational certificates check these formulae at rational L, including both
interval endpoints; the analytic estimates apply to EVERY real L in the interval,
which includes the source's actual sine value. Float replay uses the actual
step function with compensating legal noises and checks the completion and
subsequent histories. Its near equality is not used as an exact certificate.

Scope: this proves strictness on the declared positive warm-start carrier for
the retained-package repair. The original stronger shell and seed-only
reachability remain open. A frozen completion limit is persistent under its
fixed E; the outer F overwrites the retained package at its next step. Persistence
under the full outer loop is a DIFFERENT claim, not supplied here. If pi0 instead
retains the actual retained support/prototypes, completion factors through it.

## 3b. Whole scalar partition-family split and material feedback

A separate useful witness preserves even the active lens and package. Let

```
K=[[.40,.30,.20,.10],[.10,.35,.25,.30],
   [.25,.15,.30,.30],[.25,.20,.25,.30]],  K'=transpose K,
tau=1, lens=audit_flow_quantile_lens, q=log 2.
```

Both are positive and doubly stochastic. They have identical diagonals and
uniform finite informants, hence identical completion support and the actual
audit package {0,1},{2,3}. For ANY real entrywise weight function w and ANY n,
the total partition `sum_ij ((w(K/2))^n)_ij` equals its transpose counterpart,
because transposition commutes with powers and exchanges the summed endpoints.
This retains all finite total history partitions, not just an asymptotic curve
or sampled values. Total partitions and maximum row sums differ by a factor
between 1 and d, giving the same asymptotic pressure. The whole frozen-kernel
pressure curve therefore agrees. The kernels are not permutation-conjugate:
their distinct diagonal tags fix states 0,1 but the 0->1 entry differs.

The unique current audit completion limits are, respectively,

```
(4063/15745,3842/15745,784/3149,784/3149),
(4063/15849,3842/15849,1324/5283,1324/5283).
```

`PressureExtension.lean` proves the whole partition-family identity, the actual
B Q U formula, positive operators, displayed stationarity, uniqueness, and
non-factorization. Its declared base retains tau, the audit lens and the ENTIRE
identical reinstatement operator. It explicitly omits the labelled K.
This frozen history family is not the evolving full-loop cocycle of 3a.

For the first kernel, the actual completion-feedback rule sends a converged
audit panel to spectral. That policy chooses the all-state cell and yields
the exact one-step saturated output `(239/891,226/891,71/297,71/297)`, different
from the pre-forcing audit limit. The float regression executes the feedback
and then recomputes completion, rather than counting a lens proposal as forcing.
This is material enlargement of a declared one-lens completion panel. It is
not another attractor of the same positive operator, and it is not a proof
that the retained-memory full loop performs that feedback automatically.

## 4. Thermodynamic attempts and the surviving obstruction

Even the full-future split in 3a does NOT rescue the old initial-conditioned
pressure claim. If Z_n is a positive history partition and p is a positive
completion prior, `min_i p_i Z_n <= p C_n 1 <= Z_n`. Their normalized logarithms
have the same limit. Uniform one-step positivity proves this even for arbitrary
initial probability laws, with a uniform bounded factor. Thus interpreting the
paper's package conditioning as initial-law conditioning in this positive
history model gives a weighted gap exactly zero. Strictness cannot change this
result; this is not a claim about all conceivable undefined conditioning rules.

Two constructive endpoints are available, with their different scopes visible.

First, every-time path survival in each actual proper package cell has genuine
pressure loss, by the two-step escape theorem in the pressure restoration note.
Both witnesses have proper cells. This prices repeated path restriction. It is
not disintegration over persistent fixed distributions and does not by itself
price the additional retained support distinction in 3a.

Second, omission of the completion distinction has an EXTENSIVE predictive
relative-entropy cost. This applies directly to either split pair. With prior
1/2 on z=0,1, run its actual completed Markov kernel E_z from its own stationary
law p_z. The best autonomous predictor whose vocabulary has only the common
lower object and current microstate i has row

```
R_ij=(p_0i E_0ij+p_1i E_1ij)/(p_0i+p_1i).
G=sum_(z,i) (p_zi/2) KL(E_zi || R_i).
```

All laws are positive. Minimizing expected log loss separately at each current
state gives R (the KL decomposition also proves this directly). Distinct E_z
rows give G>0. For a length-n completed path, the expected log-likelihood ratio
to this fixed comparator, conditional on the same starting microstate, is nG
by additivity and stationarity. It is a prediction/free-energy price on the
COMPLETION dynamics, not an asymptotic pressure difference on the common
underlying K, nor a claim against arbitrary history-adapted predictors that
can learn z. The target observation has to distinguish the completion rows;
strictness alone does not guarantee utility for every observable.

For an exact short certificate, Pinsker in natural logs gives
`G >= sum_(z,i) p_zi ||E_zi-R_i||_1^2/4`.
One elementary proof groups the positive/negative differences using log-sum
(Jensen), then reduces to Bernoulli laws. Their KL, as a function of the first
probability at fixed second, has second derivative 1/(t(1-t))>=4, hence is
at least twice the squared probability difference. That difference is half
the original l1 distance. This supplies the displayed constant without an
unverified entropy offset.

The transpose instance has exact rational lower bound
`855037867943/1025712538718750 > .0008336` nats per step. For the retained-memory
rational instances (including the two L endpoints), an exact comparison
certifies the simpler positive bound 1/10^20 nats per step. These bounds are
calculated from the actual stationary laws and operator rows. The generic
analytic strict positivity applies at the source's real L too; the short
numerical constant is only claimed for the rational checked instances.

This gives a meaningful replacement payoff. Keeping the old pressure-gap
endpoint would require changing the conditioning operation or abandoning the
positive initial-conditioning model. This note has not silently renamed the
new consequence to the paper's original theorem.

There is now a THIRD endpoint which restores a genuine weighted pressure gap
with an explicitly declared relative-likelihood path potential. Retain the
same lower autonomous predictor R just constructed; it is common to both
states, so adjoining it to the base does not remove the split. For 0<t<1 let

```
T_z(t)_ij = E_zij^(1-t) R_ij^t,
Z_z,n(t) = p_z T_z(t)^n 1,
Q_z(t) = lim_n log Z_z,n(t)/n.
```

Expanding the matrix product gives exactly the completed-path expectation of
`exp(-t sum log(E_zij/R_ij))`. It is a partition of actual histories with a
potential paid at EVERY step. Positive finite matrices give positive finite
exponential lower/upper bounds and submultiplicativity of their row norms;
Fekete and the bounded-factor initial-law comparison give existence and
finiteness of Q_z. At t=0 and 1 the matrices are stochastic, so Q_z=0.
For 0<t<1, Holder's inequality gives each row sum at most one, strictly less
than one when the E_z and R rows differ. EVERY row differs in both displayed
split pairs. In 3a this follows because every positive transport assigns positive
mass to the first cell, whose reinstatement weights differ. In 3b it follows
from the displayed exact tables. Thus Q_z(t)<0.

At t=1/2 this has an exact quantitative certificate. Put u_j=sqrt(E_zij),
v_j=sqrt(R_ij). Both have squared norm one. Cauchy--Schwarz gives

```
||E_zi-R_i||_1^2
 <= (sum (u_j-v_j)^2)(sum (u_j+v_j)^2)
 <= 4 sum (u_j-v_j)^2
 = 8(1-sum u_j v_j).
```

Let `lambda=min_(z,i) ||E_zi-R_i||_1^2/8>0`. Every affinity row sum is at
most 1-lambda. Matrix multiplication therefore gives, at every n,
`Z_z,n(1/2)<=(1-lambda)^n` and `Q_z(1/2)<=log(1-lambda)<0`.
`AffinityPressure.lean` proves the row inequality and derives the exponential
partition bound at ALL horizons from it. It does not assume an exponential
pressure-gap comparison as a premise. Rational arithmetic verifies lambda
from the actual operators and stationary laws, without rounding square roots.

The reference channel R has pressure zero. Hence its reference-minus-weighted
package gap is `-sum_z w_z Q_z(t)>0`, and at t=1/2 it is at least
`-log(1-lambda)>=lambda` for ANY normalized nonnegative package weights.
The exact retained-memory rational examples verify the short lower bound
lambda>1/10^20. Equal completion laws give T_z=R, Q_z=0 and zero gap, a false
target control. Strictness of an unrelated observable is not used to infer it.

The same comparison can coexist with the closed base pressure P0(s): take the
tensor product of its actual history cocycle with the frozen completed-path
channel T_z(t). Nonnegative row-sum norms multiply under tensor products,
so the hybrid shell envelope is exactly `Phi_n(s)||T_z(t)^n||_infinity`;
the reference channel R has norm one. The genuine hybrid package profile is
`P_z(s,t)=P0(s)+Q_z(t)`, and

```
P0(s)-sum_z w_z P_z(s,t) = -sum_z w_z Q_z(t)>0.
```

Here P0's state carrier is paired with a FIXED selected completion channel;
the augmented update is `(x,T_z)->(F(x),T_z)`. This is a declared frozen
completion-channel construction, rather than a claim that outer F itself
preserves its previous P5 object. The pressure sum is derived from tensor
history products, not an injected entropy term. The potential and this
auxiliary retention operation differ from the old initial-conditioning model.
It restores the FORM and positive strength of a weighted pressure consequence
on this explicit hybrid carrier; identifying it with the paper's currently
unspecified conditional-disintegration object remains a target decision.

## Corpus use and remaining work

Read sources as available locally on 2026-10-01:

* `../six-birds-papers/Tsiokos_2026_Institutions_Are_Strict_Extensions_of_the_Game.tex`,
  carrier non-definability, exact gap/residual decomposition, and strict-extension
  certificate with their proof explanations. SHA256
  `5d6966a85a1c2b67f7b705ed18a057f6698d9e533b35a52fa294a5ebccf51eaa`.
* `../six-birds-papers/Tsiokos_2026_Six_Birds_Verified_VII_Formation_and_Explanation.tex`,
  RGT5/RGT6 and their appendix proofs (constructor invariance, exact split pair,
  and target-specific utility). SHA256
  `c40f90bc186cd94d58e6ff8a7a58ffc26ff1556d1a78bce8b1c61135dc3e0e02`.

These supply construction patterns and clarify the separation of strictness
from utility. Their finite application conclusions do not establish this
continuous instance. The Institutions paper itself cites this Cantor paper;
its application-level strict-extension certificate is therefore NOT used as
a circular import. The local derivations and split pairs above stand on their
own. The exact factorization lemma is the formal endpoint of the witnesses.

The remaining original-target obligations are preservation/nonemptiness of
the historical smaller shell; reachability from its historical initializer;
agreement on which exact current versus future package data T0 retains;
persistence under the outer F rather than just frozen E; automatic material
feedback on the retained-package carrier; and adoption of a valid consequence
endpoint. No source theorem eliminates these distinctions. The matrix-instance,
noise probability argument, and source-level read-set bridge still need fuller
mechanization. The new Lean files have no `sorry` or added axioms, but that is
not represented as full mechanization of the simulator or of all four originals.

## Self-review and validation

The adversarial pass checked the exact warm-start domain, the source's actual
singleton-compression policy, the cancellation of row-constant P2 viability,
the two clamps before noise, and the source read set used in future induction.
It separately checked frozen-E persistence versus outer-F persistence, coordinate
relabelling, the finite informant rather than the stationary limit, and the
failure of both new split pairs to imply an initial-conditioned pressure gap.
This is self-review, not an independent review.

Validation of this revision: 90 selected mathematical/source regression tests
passed; `lake build` succeeded with Lean/mathlib v4.8.0; the expanded axiom audit
prints only standard Lean foundations or no axioms. The 96-step receipt in
`results/core_restoration/report.json` is explicitly scoped and does not close
the original ledger. The selected tests are not represented as the entire
repository suite; the earlier audit records pre-existing paper-wording failures.
