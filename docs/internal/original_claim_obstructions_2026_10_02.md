# Original-target support: shell and pressure obstructions

This pass addresses missing support for the original first and fourth theoremlets.
It introduces no new thermodynamic observable and makes no paper edits. Its
results are obstructions that a faithful original-target repair must overcome.
The original theorem package is still incomplete.

## Original rectangular-shell control fails

The executable shell checker in `scripts/run_forward_invariant_regime_checks.py`
uses budget `[2.1,12.1]`, tau `[0.55,1.05]`, both selector margins at least
`0.01`, and all six enabled flags. These inequalities alone do not define a
forward-invariant domain under the original law.

Use the ORIGINAL 20-state pilot parameters, without the optional kernel
minorization repair, and take the following warm state:

- `K_ij=1/20`, `tau=21/20`, `budget=3`, `phase=0`, protocol `boot`;
- incumbent spectral lens and partition-cluster package;
- empty lens/package switch history; all six primitives enabled.

This is a legal warm state of the original update law. Published-seed
reachability is **not established**. Nor is membership of this state in a
stronger, unspecified invariant subclass carrying additional all-time
noncollapse restrictions. The conclusion concerns the operational rectangle.

The finite informant is exactly uniform in real arithmetic. Entropy is
`log 20`, row similarity and flow balance are one, support and diagonal are
`1/20`. Actual P5 compresses its twenty singleton similarity groups into two
ten-state groups; the cluster core contains all states. Source scores are:

| Candidate | Exact score |
| --- | --- |
| spectral lens | `731/1600` |
| similarity lens | `7/20 + sqrt(2)/40` |
| audit lens | `45197/400000` |
| cluster package | `3671/5000 + 7 sqrt(3)/200` |
| recurrence package | `427325/1000000` |
| budget package | `121/250` |

The elementary bounds `sqrt(2)<3/2`, `sqrt(3)<7/4` isolate both winners by
more than `0.03`, exceeding the stochastic tie band and both original
hysteresis thresholds. Thus this selection is independent of the random
input. Both margin requirements hold.

Write `L=731/1600`, `a=L/50`, and `D=17/10+a`. Each P1 target row has one
diagonal entry `(3/20+a)/D`, nine other within-group entries `(3/20)/D`, and
ten cross-group entries `(1/50)/D`. The rewrite strength is
`eta=101/1000+C/20`, where `C` is the cluster score, so
`0 <= eta <= 141/1000`; the source clamp does not change it.

P2 viability is `(6/25)(21/40)=63/500`, below `0.18`. All-state core membership
makes its row gate a constant factor that cancels in normalization, after
which P2 blends `0.65` of the P1 row with `0.35` of the uniform fallback.
Consequently the actual pre-noise Frobenius variation `v` satisfies

```
v^2 = 20 ((13/20) eta)^2 * [
       ((3/20+a)/D-1/20)^2
     + 9 ((3/20)/D-1/20)^2
     + 10 ((1/50)/D-1/20)^2 ]
    <= 4098392922882739/830905171600000000
    < (3/40)^2.
```

There is no switch penalty. Since `v<0.12`, the P3 pre-clamp update is

```
tau' = 21/20 + 33/2500 - (17/100) v
     >= 21009/20000 = 1.05045 > 1.05.
```

It lies between `0.6` and `4`, so the original clamp preserves the exit.
P6 kernel noise occurs AFTER P3 and cannot prevent it. The ordinary source
replay gives `tau'=1.0512825927393918`, lens margin `0.07151966094067258`,
and package margin `0.31082177826491075`. Those floating values corroborate
the source/formula bridge; they are not the exact certificate.

Lean `OriginalShell.lean` proves selector isolation and eta bounds, the
variance bound, and the clamped tau escape. The mapping from the full Python
state to these formulas is the explicit analytic calculation above, not a
formalized Python operational semantics.

**Repair consequence.** A phase/history-dependent invariant subset might
still exist inside these bounds. It must be constructed and shown nonempty;
finite trajectories and the rectangular inequalities do not supply it.
Broadening the domain to the already repaired positive carrier establishes a
different theorem and cannot silently close original-shell applicability.

## Fixed-law conditioning cannot provide the fourth theorem

Fix a finite strictly positive matrix potential `A_s`, with the ORIGINAL
path weights throughout. For an initial probability law `p`, define

```
Z_p(n,s) = p A_s^n 1.
```

If `a <= A_s(i,j) <= b` and `a>0`, then for every probability law `p`, even
one containing zero coordinates,

```
(a/b) ||A_s^n||_infinity <= Z_p(n,s) <= ||A_s^n||_infinity.
```

Entry positivity makes the rows comparable after the first step. The
geometric row-sum bounds and the submultiplicative matrix norm give a finite
pressure limit. The bounded multiplicative factor disappears after applying
`log` and dividing by `n`. Thus a SINGLE pressure is shared by EVERY `p`.
This is derived, not assumed, in
`CantorAudit.initial_conditioning_common_pressure` in
`ConditionalPressure.lean`.

For fixed package probabilities `w_h` and initial laws `p_h`, let
`p_bar=sum_h w_h p_h`. The genuine finite disintegration is exactly

```
Z_p_bar(n,s) = sum_h w_h Z_p_h(n,s).
```

