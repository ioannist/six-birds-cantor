# Revised main mathematics: lawful growth and structural pressure blindness

The user accepted this revised direction after the point 4 obstruction audit:
make the central result a lawful continuous construction with a well-defined
growth theory and a strict structural extension; replace automatic positive
pressure disintegration by an explicit limitation theorem. The constructed
positive-gap law remains a secondary existence example. This document fixes
the mathematical definitions for the later manuscript revision. No manuscript
file is changed here. Historical theorem-package ledgers describe the old
target and must not be used as certificates for these statements.

## Domain and update: an explicit controlled shell

Use twenty physical states and the exact-real interpretation of the original
pilot parameters in `continuous_full_loop_kernel_shell.json`. The six original
physical update operations and both original selector observables are retained.
The discrete phase advances modulo twelve. Include the future innovation
sequence in the state, so the original stochastic update becomes a deterministic
skew-product map F consuming its next innovation block.

Let r=1/10^14 and C_r be the scaled middle-thirds Cantor set in [0,r]. The
nominal twelve kernels are the exact rational class kernels in
`configs/mathematics/original_controlled_cycle.json`; physical class sizes are
(5,5,10). At phase k admit targets `(1-lambda)K_k+lambda J`, lambda in C_r,
and the corresponding family with every nominal K_k first mixed 1/100 toward J.
Every successive lambda is a separate input coordinate. Recent selector
records follow the certified phase schedule, tau lies in the corresponding
certified boxes, and budget lies in [3,12]. A target determines its innovation
as target minus the actual source pre-noise update.

Adjoin the two warm kernels K+ and K- below at phase 0, tau=3/5, budget 12,
audit/budget incumbents, the fixed shared half-row joining target R and the
certified twenty-four-step entry prefix into either target family. Include
the complete forward hull of these warm-entry trajectories for every allowed
Cantor word. Call the resulting controlled domain S. A point includes the
bounded physical/selector data and its prescribed future controls. Append-only
diagnostic logs are source realizations, not additional pressure coordinates;
they are not consulted in the physical update or potential.

The all-time inequalities are the checked original-control certificates:
each required innovation has magnitude below its original legal amplitude;
targets are positive stochastic, so clipping and renormalization preserve
them exactly; selector margins preserve the prescribed branch; tau remains
in its phase box; and budget increases until cap 12 and stays within [3,12].
This is a constructed controlled class. No claim of invariance under all
independent random innovations, seeded reachability, or typical occurrence
in the original simulations is part of the revised theorem.

**Theorem R1 (lawful continuous controlled shell).** S is nonempty and forward
invariant under the original skew-product update. Its future-input domain
contains C_r^N, rather than only periodic words. Kernels are stochastic with
all entries above 1/100. Tau and budget stay in their certified ranges.
Kernel variation exceeds the certified positive jump at recurring phases.
Each of the six operations changes a physical update somewhere on the shell
when removed while holding the standardized innovation fixed. This last
property means nonredundancy of the update, not necessity of every operation
for every theorem or every coordinate at every point.

The certificate's finite boxes cover the entire admitted budget, tau and
kernel ranges; induction returns those one-step bounds to all iterates.
The source formula comparison, including selector branches and exact ties,
is part of the analytic derivation. Binary-floating replay is a separate
consistency check, not its proof.

## Growth theory: a specified observable

For each of the two original source observables separately, define

`A_s(x)_ij = (exp(-q(x)) K(x)_ij)^s`, `s >= 0`.

Here K is the pre-update physical kernel and q is the original selector
observable for that transition, with its original clamping. On S,
`log(5/4) <= q <= log(10)`, so every positive branch weight lies in
`[1/1000,4/5]`. Define the ordered cocycle C_s,n(x) by multiplying A_s along
the first n actual updates, with C_s,0=I. The norm is the maximum row-sum
operator norm, not the entrywise matrix norm. Define

`Phi_n(s) = sup_(x in S) ||C_s,n(x)||`,
`P_S(s) = lim_n log(Phi_n(s))/n`.

This multiplicative history observable is the repaired pressure definition.
The old sum over individual times has identically zero pressure and is not
an equivalent definition.

**Theorem R2 (pressure closure).** P_S exists, is finite and continuous for
every s>=0, is strictly decreasing and obeys

`-(t-s)log(1000) <= P_S(t)-P_S(s) <= -(t-s)log(5/4)`, `0<=s<=t`.

