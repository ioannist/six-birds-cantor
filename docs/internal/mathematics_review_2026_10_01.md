# Mathematical review, 2026-10-01

## Scope and status

Baseline: commit `60e9096`, the clean checkpoint requested before review.
The manuscript and its claims have not been edited. This review supersedes
the evidentiary reading of the historical `closed_in_note`, `closed`, and
`narrowed_and_proved` flags: those flags are workflow decisions, not proofs.
The original `lean/` contained only `.gitkeep`. The new audit formalization
is described in `lean/README.md`; it does not certify the four main claims.

The review traced the four manuscript theoremlets through their internal
notes, dependency ledgers, diagnostic builders, and mathematical Python
modules. It also examined the earlier upper/lower, bounded-overlap,
induced-return, and certification branches. Independent agents were not
used. The final adversarial pass is self-review.

**Main-claim disposition:** substantive repair is required. Preserving the
title-level strict-extension claim is a research question, not an achieved
result. The pressure and thermodynamic claims cannot be restored with the
current pressure definition and current implication alone. A replacement
pressure object or a material narrowing of the conclusions needs an
explicit mathematical scope decision. The user authorized pursuit of research
repairs on 2026-10-01. The restored history-pressure theorem and exact
completion witness below are independent of the still-open identification
with the paper's original object maps and conditioning endpoint.

## Four main theoremlets

### Lawfulness / forward invariance: conditional content, uncertified instance

Locations: `paper/sections/04_lawfulness.tex`,
`forward_invariant_lawful_regime_v1.md`, and
`scripts/run_forward_invariant_regime_checks.py`.

The paper assumes shell preservation, persistent activity, and noncollapse,
then concludes substantially those properties. This is valid as a conditional
assembly only when the premises have exact meanings. The supporting note
instead declares shell preservation from finite sampled trajectories and
selector ranges. No inequality proving `F(S_aud) subset S_aud` for all
states, or all admitted random inputs, is supplied. Membership is not an
explicit all-time mathematical definition with a demonstrated nonempty
realized class. Turning membership into "trajectories which remain lawful"
would make preservation tautological and still require nonemptiness.

The code uses stochastic tie-breaking and independent kernel noise. A
deterministic F must include RNG state or a noise sequence in its domain,
or be stated as a random/skew-product update. A finite fixed seed is not
a theorem about all such inputs. Primitive flags mean enabled operations;
they do not prove persistent causal activity. Score gaps are distinct from
absolute winner scores and hysteresis margins. Knockouts which delete the
definition of a switching variable need additional target-coupled evidence
to establish scalar or object necessity.

Retained content: normalized finite nonnegative rows, bounded tau and
budget by explicit clamps, and well-defined updates for legal finite input
data. Global ranges `[0,12]` and `[0.6,4]` are directly built into updates;
the stronger selector/persistent-variation shell is not thereby invariant.
Repair: specify the full state/noise domain, a genuinely preserved set,
and a nonempty example; prove each required inequality or explicitly
retain nondegeneracy and noncollapse as premises.

### Cocycle pressure: implemented object has zero pressure

Locations: `continuous_pressure_existence_v1.md`,
`continuous_pressure_closure_v1.md`,
`scripts/run_continuous_pressure_checks.py::_pressure_proxy`,
`scripts/run_continuous_pressure_closure_checks.py::_fekete_proxy`, and
`paper/sections/05_cocycle_pressure.tex`.

The implementation and closure note use

```
Z_n(s) = sum_{t=1}^n exp(-s q_t),  P_n(s) = log(Z_n(s))/n.
```

For `|q_t| <= M`, at every fixed real s,

```
n exp(-|s|M) <= Z_n(s) <= n exp(|s|M).
```

Thus `P_n(s) -> 0`, uniformly on bounded s-windows. The same bounds hold
after taking the supremum over any nonempty shell with uniform M. There
is no nondegenerate pressure or unique root. The new Lean proof verifies
the general positive linear-growth bound and the actual time-sum formula
for nonnegative bounded q and s. The signed version follows from the
displayed elementary bounds and the same proved general lemma.

The advertised "equivalent branch-summed version" is not equivalent. A
sum over length-n histories with additive n-step potentials has different
growth and needs a defined history space, weights, concatenation rule,
and uniform estimates. The paper suppresses the formula for `a_n`, so it
does not resolve the implemented object's degeneracy.

Originally `_subadditivity_defect` computed `whole - (left + (whole-left))`,
identically zero. Consecutive changes of `log Z_n/n` are also not Fekete
comparison defects. Finite small errors prove no all-horizon comparison.
Monotonicity alone proves neither continuity nor a root sign change.

Retained content: genuine Fekete convergence conditional on explicit
uniform almost-subadditivity and a linear lower bound. This conditional
lemma is now proved in Lean. Repair of the nontrivial target requires a
new multiplicative cocycle/history partition object; it cannot be obtained
by relabeling this time-sum.

