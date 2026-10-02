# Missing support for the original completion/forcing claim

This work addresses original mathematical obligations, without editing the
paper or introducing a new persistent-memory update law. It follows the user's
instruction to build missing support rather than optional strengthenings.

## Freeze the original target

The paper's preliminaries define a packaged stratum as a persistent element
of the fixed-point structure of E at a given shell state. The canonical object
retains a family of such strata after completion, saturation and lens
refinement. Its strict-extension section requires saturation followed by
material P4<-P5 forcing that produces a new packaged object.

These are fixed-state completion/refinement obligations. Requiring the same
package to survive every outer substrate update was a stronger interpretation
in the earlier follow-up. It is not imposed here. Persistence means invariance
under its corresponding fixed completion operator, with an all-starts limit
and uniqueness. The original smaller-shell membership and the exact definition
of the lower observation map remain separate essential obligations.

## Mathematical saturation support

For a d-state stochastic completion matrix E with E_ij>=epsilon, subtract the
common epsilon entry from every row. If v has zero mass, this subtraction
leaves vE unchanged and the shifted rows have mass c=1-d epsilon. Consequently

```
||vE||_1 <= c ||v||_1.
```

For a mass-one stationary p and any mass-one real starting vector mu, actual
iteration therefore gives

```
||mu E^n-p||_1 <= c^n ||mu-p||_1.
```

For 0<=c<1, every coordinate tends to p. A second mass-one fixed vector would
have distance D<=cD from p, hence D=0. `CompletionDynamics.lean` derives the
contraction, all-horizon estimate, convergence and uniqueness. Neither
convergence nor saturation is assumed. The stationary vector is a visible
input to the general lemma and is explicitly supplied by checked identities
in the concrete application.

For finite candidates the same argument gives the a posteriori estimate

```
||mu-p||_1 <= ||mu-mu E||_1 / (d epsilon).
```

This residual bridge is also proved in Lean. A small consecutive-iterate
difference alone is not a bound of the same size on stationary error.

## Saturation and material forcing on the same exact source witness

`CompletionForcing.lean` applies those laws to the existing exact transpose
pair and the actual B Q U completion formulas, using the finite informant
already verified in `PressureExtension.lean`. The pre-forcing audit completions
have the previously checked stationary vectors p_z and entry floor 1/25.
Thus saturation and uniqueness hold for EVERY real mass-one start, rather
than only the three sampled starts in the old support report.

The source feedback sends a saturated audit lens to the spectral lens. Both
kernel informants are uniform, so the source's spectral-core rule selects all
states. The resulting actual B Q U operator has every row equal to

```
p_spectral = (239/891,226/891,71/297,71/297).
```

Lean computes this formula from the same transport and prototypes. Every
mass-one input maps to it in one step, and it is fixed thereafter. Both p_z
are provably different from p_spectral: forcing is material, and its newly
produced fixed object is persistent under the new operator. The same pre-force
audit transport has the exact non-lumpability defects 7/100 and 21/500.

There is an important return-map distinction. The final spectral output is
the SAME for the two split states and factors through their lower map. It
cannot itself establish strict extension. The original paper retains a FAMILY
of packaged strata. The actual unordered families

```
F_z = {p_z, p_spectral}
```

are different. Lean proves their non-factorization through the SAME existing
scalar-history base: every real entrywise-weighted history partition at every
horizon, the same audit lens and tau, and the same reinstatement operator.
No different stage labels, traversal order or artificial memory variable is
used to create the split. This base explicitly omits the labelled kernel;
identifying it with the paper's incompletely specified exact T0 remains an
original-target bridge, not a conclusion of the new theorem.

The exact example has four states. It is NOT represented as a member of the
historical 16/20-state audited shell. It discharges completion, saturation and
forcing obligations for an actual operator construction, and strengthens the
existing split pair. Original-shell applicability still has to be constructed.

## The missing source feedback step now executes

The original completion panel computed only a next-lens proposal. It recorded
no object produced by the proposed new lens. `apply_completion_feedback` now:

