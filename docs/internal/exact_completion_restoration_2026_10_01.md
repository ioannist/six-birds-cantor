# Exact completion and a declared descriptor-relative extension

This is an exact rational mathematical instance of the implemented lazy
completion. It does not certify floating execution or membership in the
stronger all-time shell. The base descriptor below is explicitly `(K,tau)`;
it omits the active completion package. It is not identified with the paper's
unspecified complete cocycle object or with its rounded empirical descriptors.

## Fixed-package theorem

For a strictly positive rational row-stochastic K, tau>0, a partition G of the
microstates, and nonnegative support weights, use the implemented rational
blend `B=(1-alpha)I+alpha K`, with
`alpha=clamp(22/100+(18/100)min(1,tau/3),18/100,78/100)`.
Let pi_hat be the current finite stationary informant: start uniform,
iterate K at most 80 times, stopping at a consecutive difference <=10^(-12).
Use rational arithmetic and an exact rational threshold. For positive K every
entry of pi_hat is positive. It need not be stationary. On every group G_j set

```
w_i = (55/100) pi_hat_i + (25/100) support_i + (20/100) K_ii,
U_(j,i) = w_i / sum_(h in G_j) w_h   (i in G_j),
Q_(i,j) = 1_(i in G_j),
E = B Q U.
```

All w_i are positive. For any endpoint i,k, at least one h in the group of k
has B_ih>0 and (QU)_hk>0. Thus E is strictly positive and row-stochastic.
Put epsilon=min E_ik>0. If d epsilon<1, write
`E=d epsilon J+(1-d epsilon)R` with J the uniform kernel and R stochastic.
For any zero-mass row vector v, vJ=0 and
`||vR||_1 <= ||v||_1`, by the triangle inequality and row sums. Hence
`||vE||_1 <= (1-d epsilon)||v||_1`. If d epsilon=1 then E=J and the
conclusion is immediate. The probability simplex is complete, E maps it
into itself, and the contraction mapping theorem gives a unique fixed
probability vector p and convergence from every probability input. The
limiting closure C has every row p. Exactly `C^2=C`, `EC=C`, and `CE=C`.
E itself need not be idempotent: limit saturation must be distinguished
from finite-step saturation.

`exact_completion.py` constructs E and p with rational arithmetic, checks
row stochasticity, stationarity, positivity, minorization, and all three
closure identities. The stationary solve uses d-1 equations and mass one;
all d stationary equations are then independently checked exactly. The rational counterpart retains the finite informant, not a substitution by
K's exact stationary limit. The
simulator uses binary float arithmetic;
agreement with its action is tested numerically, not declared exact.

## Concrete witness, retaining the current completion policy

Take tau=1 and

```
K = [[3/5,  1/5, 1/10, 1/10],
     [1/5,  2/5,  1/5,  1/5],
     [1/10, 1/5,  2/5, 3/10],
     [1/10, 1/5, 3/10,  2/5]].
```

Its stationary vector is u=(1/4,1/4,1/4,1/4). Use the simulator's
completion support `support_i=(u_i+K_ii)/2`. For this witness its spectral
core policy picks every state, so after dropping the empty complement
the spectral package is the single all-state cell. Its completion is
constant, with output

```
p_full=(97/336,239/1008,239/1008,239/1008).
```

It is therefore saturated after one step. The current row-similarity
completion routine creates singleton groups (it never merges the scored
pairs). Its completion is exactly B and has the unique fixed vector u.
Thus the existing spectral-to-cluster feedback proposal changes the
completion limit from p_full to u in this fixed-input mathematical instance.
These are different limits of DIFFERENT operators, not two attractors of
one operator. No modification of the clustering policy is hidden here.
For dimensions above six the separate P5 target helper compresses its
singleton list into two contiguous groups; that helper differs from the
completion policy and must not be conflated with it.

Define X={full,singleton}, pi0(g)=(K,1), and pi1(g) equal to the unique
completion limit for g. Then pi0(full)=pi0(singleton) exactly, whereas
pi1(full)!=pi1(singleton). This gives a genuine non-factorization witness
through the DECLARED instantaneous descriptor. `CompletionWitness.lean`
checks stochasticity, the displayed masses, one-step saturation, the
unique mass-one fixed vector of B, and this exact non-factorization.

If pi0 includes the active package/lens, pi1 is determined by pi0 and
factors through it. If pi1 records the entire family over ALL lenses,
that family is already determined by K,tau and also factors through pi0.
If pi0 retains the full future kernel cocycle, lens choices may affect
that cocycle. These alternatives are different theorem objects, not
interchangeable descriptions. The witness does not settle those variants.

For the package {0,1},{2,3}, the B row sums into the first cell from rows
0 and 1 differ by exactly 7/125. This is a genuine strong-lumpability
obstruction, proved in Lean, separate from object non-factorization.
The numerical certificate also computes the unique completion limit for
this two-cell package. A lumpability obstruction does not by itself prove
an extension through any unspecified base map.

## Thermodynamic obstruction survives this exact restoration

Choose constant q>0 and the genuine history cocycle
`A_s=(exp(-q)K)_entrywise^s`. It has the nondegenerate pressure of the
restoration theorem because K has a uniform positive entry bound. Let
`Z_n=||A_s^n||_infinity` and let `Z_(n,p)=p A_s^n 1` for either of the
two completion fixed priors above. Since p is strictly positive,

```
min_i p_i * Z_n <= Z_(n,p) <= Z_n.
```

The normalized logs differ by O(1/n), so both conditioned pressures equal
the global pressure. Any normalized weighted gap is exactly zero, despite
the exact descriptor-relative extension and different completion limits.
`bounded_factor_same_pressure` verifies the limit argument in Lean. The
numerical regression propagates the actual histories, with no entropy offset.

More generally, when every one-step A_s entry lies in [a,b], 0<a<=b,
all rows of `A_s(x) C_(n-1)(Fx) 1` are comparable by a/b. EVERY initial
probability law, including one supported in a proper cell, then gives
`(a/b) Z_n <= Z_(n,p) <= Z_n`, uniformly in x and n>=1. This also passes
to shell suprema. Initial conditioning cannot give the desired gap in
that positive model. Restricting paths at EVERY time is a different valid
operation, with the explicit escape gap in the cocycle restoration note.

The possible preserved endpoint is consequently an explicitly defined
package path-survival theorem. Keeping persistent fixed-point conditioning
requires a different thermodynamic consequence or additional dynamical
structure. Neither change has been silently made to the paper.