### Strict extension: no exact fixed-point collision supplied

Locations: `strict_theory_extension_closure_v1.md`,
`scripts/run_strict_theory_extension_closure_checks.py`,
`scripts/run_packaging_completion_endomap.py`,
`src/contextual_cantor/continuous_kernel_substrate.py`, and
`paper/sections/06_strict_extension.tex`.

The valid criterion is an exact witness `p0(x)=p0(y)` and `p1(x)!=p1(y)`.
That criterion is now proved in Lean, including the converse with an
inhabited output carrier. Rounded descriptor collisions establish only
failure to factor through the rounded descriptor itself. The exact T0
map is not specified at the requisite level, and per-family pressure
values are copied into every completion panel rather than attached to
each shell state. The new coarse-readout counterexample verifies the
logical distinction.

More seriously, all final iterations were counted as fixed points. In
the frozen first witness there were 15 nonconvergent runs, two numerically
fixed runs, and one rounded-cycle run among 18. In the second there were
16 rounded-cycle runs and two numerically fixed runs. Different transient
signatures do not supply different persistent fixed-point strata. Binning
at seven decimals can declare a cycle while a contraction is converging.
The saturation assertion `distinct_count <= 3` for three starts is true
by construction and proves no saturation. Lens-change proposals are
recorded without iterating the new map to compare pre/post objects, and
repeated signatures across tau panels do not prove persistence in time.

For a fixed partition/prototype set the completion is linear stochastic:
`E(mu)=mu B_tau Q U`, where B_tau is the implemented lazy blend, not
`K^tau`. If `B_tau Q U` is strictly positive, its Doeblin contraction gives
a unique fixed probability vector. Indeed if every entry is at least
epsilon>0, write A as `d epsilon J + (1-d epsilon) R`, with J uniform
and R stochastic (the endpoint A=J is immediate). On zero-mass row
vectors the J term vanishes and R is l1 nonexpansive. The contraction
factor is `1-d epsilon<1`. Therefore uniqueness, rather than multiple
mu-dependent strata, is expected in this positive fixed-panel case.
Positivity has not been certified for every frozen panel; this is a
conditional obstruction, not a claim that all those panels are positive.

Macro admissibility was tested using a top-level `package_count` absent
from iteration summaries; the default zero made every result false.
Even supplying that metadata would test convergence and package count,
not macro-dynamic closure. The correct strong-lumpability criterion is
equality of block transition sums for rows in the same source block.
Failure of that criterion does not itself prove non-factorization of a
packaged-object map through T0.

Repair: pin exact T0 and T1 maps, construct two realized lawful states
with exactly equal base objects, and certify separated persistent
completion objects. If T0 retains all K/tau/lens data used to define the
fixed-point family, that family already factors through T0; a theorem
must identify precisely which mathematically meaningful information is
forgotten. Changing that information is a change of theorem scope.

### Conditional disintegration: the claimed implication is false

Locations: `conditional_pressure_disintegration_v1.md`,
`scripts/run_conditional_disintegration_checks.py::_stratum_pressure_profile`,
and `paper/sections/07_conditional_disintegration.tex`.

The code does not restrict a cocycle partition to a packaging fiber. It
defines a synthetic profile from a final probability signature p by

```
P_p(s) = P0(s) + log(sum_i p_i^(1+s))/support(p).
```

For a single fiber with uniform p on m states, the synthetic gap is
`s log(m)/m > 0` for s>0, while the information deficit is exactly zero.
The global P0 cancels out. This is an inserted Renyi-moment correction,
not a consequence of strict extension or a pressure disintegration.
The new regression exercises this one-fiber negative control. The
second frozen witness even had zero minimum KL proxy and zero descriptors
with a KL signal above its threshold, yet was labeled closed from the
synthetic gap. Such comparisons do not prove thermodynamic insufficiency.

The theorem's four stated assumptions do not imply nontriviality. Take
two states, constant T0, distinguishing T1, and all pressure profiles
identically zero, with normalized fiber weights. Strict extension holds
and the gap is zero. This counterexample is now checked in Lean. Object
non-definability does not force the chosen scalar pressure to separate
objects. Defining "sufficiency" to mean zero synthetic gap supplies no
bridge to standard conditional-information sufficiency.

Repair: define real conditional partition profiles on specified fibers
and supply a target-coupled strictness assumption or a constructive
example proving the chosen profiles actually differ. A disintegration
claim also needs a specified measure, measurable fibers/conditional laws,
and a justified relation between global and conditional pressures.
Positive moment offsets and finite frequency weights cannot replace
those inputs. A fixed positive all-shell bound requires a uniform
estimate; a finite parameter grid supplies no such estimate.

