# Mathematical audit formalization

Build with `lake build` in this directory. The portable dependency manifest
pins Lean and mathlib to v4.8.0. The review used the matching local mathlib
cache; no local filesystem paths are present in the committed manifest.

The adopted revised main target is now specified in
[the revised theorem package](../docs/internal/revised_main_theorem_package_2026_10_03.md).
`TwentyStateWitness.lean` checks the original-dimensional warm kernel data,
their actual lazy prototype completion, the stationary objects and their
all-start convergence/uniqueness. It derives identical weighted history norms
at every horizon with an arbitrary common suffix and proves nonfactorization
through the whole stated growth descriptor. The rational candidate data are
regenerated from the existing constructor; the Lean kernel checks the proofs.
`CompletionObject.lean` constructs global stationary objects from positive
transport/prototype bounds. Physical source realization and interval instance
bounds remain analytic and are distinguished from this mechanization.

The notes below record the successive historical repair stages. Their open
original-shell obligations and surrogate scopes are preserved for provenance;
the adopted controlled-domain statements above are the current target.

## Historical formalization notes

`ControlledShell.lean` supplies clipping/normalization return for legal target
corrections, the actual four-phase timescale reset bounds, budget invariance,
and all-time induction. Its pressure endpoint gives a unique root in (1/3,1)
from explicit original-potential bounds. The actual 20-state controlled
carrier and score guards are separately checked by exact outward rational
interval arithmetic; they are not imported as Lean data. See
`../docs/internal/controlled_original_shell_2026_10_03.md` for the precise
real-arithmetic, controlled-input, and original-base scope.

`PackagedDisintegration.lean` conditions a binary world law on its actual
object-valued readout, proves the finite law of total expectation and the
conditional pressure limits, and returns a quantitative gap from a separate
pressure-separation input. The current 20-state instance uses exact audit
completion outputs and two certified original-potential continuations. Its
constructed input law, coarser current-state base, and forward-orbit pressure
are explicit. It does not establish the original independent-noise law or
identify its pressure with the entire continuous shell supremum. See
`../docs/internal/packaged_world_disintegration_2026_10_03.md`.

`WeightedHistoryBounds.lean` proves shared-positive-vector bounds for arbitrary
nonautonomous products and returns them to maximum row norms. This supports
uniform pressure bounds over every legal Cantor input word, rather than only
periodic examples. `ReferencePressure.lean` proves that arbitrarily small
exponential losses suffice for a fixed reference law to reproduce envelope
pressure, with loss-dependent prefactors; it also formalizes geometric and
interval bounds. The existing binary object-valued conditioning theorem uses
the actual audit-completion outputs at one common active lens and base descriptor.
The continuous-shell instance is certified by rational intervals.
Its single parameter-independent reference law uses Schreiber's subadditive
variational theorem analytically, together with compactness, Jensen and
positive source-realization comparisons. These measure constructions and the
interval datasets are not imported Lean proofs. See
`../docs/internal/all_word_pressure_disintegration_2026_10_03.md`.

`CommonInputDisintegration.lean` integrates the actual row-history bounds under
one common input measure, proves the conditional pressure return and derives
zero gap alongside structural nonfactorization. The original twenty-state
controlled instance uses the same shell, potential and actual audit outputs as
the positive-gap construction, with a common mixture of lawful futures. It
still matches the full-shell supremum. Thus supplying that missing pressure
return cannot make strictness alone imply a gap. The source and measure inputs
remain analytical instances, while the integral/limit argument is mechanized.
See `../docs/internal/common_input_disintegration_obstruction_2026_10_03.md`.

`LoopExtension.lean` now also handles a first-matrix difference supported on
selected columns when only the corresponding second-matrix rows agree. This
supports the original small-budget split and its common evolving tail without
requiring a globally rank-one second kernel.

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
# Original-target obstruction checks (2026-10-02)

`ConditionalPressure.lean` proves exact finite initial-law disintegration of
the same positive matrix path potential and derives a common pressure for all
initial probability laws, including those with zero coordinates. It then
combines the actual B Q U completion/refinement split with an identically zero
original-potential weighted gap, for every real parameter. This prevents
structural strictness from being used as an unsupported scalar-separation
bridge. The 4-state operator countermodel does not certify membership of the
original 16/20-state invariant shell.
It also proves the correct two-fiber mixture pressure law and the exact
criterion for a positive gap: different conditional pressure limits. Those
limits must be derived from a genuine disintegration; object strictness alone
does not establish their inequality.

`FiniteDisintegration.lean` proves the corresponding return for any fixed
finite family with positive probabilities. The logarithmic pressure of the
total partition is the largest conditional pressure. The weighted gap is
nonnegative, vanishes exactly when all conditional pressures agree, and is
positive exactly when two of those pressures differ. A quantitative deficit
at one fiber gives a quantitative lower bound. Actual conditional partitions,
their limits and a return to the shell supremum remain explicit instance
obligations. See [the point 4 import audit](../docs/internal/point4_pressure_return_and_import_audit_2026_10_03.md).

`PrimitiveCompletion.lean` removes one-step positivity from the completion
saturation argument: a positive finite power suffices. It CONSTRUCTS stationary
existence from a Cauchy sequence, proves full convergence including remainder
steps, uniqueness, a block-residual error bound, and an idempotent limiting
closure. It proves the return through the actual B Q U prototype constructor
and the positive-path certificate implication. `completion_support.py` records
exact support paths on the original 16/20-state snapshots; the real input
normalization and full seeded-shell exclusions are explicit in the follow-up.

`HistoryConditioning.lean` proves initial-law/norm comparison for arbitrary
nonautonomous nonnegative history matrices. At s=1 it proves exact
initial-law independence for the original weighted stochastic cocycle,
including initial distributions with zero coordinates.

`OriginalShell.lean` proves selector isolation, the variance bound and the
clamped timescale escape of a uniform 20-state warm state under the original
parameters. The full Python-to-formula bridge is analytic, not mechanized;
seed reachability and arbitrary invariant-subclass nonexistence are not claimed.
See `docs/internal/original_claim_obstructions_2026_10_02.md` for exact coverage.

`LoopExtension.lean` proves the moving-history bridge: equal first-step row
moments and one shared rank-one second matrix give equal full products at
all later horizons and equal scalar growth profiles at every horizon. The
original-parameter 20-state warm construction is exact rational Python plus
an analytic source bridge; original infinite-shell membership remains open.

`SparsePressure.lean` derives finite pressure existence and strict decrease
from nonnegative stochasticity and bounded positive q, without a positive
entry floor. It keeps zero edges absent at s=0. The original recurrent budget
branch supplies a derived core floor and positive anchor at s=1/32, giving a
unique root in (1/32,1). Interior regularity, phase counting and the source
branch bridge are analytic; survival of its floor through clipping noise is
mechanized. Original tighter-shell applicability remains open.
