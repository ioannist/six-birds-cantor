# Pressure without an added positive-entry blend

This supplies missing pressure applicability for the original NONNEGATIVE
stochastic kernels, including their recorded zeros. It does not modify the
outer loop, add minorization, or assert that the undefined original infinite
audited shell has been populated. The results apply to a declared nonempty
carrier X with F:X→X and the restored selector-weighted history potential.
Original-shell applicability is a separate unresolved input.

## Exact potential and original sparse bounds

K(x) is a d-by-d nonnegative row-stochastic matrix, d≥1. Fix F, K and q
independently of the pressure parameter s. Suppose
`0<q_min≤q(x)≤q_max<∞`. There are TWO source selector observables:
`_observable_value` in `run_continuous_pressure_checks.py` has coefficients
.28/.32/.10/.08; `_observable` in `run_continuous_pressure_closure_checks.py`
has coefficients .25/.30/.05/.05. A pressure instance must declare which one
it uses; they are not identical. The restoration runner uses the former and
declared [.05,10] clamping. On the original full-role physical carrier that
clamping is actually inactive, by the source bounds below. The old bounded time-sum diagnostic
still has zero pressure and is not being silently certified by these results.

For present edges, define

```
A_s(x)_ij = (exp(-q(x)) K(x)_ij)^s
           = exp(-s q(x)) K(x)_ij^s.
```

An absent edge has weight zero, including at s=0. This matches the source
history routine's support convention; it does not assign weight one to 0^0.
The moving ordered product is
`C_n(s,x)=A_s(x) A_s(Fx)...A_s(F^(n-1)x)`, and its growth readout is the
maximum ROW sum `||C_n||_infinity`, not an entrywise matrix norm. The pressure
uses the original Fekete-sup form `Phi_n(s)=sup_x ||C_n(s,x)||`.

Every stochastic row contains some entry at least 1/d, and every entry is at
most one. Thus for all s≥0,

```
a(s)=exp(-s q_max) d^(-s)
     <= sum_j A_s(x)_ij
     <= d exp(-s q_min)=b(s).
```

a(s)>0 even with zeros, without assuming a positive entry floor. Nonnegative
matrix multiplication propagates these bounds to every ordered history:

```
a(s)^n <= sum_j C_n(s,x)_ij <= b(s)^n,
a(s)^n <= Phi_n(s) <= b(s)^n.
```

Actual product splitting and the row-sum operator norm give
`Phi_(n+m)≤Phi_n Phi_m`, since F^n x stays in the SAME carrier. Taking logs,
Fekete convergence and the lower exponential bound construct a finite limit
P(s) for each s≥0. This proves existence, rather than assuming an all-horizon
growth comparison. Coarse quantitative pressure bounds are

```
-s(q_max+log d) <= P(s) <= log d-s q_min.
```

`SparsePressure.lean` proves the stochastic-entry bound, actual sparse branch
row bounds and pressure existence via `matrix_pressure_exists`. Its pressure
declaration has NO minimum-positive-entry hypothesis. The forward-invariant
nonempty X and bounded q remain visible premises.

## Source bounds, without changing the original observable

This bridge uses the ideal real interpretation of the original 16/20-state
update with all six roles enabled. Stochasticity is preserved, budget stays
in [0,12], and tau stays in [.6,4]; both original initial values satisfy these
coarse bounds. These are NOT the disputed tighter audited-shell bounds.

For every phase, one P4 candidate has its .42 active-window bonus and
nonnegative remaining terms. Its best score is therefore at least .42.
The actual selector can retain an incumbent within hysteresis, or draw from
the near-best band. Both original lens hysteresis values are below .03, so
the selected score is at least .42-.03=.39. Its upper bound is 1.25:
spectral is at most .78+.05+.42, similarity at most .32+.10+.08+.42,
and audit is smaller using flow≤1 and diagonal spread≤1.

In phases 0–3 the cluster packaging best-score floor is
`.50+.32*.39`; in phases 4–7 the return floor is `.54+.12*.39`; in phases
8–11 the budget floor is .46. The best score is thus always at least .46.
With tau≤4, original packaging hysteresis is at most .018+.03=.048 (base
pilot) or .012+.03=.042 (20-state pilot). Allowing also the .03 tie band,
the common selected floor is .46-.048=.412. Scores are capped at one.

The finite informant is a probability vector without requiring stationarity.
Both stochastic kernels before/after the step are probability rows, so
final Frobenius variation is at most sqrt(2d)<7 for d=16 or 20. The six-action
softmax entropy lies in [0,log 6], hence below 2. Tau/budget AFTER the step
still satisfy their coarse bounds. For the closure observable, its log1p
argument is at least `.25*.39+.30*.412+.05*.6=.2511>1/4`.
The other source observable has larger nonnegative coefficients. For both,
the argument is bounded by

```
7+.28*1.25+.32*1+.10*1+.08*4+.05*2 = 8.19 < 9.
```

