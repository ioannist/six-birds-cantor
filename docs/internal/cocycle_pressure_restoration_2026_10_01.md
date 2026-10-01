# Kernel-history pressure construction

Follow-up: [the all-core construction](all_core_restoration_2026_10_01.md)
supplies a nonempty invariant positive carrier via an explicit optional
minorization repair and proves ideal-noise noncollapse and six-operation
nonredundancy there. The pressure theorem below now applies analytically to
that repaired carrier. The original stronger shell remains an open bridge.

Status: general analytic construction proved under explicit hypotheses;
original-shell and object-map applicability bridges remain open. The theorem below is proved here
under explicit shell hypotheses. Applying it to the full simulator requires
the shell-instance obligations at the end; no sampled run discharges them.
The paper has not been changed. The user authorized this restoration route
on 2026-10-01 after the initial review.

## Genuine history object

Let S be a nonempty forward-invariant state space for F:S->S. The full
six-mechanism dynamics may be used as F; this construction does not replace
it with a finite-state base update. If F uses noise, include the legal
noise sequence/RNG state in S and shift that sequence in F.

For a fixed d>=2, let K(x) be a row-stochastic d-by-d matrix. Assume
`K_ij(x)>=kappa>0` and `0<q_min<=q(x)<=q_max<infinity` for all x,i,j.
The q observable is attached to the actual selected lens/packaging/budget
state; its uniform bounds are explicit hypotheses. Define

```
r_ij(x) = exp(-q(x)) K_ij(x),
A_s(x)_ij = r_ij(x)^s,
C_n(s,x) = A_s(x) A_s(Fx) ... A_s(F^(n-1)x),
a_n(s,x) = ||C_n(s,x)||_infinity,
Phi_n(s) = sup_{x in S} a_n(s,x),
P(s) = lim_n log(Phi_n(s))/n.
```

For nonnegative matrices the infinity operator norm is the maximum row
sum. Expanding the product shows that a_n is the maximum, over initial
microstates, of the sum over all length-n kernel histories of
`product_t r_{i_t,i_(t+1)}(F^t x)^s`. This is a real history partition,
not the old sum over observation times. Summing over initial microstates
instead would change it by a factor between one and d; hence the pressure
is unchanged. These branch weights define a thermodynamic potential.
No geometric Hausdorff dimension conclusion is asserted without a separate
geometric coding, contraction, and separation bridge.

## Pressure theorem and proof

Set `r_min=exp(-q_max) kappa` and `r_max=exp(-q_min)<1`. Both bounds are
uniform over S. For every s>=0, entries of A_s lie between r_min^s and
r_max^s, so

```
(d r_min^s)^n <= a_n(s,x) <= (d r_max^s)^n.
```

The lower bound follows by applying each positive matrix to the all-ones
column and inducting on the minimum row sum; the upper bound is the same
argument with the maximum row sum. Consequently Phi_n is positive finite
and its logarithm is bounded above and below linearly in n.

Cocycle multiplication and the norm inequality give

```
a_(n+m)(s,x) <= a_n(s,x) a_m(s,F^n x),
Phi_(n+m)(s) <= Phi_n(s) Phi_m(s),
```

where the second inequality uses forward invariance. Fekete's lemma gives
existence and finiteness of P(s). This argument uses a supremum over all
legal states, not an estimate from one sampled trajectory. The comparison
has no uncontrolled finite-horizon defect.

For t>=s>=0, every length-n path acquires a factor between
`r_min^(n(t-s))` and `r_max^(n(t-s))`. Entrywise positivity, row summation,
the supremum, and the limit therefore give

```
(t-s) log(r_min) <= P(t)-P(s) <= (t-s) log(r_max)<0   (t>s).
```

Thus P is globally Lipschitz on `[0,infinity)` and strictly decreasing.
At s=0 all A_0 are the all-ones matrix, so `Phi_n(0)=d^n` and
`P(0)=log d>0`. At s=1,

```
C_n(1,x)=exp(-sum_{t<n} q(F^t x)) product_{t<n} K(F^t x).
```

The kernel product is row-stochastic and has infinity norm one. Hence
`-q_max <= P(1) <= -q_min<0`. Continuity and strict monotonicity give a
unique zero `s_* in (0,1)`. This restores genuine nondegeneracy and the
root-supporting regularity missing from the time-sum construction.

## Relative pressure from actual packaging fibers

Let a completion package supply a measurable/deterministically assigned
partition of the microstates at each x. Fix a tracked fiber label j with
nonempty proper cell Sigma_j(x) at every x in S; use a fixed finite label
set with no disappearing cells. Let D_j(x) be its diagonal indicator.
Define the restricted cocycle

```
B_(s,j)(x)=D_j(x) A_s(x) D_j(Fx).
```