One can realize it probabilistically by first sampling a package label,
sampling its initial state, and evolving the SAME physical Markov kernel.
The original weighted history sum is a Feynman--Kac observable under this
joint law. Conditioning the label changes the initial law, not the kernel or
the path potential. There is no per-step entropy offset. The global mixture
and every conditional component have the same pressure, so

```
P(s) - sum_h w_h P_h(s) = 0
```

identically. Lean proves the exact disintegration, common limits, uniqueness
of any extracted profiles, and zero weighted gap.

### Actual B Q U completion countermodel, not a label-only example

The existing positive 4-state transpose pair has exactly equal scalar
history objects at EVERY parameter and horizon, a nonfactorizing family of
completed fixed objects, convergence from every mass-one input, material
audit-to-spectral forcing, and an exact macro-admissibility defect. These
were established in `PressureExtension.lean` and `CompletionForcing.lean`.

Use its distinct audit and post-forcing fixed laws as `p_h`, while keeping
the existing witness's physical potential `A_s(i,j)=(K_ij/2)^s`, with frozen
`q=log 2`. This has the original branch-potential form; it is not a replay
of the full-loop selector observable along an original seeded trajectory.
The generic common-pressure theorem applies to any strictly positive matrix
potential, regardless of this illustrative scalar choice.
No completion channel replaces
the physical kernel. Both transpose choices share the same pressure for
every real `s`, by equality of their uniform history partitions and the
all-initial-laws result. The weighted gap is identically zero for ANY
probability weights on the two fixed objects.

At `s=1`, the stronger identity is exact at every horizon:
`Z_p_h(n,1)=2^(-n)`, since the physical weighted matrix has row sum `1/2`.
For other `s`, finite conditional sums need not agree, but their limiting
pressures do. The tests check both behaviors and exact mixture identities.
The full all-real-parameter result is mechanized as
`strict_completion_with_common_original_pressure` and
`original_strict_completion_zero_gap`.

This is an exact countermodel to the claimed **structural-to-scalar
inference** in the operator/completion package. It is NOT a claim that this
4-state frozen carrier is the original invariant 16/20-state full-loop shell.
It shows why strict extension, saturation, material forcing, and profile
well-definedness cannot by themselves establish the asserted consequence.
Original-shell dynamics would need an additional pressure-sensitive fact.

## What a claim-preserving repair now requires

There is also positive original-target support for the missing disintegration
law. Lean `binary_disintegration_pressure` proves that if
`Z(n)=w Z_0(n)+(1-w) Z_1(n)`, `0<w<1`, and both positive component partitions
have pressure limits `P_0,P_1`, then the global pressure limit is
`max(P_0,P_1)`. Its companion theorem proves

```
max(P_0,P_1) - [w P_0+(1-w) P_1] > 0  iff  P_0 != P_1.
```

The mechanism is explicit: `min(w,1-w) max(Z_0,Z_1) <= Z <= max(Z_0,Z_1)`;
the maximum partition has pressure `max(P_0,P_1)`, and the bounded factor
disappears in the limit. Conditional PRESSURE separation is necessary here;
independent stratum ROOT separation is not asserted. This is a valid general
closure law, not evidence that the original package supplies its inputs.
For a finite family the same argument gives the maximum over active fibers.

It also sharpens the exclusion of the earlier affinity construction. The
reference partition has pressure zero, but all affinity partitions have
strictly negative pressure. Their fixed-weight mixture has negative pressure,
so it cannot equal the reference partition. That result is a valid relative
pressure comparison and cannot be renamed a disintegration of one partition.

The fourth theorem's proof step 3 needs an independent bridge from object
strictness to thermodynamic separation. Its four listed premises do not
supply such a bridge. Under fixed-law conditioning the proposed bridge is
actually false, not merely unmechanized.

There are two substantive routes:

1. Specify a genuine original-potential conditioning law on persistent
   history fibers, with normalized weights and an exact finite-horizon
   disintegration. Independently prove pressure separation on the ORIGINAL
   invariant shell. The existing finite family of full-support fixed laws
   does not provide such path restrictions. This could retain a positive-gap
   main claim, but requires a new target-specific construction.
2. State the positive-gap theorem conditional on independently established
   thermodynamic separation, and keep structural strict extension as a
   separate theorem. This changes a main theorem materially; it is not an
   automatic local repair.

The previous affinity-pressure/KL constructions deliberately change the path
observable. They remain valid scoped results but are not a repair of this
missing original support. We have not adopted either route or altered the
paper. The rectangular-shell obstruction may be repairable by a proper
invariant subset; it is not a nonexistence theorem for all such subsets.

## Reproduction and validation

Run `scripts/run_original_claim_obstructions.py` using the project Python
environment. Its compact report records exact rational bounds, floating
original-source replay, exact finite partition checks, file hashes and
coverage exclusions. Build the entire Lean library and run `AxiomAudit.lean`
for fresh kernel checking and transitive axiom evidence. Validation receipts
below refer to this pass, not the older support runs.

Fresh validation: the full `lake build` passed; 81 selected Python tests
passed (original obstruction checks plus the existing matrix/completion,
retained-memory, continuous-source and strict-extension regression tests).
The axiom audit checked 111 exports, using only `propext`, `Classical.choice`,
`Quot.sound`, or no axioms. The compact obstruction report's input hashes
matched the current sources. No paper files changed.