Consequently BOTH actual source observables satisfy
`log(5/4)≤q≤log 10`. In particular q is strictly between .05 and 10, so
the declared [.05,10] clamp leaves it unchanged throughout this full-role
physical carrier. The source-to-score bounds above are analytic. The final
rational score-to-observable/log comparison is also mechanized as
`original_selector_observable_bounds`.

The exact 20-state join proves equality for either observable because ALL
their scalar inputs agree on its pair. No script's coefficients were changed
to get that equality.

## Strict monotonicity of the actual pressure

For 0≤s≤t, on every present edge K≤1 implies

```
A_t(x)_ij <= exp(-q_min(t-s)) A_s(x)_ij.
```

It is also true for absent edges. Entrywise domination propagates through the
full moving history with one scalar factor per step. Row norms, then the
shell supremum, give

```
Phi_n(t) <= exp(-n q_min(t-s)) Phi_n(s).
```

Taking the already constructed limits gives
`P(t)-P(s)≤-q_min(t-s)`. Thus P is strictly decreasing and nonconstant on
the nonnegative parameter range. This is a mechanized derived secant bound,
not a secant-shaped hypothesis. Lean exports include
`sparse_selector_pressure_parameter_bound` and
`sparse_selector_pressure_strictAnti`.

At s=1, each A has row sum exp(-q). Consequently the sharper bound is
`-q_max≤P(1)≤-q_min<0`. The mechanization proves the upper endpoint
`sparse_selector_pressure_at_one`; the lower endpoint follows directly from
the same scalar-row product inequality. Strict decrease plus this negative
anchor supplies genuine nondegeneracy, rather than relying on rounded signs
of the old zero-pressure diagnostic.

## Regularity on the original positive working window

For fixed x, initial i and finite horizon n, list the PRESENT length-n paths
h. Their weights have the form `exp(s L_h)` where L_h is the sum of the log
branch weights along the actual moving hybrid history. The list does not
depend on s. At least one legal path exists from each i by stochasticity.
For 0≤theta≤1, the finite Holder inequality gives

```
Z_i(theta s+(1-theta)t,x)
  <= Z_i(s,x)^theta Z_i(t,x)^(1-theta).
```

Taking the maximum over i and supremum over the SAME X preserves this upper
bound. Thus `log Phi_n(s)/n` is convex. The finite pointwise pressure limit
preserves the convexity inequality. A finite convex function is continuous
and locally Lipschitz on the INTERIOR (0,∞). This completes the mathematical
regularity bridge on the positive working window [.5,1.5]. This Holder/
convexity/regularity step is an analytic proof, not yet a Lean declaration.

For an explicit local estimate, take 0<a≤b and set
`D=log d+2b(q_max+log d)`. The above coarse bounds confine P on [a/2,2b]
to an interval of width at most D. Monotonicity of convex secant slopes bounds
each secant on [a,b] in absolute value by 2D/a. Thus the proof does not assume
any uniform log K bound to derive its local Lipschitz constant.

For a general sparse pressure instance, if an independently established
positive anchor P(a)>0 occurs at some
0<a<1, continuity and the negative P(1) anchor give a root in (a,1);
strict decrease makes it unique throughout (0,∞). A finite positive-pressure
profile alone is diagnostic evidence, not an all-time anchor. For the original
pilots the source recurrent-branch argument below now supplies the anchor.

## Derived recurrent branching and positive root for the original pilots

The following source argument now supplies that positive anchor. It applies
to the ORIGINAL 16/20-state parameters on their coarse full-role physical
carrier; it does not need the tighter audited-shell invariance as a lemma.

At pre-update phase 8, the selected lens score L is at most .75: spectral's
window is -.08, similarity's is -.08, and audit's active-window score is
below .65. Every actual P5 physical cluster grouping has two contiguous
halves. Its score at this phase is below .56, using
`phase_signal=.5-sqrt(3)/4`. The return core has at least five indices for
both dimensions, so its mean informant probability is at most 1/5. Its score
is at most `.32+.42/5+.12*.75+.12=.614`.

The budget candidate's score is at least .665:

```
.24+.22 + [.10 b/5+.18(1-b/12)] + .10*.25
  = .665+.005 b >= .665.
```

Support adds a nonnegative term. Protocol_signal is at least .25. Thus its
advantage over every challenger is at least .051, strictly greater than
the maximum original packaging hysteresis .048 and .03 near-best band.
The actual selector deterministically chooses budget packaging at phase 8,
for EVERY admissible stochastic input kernel and legal source noise word.
The chosen core has four entries for d=16 and five for d=20.

Set `a=.07+.03 C >= .08995=1799/20000`. The P1 target gives EVERY row and
EVERY budget-core column a numerator at least a. Its row denominator is at
most `1+5*.10+.05+.03=1.58=79/50`: the source kernel contribution is at
most one, there are at most five core additions, the diagonal core bonus is
at most .05, and any lens diagonal shift is at most .03. Also
`eta >= .08+.05*.665+.02*.6=.12525=501/4000`; source clamping cannot lower
it below this value. Therefore the P1 entry on each such column is at least