Products of these matrices count exactly the histories which stay in
that tracked packaging fiber at every step. They are not autonomous
stratum systems and they are not ordinary conditioning solely on x at
time zero. The covariance of the final projection is essential to the
cocycle identity and the ensuing Fekete argument. Define Phi_(n,j) by
the supremum of the corresponding row norm and P_j by its logarithmic
growth. Nonempty cells and positive entries give a linear lower bound,
so submultiplicativity again gives a finite true limit.

At a fixed s choose uniform `0<a<=A_s(x)_ik<=b`. For any two consecutive
matrices A,A' and any proper intermediate cell Sigma, put D=1_Sigma.
For each endpoint pair i,k,

```
(A A')_ik = (A D A')_ik + sum_(h outside Sigma) A_ih A'_hk,
sum_(h outside Sigma) A_ih A'_hk >= a^2,
(A D A')_ik <= d b^2.
```

It follows, entrywise, that

```
A A' >= (1+delta) A D A',   delta=a^2/(d b^2)>0.
```

Including endpoint projections can only decrease the restricted matrix.
Pair consecutive steps, multiply nonnegative matrix inequalities, and
handle one remaining step by A>=D A D'. This proves

```
a_n(s,x) >= (1+delta)^floor(n/2) a_(n,j)(s,x),
P(s)-P_j(s) >= (1/2) log(1+delta)>0.
```

For any normalized nonnegative package weights w_j,

```
Delta(s)=P(s)-sum_j w_j P_j(s) >= (1/2) log(1+delta)>0.
```

On a bounded parameter window `[0,S_max]` one may use
`a=r_min^S_max`, `b=1`, so the bound is uniform in s and in shell states.
This is a dynamical escape/return estimate, not an inserted entropy
offset and not an implication from non-factorization alone. The false
target of one all-state cell does not satisfy the proper-cell hypothesis;
then D=I, B=A and the gap is zero, as required.

For uniform K and constant q the calculation is explicit:
`P(s)=log d-s(log d+q)`. A constant cell of size k<d has
`P_j(s)=log k-s(log d+q)`, so its gap is `log(d/k)>0`.
The diagnostic module tests this by actual matrix products and an
independent enumeration of short histories.

The phrase "conditional disintegration" still requires care. The quantity
above is a weighted comparison of genuine global and fiber-survival
pressures. It is not a Rokhlin measure-disintegration identity, nor does
it establish statistical sufficiency of T0 for every packaged future.
Its link to the paper's persistent completion-stratum fibers remains an
explicit mathematical bridge to be established; substituting microstate
partition fibers for those strata must not be hidden in a renamed symbol.

## Open shell and object-map obligations

1. The actual simulator can clip entries to zero. The positivity bound
   kappa has not been proved for its original audited shell. Options to
   examine are a legally retained positive subsystem, a uniform bounded
   mixing-time version of the proof, or an explicitly regularized kernel
   update. No regularization is silently applied to the original F.
2. The stronger lawfulness shell still needs all-time preservation and a
   nonempty realized instance. Conditional assembly must keep those
   premises visible. Enabled primitive flags do not prove necessity.
3. Specify the exact T0 object. If it retains the full kernel/lens data
   determining the completion package, the old E-derived fixed-point
   family is definable from T0. Exact strict extension requires an
   independently retained packaging distinction or a genuinely coarser
   base object and an exact collision certificate.
4. A fixed positive completion matrix has a unique fixed distribution.
   The meaningful T1 object may have to retain its entire completion
   operator and package structure, not treat transient numerical outputs
   as distinct fixed points. The relation to saturation and forcing needs
   an actual pre/post operator or persistent-object comparison.
5. Map the package fibers used in the relative-pressure theorem to the
   intended completion object. This bridge is independent of the analytic
   escape estimate and cannot be supplied by strict extension alone.


## Implementation and mechanization receipts

The numerical history module expands and multiplies the actual microstate
history weights. Independent short-history enumeration, explicit uniform
kernel pressure/root formulas, excluded-path gaps, stochastic s=1 identities,
and the genuine initial-conditioning negative control are tested.
`run_kernel_history_pressure_checks.py` samples unrounded kernels of the full
six-mechanism update and declares its bounded positive selector potential.
Its first packaging cell is tracked at each step, including the endpoint;
it does not report this as a persistent fixed-point stratum.

`KernelCocycle.lean` checks the split identity and derives submultiplicativity
of the supremum before applying Fekete. `KernelEscape.lean` checks the local
positive matrix comparison and the limit-gap transfer given the paired
comparison. The analytic proof above supplies the pairing and parameter/root
arguments; their matrix instance and complete endpoint assembly are not
claimed as fully Lean-mechanized. All checked declarations use only standard
Lean foundations, without `sorryAx` or project-specific axioms.