## Supporting branches

1. **Upper Hausdorff bound.** The cover argument is valid for s>0 given
   actual all-depth covers, diameters tending uniformly to zero, and
   negative limsup pressure. The limsup itself supplies eventual
   exponential decay, so the extra finite-memory/Fekete lemma is not
   needed for this implication. This does not construct a lower measure.

2. **Lower premeasures.** Normalizing stage weights gives finite
   probability assignments; it does not give consistent cylinder masses.
   Stationarity and finite memory alone do not establish a uniform
   quasi-Bernoulli bridge, especially for reducible graphs, restricted
   starts, or partially defined maps. Compactness can give subsequential
   probability limits on a compact ambient space, but a Frostman bound
   must be uniform and survive that limit. Unequal contraction scales
   require stopping cylinders, not a single fixed word depth. The gaps
   acknowledged in `lower_pressure_bound_v1.md` remain live in later
   notes which reuse that route as if closed.

3. **Coalesced overlap.** The advertised all-s>=0 inequality follows
   neither from pointwise multiplicity nor from finite memory. The new
   `bounded_overlap_repair_2026_10_01.md` supplies counterexamples and a
   corrected bounded-chain proof retaining pressure coincidence for the
   stated digit witnesses. General lower dimension still needs a measure
   construction/separation proof.

4. **Induced returns.** `run_delayed_return_diagnostics.py` truncates at
   RETURN_CAP=5 and treats a cylinder merely intersecting the core as a
   return of the whole word. Same-core start/end alone does not make all
   return blocks freely concatenable: partial domains may restrict the
   next block. The product formula `Z_ind=Lambda^n` requires full-domain
   return maps or a proven full-shift coding, not just a return label.

   In witness a3, f0 maps `[0,1/5]` into `[11/50,3/10]`, the waiting map
   f1(x)=(7/20)x+9/50 preserves that interval, and f2(x)=(2/5)x maps it
   into `[0,1/5]`. The waiting interval is disjoint from the core.
   Consequently `f0, f1 repeated k times, f2` is a first-return path of
   length k+2 for every k, and f1 may also be used forever. The rational
   waiting and return invariants are proved in Lean. Thus a3 is not the
   claimed bounded-return witness. Its return images can overlap; a
   countable alphabet pressure upper bound is not automatically its
   Hausdorff dimension. The full-core/bounded-entry transfer assumptions
   are unverified and cannot be inferred from finite searches.

5. **Perron computations.** Unshifted power scaling can oscillate for
   periodic matrices (e.g. `[[0,4],[1,0]]`), and reducible/Jordan cases
   can return an unconverged scale. The corrected implementation uses
   communicating components and shifted iteration with numerical
   Collatz bounds and explicit failure on nonconvergence. These are
   floating estimates, not certified intervals. Transfer matrices now
   respect reachable start states and distinct restricted digits.

6. **Interval certification.** Setting `mp.mp.dps` does not set
   `mp.iv.dps`; nearest-rounded float exports can shrink enclosures;
   arbitrary mpf/float margins are not proven error bounds. Certification
   now requires an actual interval evaluator, uses/restores interval
   precision, and exports outward-expanded endpoints. Classical digit
   ratios are evaluated as exact 1/base; the family-specific Fibonacci
   reduction verifies its configured adjacency before use. Contextual
   reference values are no longer attached to unrelated configurations.
   Collatz integer bounds require nonnegative integer matrices and
   positive test vectors. The general finite-state dimension interpretation
   still requires an actual geometric coding/separation hypothesis.

## Implemented repairs and validation scope

The new `tests/test_mathematical_regressions.py` uses mathematical negative
controls for periodic/reducible spectra, unreachable components, interval
exports, fake certification, unfinished fixed-point iterations, rounded
cycles, genuine lumpability, invalid probability vectors, the single-fiber
synthetic gap, and switch penalties. The code now reports convergence as
numerical and separates it from certified fixed points and saturation.
It measures selector margins inside the actual simulated step, removing
an extra RNG draw from the forward-invariance diagnostic. Exit counts
are measured, not hardcoded. Switch costs/penalties compare the prior
selection instead of the already-appended current selection. Finite
time-sum evaluation is stable under large s, and the former tautological
subadditivity diagnostic evaluates the actual two sums.

These fixes change sampled results; historical reports and manuscript
ledgers must not be regenerated and presented as equivalent proof receipts.
The synthetic pressure profile is explicitly labeled as such; preserving
the historical v1 compatibility fields does not certify their decisions.
The current claim ledger now marks all four original main claims as requiring
mathematical repair. Historical dependency flags are explicitly scoped as
workflow provenance. Diagnostic builders cannot certify the main theorems,
and the Level-3 builder refuses to regenerate a closed ledger from those flags.
The paper source is unchanged.