```
y=(501/4000)(1799/20000)/(79/50).
```

P2's normalized gate has weight one on core columns and sqrt(.55) outside.
Its normalizing sum is at most one, so it cannot reduce these core entries.
If fallback is used, its .65 multiplier still leaves them at least .65 y;
its added component is nonnegative. No-fallback rows satisfy the same bound.

P6 noise has amplitude at most .0045=9/2000. After clipping, core entries
are at least `.65 y-.0045>0`. The noisy row mass is at most
`1+d*.0045≤1.09`, so the FINAL original update has core entries at least

```
[(13/20)y-9/2000]/(109/100) > 1/10000 = kappa.
```

This is a derived source floor, not an added minorization parameter. It holds
on four or more columns of EVERY row of the kernel that follows phase 8.
It does not assert positivity of all original entries at every time.

P3 cycles phase through all twelve values. Apart from a finite initial
offset, these branching kernels therefore recur once per twelve history
matrices. For 0<s≤1, all other stochastic rows obey `sum_j K_ij^s≥1`.
On a branching step they obey `sum_j K_ij^s≥4 kappa^s`. Nonnegative product
row estimates then give, for EVERY physical starting state and legal future,

```
P(s) >= -s log 10 + [log 4+s log kappa]/12,
```

whenever the shell-sup pressure limit exists. Select floor(n/12)-1 of the
available branching steps (for sufficiently large n); extra branching steps
can use the ordinary stochastic row bound one. The selected count's ratio
tends to 1/12, so the finite initial offset has no effect. This remains valid
even when `4 kappa^s<1`. No sampled infinite trajectory has been substituted
for this phase/branch argument.

Taking kappa=10^-4 and s=1/32 gives

```
P(1/32) >= [log 4-(1/2)log 10]/12 = log(8/5)/24 > 0.
```

Together with P(1)<0 and the proved interior continuity and strict decrease,
this supplies a UNIQUE root in (1/32,1) for every nonempty forward-invariant
instance of this original physical update carrying the declared history
potential. The phase count and positive-root return here are analytic; the
source rational floor is separately mechanized. Original tighter-shell
nonemptiness remains a DIFFERENT missing applicability obligation.

## Why continuity at zero cannot be silently imported

Pointwise positivity, stochasticity and persistent changes alone do not give
continuity at s=0. For a general 2-state moving-kernel example, let X=N,
F(m)=m+1, q=1 and epsilon_m=exp(-(m+2)^2). At even m use
`[[1-epsilon,epsilon],[epsilon,1-epsilon]]`; at odd m use its column swap.
Every kernel is strictly positive and successive kernel differences tend
to Frobenius norm 2, so the kernels keep changing.

For all s>0 the branch row sum is
`exp(-s)[(1-epsilon_m)^s+epsilon_m^s]`, regardless of parity. If 0<s≤1,
the bracket lies between 1 and `1+epsilon_m^s`. Its total log correction is
bounded uniformly in the horizon and start by the convergent series
`sum_m exp(-s(m+2)^2)`. Hence P(s)=-s. If s>1 the bracket is at most one;
starting at m→∞ makes each finite correction tend to one, so the supremum
again gives P(s)=-s. Yet at s=0 every row has two present edges and P(0)=log 2.
This is a counterexample for the general pressure hypotheses, NOT a source
trajectory or an original-shell counterexample. It explains why this repair
proves interior regularity and asks for a POSITIVE-PARAMETER root anchor,
rather than incorrectly invoking continuity from an unproved endpoint bound.

## Outstanding original returns

The matrix pressure conclusions are now valid without optional minorization.
The original full package still needs a nonempty invariant realization of its
audited shell and the exact base/fiber definitions. A genuine positive
conditional-disintegration gap additionally needs conditional-pressure
separation for the SAME declared history potential. The moving 20-state
extension witness demonstrates that strict packaged-family extension alone
does not supply that separation.

## Fresh checks and self-review

The current targeted suite passed 118 tests. Sparse moving paths, absent-edge
s=0 behavior, original selector bounds across all phases on boundary kernels,
and adversarial phase-8 clipping noise are included. The phase-8 source test
covers both original configurations, including identity and absorbing kernels;
it is a regression check, not the general proof. The general source derivation
is given above.

The complete `lake build` passed and the axiom audit covered 160 exports using
only the standard Lean axioms (two declarations need none). These receipts
cover both this module and the original moving-history extension construction.
No sorry, admit, new axiom or native_decide occurs in the four new modules.
No paper file was edited.

Self-review checked selector retention AND stochastic near-best selection,
the base pilot's larger .048 packaging hysteresis, finite-informant mass rather
than stationarity, core cardinalities, gate normalization, clipping mass,
and the use of designated branching times in the pressure lower bound. It
also checked that both source observable variants are retained explicitly.
The original source score/phase bridges and Holder/root assembly remain
analytic; the formal build is not represented as a full simulator proof.
