# Mathematical audit formalization

Build with `lake build` in this directory. The portable dependency manifest
pins Lean and mathlib to v4.8.0. The review used the matching local mathlib
cache; no local filesystem paths are present in the committed manifest.

`CantorAudit.lean` proves:

- Exact equal-base/different-extension witnesses obstruct factorization.
- With an inhabited output carrier, factorization is equivalent to being
  constant on exact base fibers.
- A collision of a further coarse readout need not obstruct factorization
  through the original base object.
- Strict object extension does not imply a nonzero weighted pressure gap.
- Fekete convergence is valid given explicit all-horizon comparison and
  lower-bound hypotheses. Those hypotheses are not verified for the
  simulator.
- Positive linear-growth partition sequences have zero logarithmic growth;
  in particular the implemented bounded-observable time-sum has zero pressure.
- The exact rational waiting map of frontier witness a3 preserves its
  waiting interval for arbitrarily many iterations and permits return
  afterwards.

`KernelCocycle.lean` additionally defines a genuine product over forward
iterations, proves its split identity, derives submultiplicativity of its
state supremum, and proves the finite logarithmic limit under visible uniform
exponential bounds. Its normed-ring interface is abstract; the concrete
maximum-row-sum matrix instance is now supplied in `MatrixPressure.lean`,
with its exponential bounds derived from one-step row estimates.

`KernelEscape.lean` proves the positive two-step matrix escape estimate,
transfers an explicit even-horizon comparison to a pressure gap between
existing limits, and proves that bounded-factor initial conditioning leaves
pressure unchanged. The all-horizon matrix pairing and the pressure family's
parameter continuity/unique root are proved analytically in the restoration
note, not claimed to be fully mechanized here.

`CompletionWitness.lean` proves exact stochasticity, completion/prototype
formula bridges, one-step saturation for the all-state package, unique
stationarity for the singleton package, and a non-factorization witness
through the **declared instantaneous descriptor (K,tau)**. It also proves
the exact strong-lumpability defect 7/125 for a two-cell package. It does
not certify membership in the original stronger shell or identify that
descriptor with the paper's unspecified full cocycle object.

These are audit and repair lemmas with declared scopes, not mechanizations of the
paper's four main theoremlets. `AxiomAudit.lean`, checked with
`lake env lean AxiomAudit.lean`, prints their transitive axioms. The outputs
contain only standard Lean foundations (`propext`, `Classical.choice`,
`Quot.sound`), or no axioms, and no `sorryAx` or project-specific axioms.

The next constructive pass adds:

- `KernelLawfulness.lean`: exact stochasticity after clipping/normalization
  for d sigma<1, a uniform positive floor for the explicit minorization
  repair, clamp bounds, and the finite-difference identity underlying the
  analytic almost-sure noise noncollapse proof.
- `PressureRegularity.lean`: Lipschitz continuity, strict decrease, and a
  unique zero in (0,1), derived from the pressure family's secant bounds
  and endpoint signs. The matrix-to-secant bridge is still analytic.
- `PressureExtension.lean`: transposition preserves EVERY total frozen-kernel
  history partition at EVERY horizon and real entrywise weight function.
  A concrete same-lens/same-package example has different uniquely stationary
  completion limits. The base keeps the entire reinstatement operator but
  explicitly omits the labelled kernel. This is a stronger scalar-object
  witness than the previous (K,tau)-descriptor example, with a different base.
- `RetainedMemory.lean`: stationarity transfers within-cell reinstatement
  ratios to fixed distributions; changing a prototype against a common
  positive anchor forces a split. Exact midpoint noise recouples two preimages.
  The complete actual-P5 source construction and its equality of full future
  cocycles are proved analytically in the new restoration note, rather than
  claimed as fully mechanized here.
- `AffinityPressure.lean`: Cauchy--Schwarz gives an explicit row loss for
  relative-likelihood history weights, and that row loss implies exponential
  loss of the actual partition at every horizon. This supports the new
  weighted affinity-pressure gap, with its changed path potential explicit.
- `MatrixPressure.lean`: instantiate the operator norm for actual finite
  nonnegative matrix products; derive all-horizon bounds and pressure existence
  from one-step row bounds. For a fixed positive matrix, prove existence for
  every initial probability law, including laws with zero entries. Combine
  existence with the affinity row loss to obtain strictly negative pressure,
  the weighted positive gap, and zero-pressure stochastic/equal-channel controls.
- `CompletionAffinityWitness.lean`: apply those theorems to the actual B Q U
  operators of the transpose split pair, their stationary laws, and their exact
  common predictor. Prove an explicit rational lower bound on the weighted
  pressure gap for every probability weighting. No pressure limit, exponential
  gap, or row discrepancy is assumed for this concrete instance.

See [the matrix-pressure follow-up](../docs/internal/matrix_pressure_mechanization_2026_10_01.md)
for its precise scope. The potential is changed and the completion channels
are frozen. Simulator bridges, the parameter-to-secant bridge, persistent
outer-loop packages, and the historical smaller shell remain open.

`CompletionDynamics.lean` and `CompletionForcing.lean` now support the original
fixed-state completion/refinement obligations: derive l1 contraction from an
entry floor, prove all-starts convergence and real fixed-point uniqueness,
and instantiate the actual pre/post audit-to-spectral operators. The new fixed
object persists under its own completion. The unordered family of pre/post
strata is a genuine split of the existing scalar-history base; keeping only
the final output is a proved factorizing false target. Original-shell
membership is still open. Outer-loop package retention is a stronger possible
continuation, rather than an imposed extra requirement for this repair.
See [the original-completion support note](../docs/internal/original_completion_support_2026_10_02.md).

See [the all-core construction note](../docs/internal/all_core_restoration_2026_10_01.md)
for exact carrier changes, the stronger actual-P5 memory split pair,
counterfactual necessity of all six operations, surviving thermodynamic
obstructions, new consequence candidates, and remaining original-shell bridges.

The rational a3 statements interpret the displayed decimal map parameters
as exact rationals. They prove a waiting-domain invariant and return
availability. The accompanying review explains why the domain disjointness
and initial transition make these genuine arbitrarily long first-return
paths. They do not establish a dimension formula for that local IFS.
