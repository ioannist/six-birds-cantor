# Concrete matrix pressure and completion-gap mechanization

This pass strengthens the mathematics and Lean only. The paper is unchanged.
It follows [the all-core construction](all_core_restoration_2026_10_01.md) and
does not declare the four original theoremlets restored.

## Endpoints now mechanized

`lean/MatrixPressure.lean` uses mathlib's **explicit maximum absolute row-sum
operator norm**. The default entrywise matrix norm is not substituted for it.
For any inhabited state carrier X, update F:X->X, and nonnegative d-by-d
matrix field A, assume the ONE-STEP row sums lie in [a,b], uniformly in X,
with a>0 and finite b. Actual ordered multiplication gives, for every n,

```
a^n <= sum_j (A(x) A(Fx) ... A(F^(n-1)x))_ij <= b^n.
```

Lean derives both bounds, proves their connection to the concrete operator
norm, and applies the previously verified cocycle/Fekete theorem. The finite
pressure limit of the state supremum therefore exists. Uniform exponential
history bounds are no longer supplied as independent assumptions at this
matrix endpoint. F maps the declared carrier into itself by its type; this
does not prove that a numerical simulator preserves a proposed shell.

For a FIXED strictly positive finite matrix M, Lean also constructs finite
positive entry bounds from the minimum and maximum entries. For any initial
probability p, including p with zero entries, its actual history partition

```
Z_n = sum_i p_i (M^n 1)_i
```

is between (a/b)||M^n||_infinity and ||M^n||_infinity. At positive horizons the
comparison follows from the first matrix step; at horizon zero both partitions
are one. Thus the pressure of Z_n exists and agrees with the norm pressure.
This also strengthens the mechanized initial-conditioning obstruction: a
strictly positive initial density is unnecessary in this finite positive case.

For strictly positive stochastic E and R, put T_ij=sqrt(E_ij)sqrt(R_ij).
Given a positive common bound

```
lambda <= (sum_j |E_ij-R_ij|)^2/8   for every row i,
```

Lean derives 0<1-lambda, the exponential all-horizon partition bound, pressure
existence, and Q<=log(1-lambda)<0 together. No pressure limit or exponential
pressure-gap-shaped premise is assumed. The remaining input is the specific
one-step discrepancy, whose derivation for the actual example follows below.
The reference stochastic channel has pressure zero, and equal channels have
T=E and zero pressure. For every normalized nonnegative package weighting,
the weighted gap is at least lambda; zero package weights are allowed.

## Concrete B Q U application

`lean/CompletionAffinityWitness.lean` imports the exact transpose split pair
from `PressureExtension.lean`. Its completion operators have already been
proved equal to the actual B Q U formulas, rather than supplied as arbitrary
tables. Their p_z are the exactly verified rational stationary distributions;
the new file also proves stationarity after casting to real probabilities.
The earlier uniqueness mechanization is over rational vectors. Uniqueness
over arbitrary real probabilities follows analytically from positivity; the
new pressure-gap proof does not assume or need that uniqueness conclusion.

The shared stationary predictor is explicitly

```
R_ij = (p_false,i E_false,ij + p_true,i E_true,ij)
       / (p_false,i + p_true,i).
```

Lean proves positivity and stochasticity of R and E_z, the initial probability
conditions, and the exact all-rows discrepancy bound

```
lambda = 3283594060761 / 134912463042781250
       ~= 0.0000243387007152909.
```

The exported `completion_affinity_witness_gap` constructs the two actual
pressure limits and proves their weighted gap is at least this lambda for
EVERY probability weighting on the pair. The source's Fraction computation
independently returns exactly the same lambda; the regression test checks this
bridge. This is a concrete theorem application, not only a generic conditional
pressure lemma.

## Exact scope and remaining core work

The potential is the previously declared relative-likelihood PATH potential.
These are frozen completion-channel histories. This result does not turn
initial conditioning of the physical K histories into a positive pressure gap,
identify the original unspecified measure disintegration, or establish that
outer F preserves its earlier package. The hybrid tensor-product construction
and the simulator-to-state-carrier bridge remain analytic.

Likewise, the branch-weight-to-parameter-secant bridge remains analytic;
`PressureRegularity.lean` derives the unique zero from explicit secant and
endpoint inputs. The new finite-matrix theorem removes the abstract normed-ring
instantiation gap for pressure EXISTENCE, without claiming a full formalization
of the parameter family or simulator.

The highest-value remaining construction is a persistent package under the
outer loop, with material feedback and the same precisely declared lower
observation map. The present stored P5 package is overwritten at the next
step. A distinct frozen readout by itself cannot establish persistent packaged
future distinctions. Simply storing an extra label is insufficient: its
evolution, completion readout, and feedback must preserve a real distinction.
If feedback changes the physical future, that future may reveal the package;
the observation map and the timing of the extension must therefore be fixed
before asserting non-factorization. A pre-intervention base and a
post-intervention base are different theorem targets.

After that construction, the remaining original-domain tasks are reachability
from the historical initializer and preservation of its smaller shell. A
single end-to-end theorem must connect those domain facts, pressure closure,
strict extension, saturation/forcing, and the chosen consequence endpoint on
the SAME system. The present results are useful proved components, not a
substitute for those bridges.

## Self-review and verification

The separate self-review checked the norm instance, horizon-zero comparison,
zero entries in the initial probability, the strict positivity used in taking
logarithms, the realized rational predictor, all-row loss rather than a
single-row loss, and the changed path potential. No independent review is
claimed. All proof exports are included in the transitive axiom audit; only
standard Lean foundations are permitted. Build and test results are recorded
after running the checks for this revision.

Validation: `lake build` passed with Lean/mathlib v4.8.0. The fresh expanded
axiom audit covers 73 declarations with only standard foundations or no axioms.
The 20 affected pressure, completion, and cocycle regression tests passed.
The 96-step scoped receipt was regenerated; its original-theorem closure flag
remains false. The paper was unchanged, and `git diff --check` passed.
