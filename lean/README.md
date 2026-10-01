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
exponential bounds. Its normed-ring interface is abstract; no simulator
instance or matrix operator-norm instance is smuggled into the file.

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

The rational a3 statements interpret the displayed decimal map parameters
as exact rationals. They prove a waiting-domain invariant and return
availability. The accompanying review explains why the domain disjointness
and initial transition make these genuine arbitrarily long first-return
paths. They do not establish a dimension formula for that local IFS.