1. requires a numerically converged pre-feedback completion;
2. applies the existing cyclic lens refinement;
3. regenerates the package at the SAME kernel and timescale;
4. completes from the preceding output under the new operator;
5. compares the actual pre/post outputs and their estimated stationary errors.

`compute_packaging_fixed_points` now executes this operation for its panels.
The outer substrate step is unchanged. The old trigger could fire from package
count, entropy, a cycle, or an absent residual; those do not substantiate
saturation and no longer trigger the post-saturation operation.

The floating residual/error comparison remains explicitly numerical: the
minorization and error estimates are not computed with outward rounding, and
the report does not certify exact materiality. Unknown/zero entry floors or
nonconvergent post-completions remain inconclusive. A real lens change with
uniform K supplies a false target: the fixed output stays uniform and is not
counted as a material object change. A deliberately short post-feedback run is
also not counted as material.

The existing support scripts now read actual POST-feedback candidates; they
do not reassign the old signature to a new lens. Exact original-theorem closure
flags remain false. Increasing the original panel's iteration budget to 512
supplies enough computation for its previously unfinished completion runs.
It changes the search horizon, not the dynamics or mathematical claims.

A fresh downstream run also exposed an old test that required the historical
"strict_extension_certified" label to agree with the current diagnostic result.
The historical v2 evidence/verdicts are now archived explicitly. Its current
status and the regenerated audit are diagnostic, with exact factorization
unknown. Tests check those honest scope flags instead of requiring unsupported
historical certification. No mathematical claim is withdrawn solely because
of the new sample; the original-domain proof was already unestablished.

## Original-configuration evidence and remaining children

The completion support was rerun on the two original frozen configurations,
using their original outer update and initializers. Each has 18 pre-feedback
panels and 18 actually evaluated post-feedback completions. The base config
has six numerically separated object changes; the shell config has 18.
Their minimum estimated stationary separations are about 0.0179219 and
0.00140114 respectively. These observations are useful support for the
original feedback assertion, not proofs of an all-time invariant shell.

The compact receipt `results/packaging_completion_endomap/support_summary.json`
records configuration/source/full-report hashes and numerical-versus-formal
scope. The full diagnostic report remains an uncommitted generated artifact.

The essential unresolved applicability children are:

- an exact nonempty invariant realization of the ORIGINAL smaller shell;
- an exact split pair inside that realization for the adopted original T0 map;
- applicability of the completed/refined stratum family and the chosen pressure
  consequence on that SAME carrier, with the original versus repaired path
  potential distinction resolved explicitly.

Outer-loop preservation of a historical package and seed reachability beyond
what the original carrier requires are not added as new obligations. The paper
still needs its own claimed domain and maps; the explicit frozen construction
cannot silently replace them.

## Self-review and validation

Self-review checked all real rather than only rational starting vectors,
residual versus stationary error, pre/post kernel and tau identity, the actual
spectral package constructor, the unordered stratum-family split, final-only
factorization, zero-floor and nonconvergence handling, and numerical versus
exact evidence. This is self-review, not independent review.

Validation: `lake build` succeeded with Lean/mathlib v4.8.0. The fresh axiom
audit covers 93 declarations and reports only standard Lean foundations or
no axioms. The 69 affected mathematical, source and report regressions passed.
The original completion configurations and their downstream strict-extension
diagnostic reports were regenerated. Their exact closure flags remain false.
The compact receipt hashes the current source and generated full report.
`git diff --check` passed, and the paper was unchanged.
# Follow-up: original-target obstructions

The [original shell/disintegration follow-up](original_claim_obstructions_2026_10_02.md)
now supplies an exact 20-state escape from the operational rectangle and a
mechanized all-real-parameter zero-gap result for genuine fixed initial-law
conditioning, even in the actual completion/refinement strict split example.
These are original-support obstacles; they do not complete original-shell
applicability or replace the original pressure by the affinity observable.