Moreover P_S(0)=log(20), P_S(1)<=-log(5/4), and its unique nonnegative zero
lies strictly between 1/3 and 1. Submultiplicativity and forward invariance
give Fekete convergence. Entry bounds give the secants; stochasticity gives
the bound at one; the anchor at 1/3 is at least log(2). This is a theorem
about the declared growth observable, not an unproved Hausdorff-dimension
identification. It does not assert pointwise convergence at every input word.

To see the uniform bounds, put a=1/1000 and b=4/5. For t>=s every
entry satisfies
`a^(t-s) A_s(x)_ij <= A_t(x)_ij <= b^(t-s) A_s(x)_ij`.
Nonnegative multiplication preserves entrywise inequalities, so an n-step
product has the corresponding factors a^(n(t-s)) and b^(n(t-s)). The
maximum row-sum norm and supremum preserve them too. Independently,
`20^n a^(sn) <= Phi_n(s) <= 20^n b^(sn)` gives finite logarithms and a
linear lower bound. The cocycle split, F(S) subset S, and the operator norm
inequality give `Phi_(n+m)<=Phi_n Phi_m`. Fekete therefore supplies the
limit and returns the displayed secants. At zero all matrices are all-ones,
giving exactly 20^n. At one stochasticity gives `Phi_n(1)<=b^n`. At 1/3
every entry is at least 1/10, every row sum is at least 2, and every product
has row sums at least 2^n. These are uniform bounds on the declared S,
not assumptions about a particular word's limiting rate. The opposite
signs, continuity and strict decrease prove existence and uniqueness of
the zero in (1/3,1).

## Completion objects and the exact information forgotten

For a state x with current completion lens l, let

`E_(x,l) = B_tau(K) U_(x,l)`.

B_tau is the actual lazy transport, not a fractional matrix power. U is
the actual block-prototype reinstatement determined by the lens partition,
finite stationary informant, support and diagonal. Positive K and positive
prototype diagonals imply E is a positive stochastic matrix. Let Gamma(x,l)
be its unique stationary probability vector. Every probability start
converges to Gamma under this FIXED completion. The object is not defined
by rounded transient signatures, and different starts of one positive E
do not create multiple fixed objects.

This existence assertion holds throughout S, not just at the warm pair.
The finite informant starts uniformly and each stochastic iterate has every
coordinate at least 1/100, because K_ij>=1/100. The support and diagonal have
the same lower bound. Thus each prototype weight is at least 1/100 and at
most 1; every nonempty cell has total prototype weight at most 20, so
U_jj>=1/2000. The original lazy coefficient is at least 18/100, giving
B_ij>=9/5000. Consequently E_ij>=9/10000000 uniformly. Positive stochastic
contraction gives existence, uniqueness and all-start convergence for every
declared current lens. Empty complementary cells are omitted from the source
partition, rather than divided by zero.

For the base observation D(x), retain the original pilot configuration,
current tau, budget, phase, protocol, active lens, current diagonal/support,
current forget/reinstate operator U, and the two complete growth observations

`(q-observable, s, n) -> ||C_s,n(x)||`, `s>=0`, `n>=0`.

All ingredients are actual observables or declared control data. The base
forgets the labelled off-diagonal kernel and raw innovation sequence. It
retains the full finite-horizon growth observations, not merely a constant
shell pressure or a rounded numerical summary. The extension is

`H(x) = (D(x), Gamma(x,current_lens))`.

Retention of D is the first projection. The unique stationary object at
the current lens is the primary object map. Frozen-input audit-to-spectral
refinement and its genuinely changed fixed object are additional results;
the final forced spectral output alone is not the strictness witness.
Persistence always states its operator: fixed-completion persistence does
not imply that Gamma is preserved under the outer physical update F.

The growth observation is for the prepared future input word carried by the
state. It is not the response to every counterfactual raw-innovation experiment.
The warm pair uses distinct first joining innovation blocks, followed by
common future targets. Omitting the raw innovations from D is explicit;
retaining them or the whole labelled K would change the observation problem.

**Theorem R3 (strict retentive structural extension).** There are points
x+ and x- in S with D(x+)=D(x-) and Gamma(x+,audit)!=Gamma(x-,audit).
Thus no function of D reconstructs Gamma on S, and H is a strict retentive
extension of this specified growth description. This is not a claim that
completion is undefinable from all raw kernel/lens data; those data define
it directly.

The witness starts at the exact tagged/skew kernels from
`original_loop_extension.py`. K-=K+ transpose, with identical labelled-row
entry multisets, diagonal, support and reinstatement. At audit core
{0,4,5,6,7}, the actual B Q U outputs p+ and p- are uniquely stationary,
with the exact nonzero difference

`p+_0-p-_0 = 390467997745347846870000 /
             120131948909489644812213124707327077`.