## Concrete restoration choices

**Research restoration:** define a true multiplicative cocycle/history
partition and prove the uniform comparison/parameter estimates; replace
transient panel splitting with exact non-factorization witnesses and
certified completion separation; define genuine conditional profiles and
prove a target-coupled positive gap. Retain lawfulness as an honest
conditional shell statement until a nonempty preserved regime is proved.
This can preserve a strict-extension title, but is substantive new work
and may require changing the mathematical objects. There is no proof yet
that the current full six-primitive model realizes all of these targets.

**Current-object route:** retain the time-sum and prove its zero pressure,
retain finite completion/selector diagnostics with their corrected scope,
and state non-factorization only conditional on exact witnesses. Remove
the implication from structural extension to thermodynamic strictness.
This requires material weakening of main claims, including the current
unconditional strict-extension presentation. It is not silently adopted
by this review.

## Adversarial self-review

The audit proofs do not assume the desired shell, exact collision,
separation, or nonzero gap. The conditional Fekete result exposes its
uniform comparison and lower-bound inputs. The factorization converse
handles the otherwise missing inhabited-output requirement. The
zero-pressure proof covers the actual time-sum rather than a substituted
branch pressure. The a3 proof is an exact domain invariant, not an
extrapolation of a larger numerical cutoff. Floating convergence and
rounded candidate counts remain explicitly separate from mathematical
existence, uniqueness, and fixed-point certification.


## Restoration achieved under exact stated scopes

See `cocycle_pressure_restoration_2026_10_01.md` for the analytic kernel-history
pressure theorem: finite existence, strict monotonicity, Lipschitz continuity,
and a unique zero in (0,1), under a nonempty forward-invariant state domain,
positive uniform kernel entry bounds, and positive bounded selector potential.
`KernelCocycle.lean` derives envelope submultiplicativity from actual cocycle
multiplication and proves the finite limit with the exponential bounds exposed
as premises. `KernelEscape.lean` proves the local two-step matrix escape
inequality and its transfer to a pressure gap given a paired comparison.
The all-horizon matrix pairing, parameter regularity, and root are proved
analytically in the note, not claimed as fully mechanized endpoints.

`exact_completion_restoration_2026_10_01.md` and `CompletionWitness.lean` give
an exact rational fixed-point witness for the explicitly chosen instantaneous
base (K,tau), a one-step saturated completion operator, the unique stationary
vector of another package, and an exact strong-lumpability defect. This is not
an exact collision of the original unspecified full cocycle objects on the
stronger audited shell. No such instance bridge has been proved.

A further obstruction is now proved: bounded positive initial conditioning
does not change pressure (`bounded_factor_same_pressure` in Lean). For uniformly
positive history matrices even initial probability laws with zeros give a
uniform bounded-factor comparison after the first step. Thus initial fixed-point
conditioning cannot supply the desired strict pressure gap. The alternative
path-survival gap is a valid different endpoint with an explicit proper-cell
hypothesis; it has not been silently identified with persistent fixed-point
stratum disintegration.

The new sampled history-product driver uses actual unrounded kernels from
both original full-update configurations, with a declared positive bounded
selector potential. In 64 steps the first configuration already has a zero
kernel entry, while the second has a positive sampled minimum. Neither run
certifies a positive uniform all-shell lower bound. The identity at s=1 is
verified to floating error around 10^(-14). Paper files remain unchanged.

Validation: 74 focused mathematical/numerical tests passed before the final
additional initial-conditioning regression. The broad pre-migration suite
returned 233 passed and 10 failed in 2533.66 seconds; all failures asserted
paper wording that was already absent, and the paper was not changed. That
run also exercised publication artifacts whose obsolete closure statuses
are now explicitly quarantined. It is not a receipt for the final repaired
tree. Final focused test/build results are recorded at the end of this note.


Final validation of the repaired tree: **90 passed in 15.76s** across the
mathematical regressions, history-pressure and exact-completion tests,
classical/symbolic/transfer/interval/local-pressure modules, and the updated
core diagnostic/ledger checks. `lake build` succeeds for all four proof
modules. `lake env lean AxiomAudit.lean` reports only standard foundations
or no axioms for all audited declarations; no `sorryAx` or custom axioms.
Internal JSON documents parse and `git diff --check` passes. The manuscript
and its generated publication files were not edited. Publication assembly
from the obsolete closure flags is intentionally blocked by the mathematical
audit guard pending actual main-theorem repairs; the old paper phrase tests
were not rewritten to conceal their ten pre-existing failures.

No material reinterpretation of the original fixed-point conditioning endpoint
has been adopted. The alternative proven path-survival endpoint is separately
named. The substantive remaining decision is whether to use that endpoint,
seek another thermodynamic consequence on the original fixed-point strata,
or retain the original gap as an open research claim.