The tags distinguish the relevant physical indices, and the shared diagonal
observations are retained; no extra random object mark is introduced. The
legal joining controls lead to the same R and subsequent source variables
affecting the cocycle. Auxiliary previous-kernel bookkeeping is overwritten
and does not enter F or q. The initial q values agree for both original
observables. The source-control proof places these warm starts and arbitrary
common future words in the same declared S.

The prepared outer trajectories share their physical successor after the
joining update. Their current object distinction can disappear under F;
R3 concerns structural information at the current state, rather than a
permanent difference between future physical trajectories.

## Replacement for point 4: a pressure limitation

**Theorem R4 (structural differences invisible to growth).** The points
x+ and x- above, with a common allowed future target word after joining,
have identical maximum-row history norms for BOTH original q observables,
EVERY real s>=0 and EVERY horizon n>=0. Their complete history matrices
are equal from horizon two onward. Their current completion objects are
nevertheless different. Hence these growth observations, including any
pressure limits derived from them, do not determine the completion object.

This follows from actual row permutations of K+ and K-, equality of the
first weighted row sums, and equality of rows 0,1,2 of the shared second
weighted matrix. The first-matrix difference is supported on precisely
those columns, so `A_s(K+) A_s(R)=A_s(K-) A_s(R)`. An arbitrary shared
suffix preserves that matrix identity. At horizons zero and one the norm
identity follows directly. This proves the limitation without selecting a
probability law designed to enforce a pressure conclusion.

A common initial microscopic probability gives identical finite path
partitions. Using the two actual stationary vectors as initial microscopic
probabilities can change finite partition values; full-support comparison
still gives the same long-time rate whenever that rate exists. The
common-input disintegration construction is a further zero-gap instance.
It is not needed for the main structural limitation theorem.

## Secondary example and supporting calculation

The earlier correlated reference law is a declared parameter-independent
construction on S. Its actual completion fibers have different pressure
limits at the certified positive grid neighborhoods, and its reference
pressure returns the full-shell supremum. It establishes that a pressure
gap is possible under the specified coupling, not that strict extension
forces it, or that the original independent-noise experiment has that gap.
The positive example uses different prepared future histories. Those worlds
do not share the complete growth descriptor D of R3--R4; the example is not
a thermodynamic consequence inside one fiber of that richer base.

For any fixed finite family of positive-probability fibers of one reference
law and one potential, finite total expectation and existing conditional
limits give `P_reference=max_i P_i`. Therefore the weighted gap is
`sum_i w_i(max_j P_j-P_i)`, and is positive exactly when conditional
pressures differ. This elementary supporting calculation is not presented
as the new scientific contribution. Zero gap certifies equality of these
growth rates, not predictive sufficiency for the whole packaged future.

## Evidence and remaining formal coverage

The controlled source, original warm completion and full-word receipts are
source-bound exact-rational/interval evidence, with analytic source and
all-time return proofs in their notes. The Lean pressure/control lemmas
verify the indicated implications. `TwentyStateData.lean` contains generated
candidate data; `TwentyStateWitness.lean` checks the actual twenty-state
matrix and completion instance independently. Generic matrix/history
identities in `LoopExtension.lean` prove the arbitrary-suffix return.

The exact domain and observation definitions above are the adopted revised
target. They resolve the earlier *definition* choice by explicit user
authorization. They do not turn an analytic source comparison or an interval
instance into a full Lean encoding of the physical update. The accompanying
manifest is generated only after a fresh full build and a transitive axiom
audit covering every requested declaration. It binds every local Lean source,
the toolchain/manifest, this statement and the current constructor receipts.
These checks certify the represented statements within the documented
analytic/formal split. The manuscript's
older F(x) and unnamed audited-shell claims are superseded for future editing;
they are not silently certified by these changed definitions.

This pass's adversarial self-review checked row-sum versus entrywise norms,
current-object versus outer-update persistence, legal input realization versus
independent-noise invariance, common true source observables versus rational
test scalars, finite partitions versus limiting rates, all-word versus periodic
coverage, and positive-prototype well-posedness including empty cells. The
strict witness keeps identical current reinstatement data while forgetting
the labelled off-diagonal kernel; the positive example uses different future
growth descriptors. Neither distinction is supplied by an assumed pressure
gap. This is self-review, not independent review.

The targeted source/certificate suite passed 26 tests across
`test_original_loop_extension.py`, `test_controlled_shell.py`, and
`test_common_input_disintegration_obstruction.py`. Reproduce the Lean/source
binding check with `python scripts/run_revised_main_theorem_package.py` in
the repository's Python environment. The manifest records the actual build
and axiom-audit results rather than copying historical closure flags.
