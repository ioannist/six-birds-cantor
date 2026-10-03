# Actual completion fibers and an original-potential world law

This repairs part of original obligation 4. The paper is unchanged. It constructs
a genuine disintegration whose conditioning objects are actual completion
outputs, rather than a synthetic correction to pressure. It does **not** yet
complete the full continuous-shell theorem.

## Domains and definitions

Use the exact 20-state warm kernels `K+`, `K-` from
`original_loop_extension.py`, at tau=3/5, budget=12, pre-phase 0, with previous
audit/budget selectors. Their current audit completion outputs are the distinct
positive probability vectors `u+`, `u-`. Those vectors, not continuation names,
are the object readout. Their first coordinates differ by

`390467997745347846870000 / 120131948909489644812213124707327077 > 0`.

World `+` uses the previously certified common fixed-half join and 24-step
entry prefix, then the original twelve-cycle. World `-` uses the same join and
prefix, then the cycle obtained by mixing each kernel with the uniform kernel
at parameter 1/100. All formulas and pilot parameters are original. Both cycles
have separately certified all-time continuous thickenings and legal entry
controls. The exact source score containing sqrt(3) is enclosed, not replaced
by the rational score used to choose the join target.

Put probability 1/2 on each world. Conditional on a world, choose microscopic
initial distribution equal to its **actual** audit completion output and use
the original time-dependent stochastic kernels as transition probabilities.
This specifies consistent finite-dimensional path laws, hence a path measure.
The deterministic hybrid dynamics include the future legal input word as before.

For each path define the finite integrand

`W_n(s) = product_t [ A_s(world_t)[i_t,i_(t+1)] / K_t[i_t,i_(t+1)] ]`,

where `A_s[i,j] = (exp(-q_t) K_t[i,j])^s` is the original potential. Positivity
of the kernels makes every denominator legal. Multiplying by reference path
probability cancels the K factors and gives exactly

`Z_sigma(n,s) = u_sigma A_s(world_0)...A_s(world_(n-1)) 1`.

The ratio is a way of integrating the original path weights under a probability
reference; it does not replace the potential with a likelihood or KL potential.
Both different original definitions of q are evaluated separately.

The event `{actual completion output = u_sigma}` is precisely one world atom,
has fixed positive mass 1/2, and its conditional expectation is `Z_sigma`.
Consequently `Z(n,s) = (Z_+(n,s)+Z_-(n,s))/2` at every finite horizon. No rounded
signature, empirical clustering, or changed observable is involved.

The continuation policy is **correlated with the completion output** in this
constructed reference law. This correlation is the source of the conditional
pressure difference. It is an explicit additional construction; it is neither
derived from structural strictness nor claimed for independent noise.

## Pressure existence, exact return, and quantitative separation

Finite legal prefixes do not change pressure: their positive matrix products
and the positive initial vectors bound the periodic-tail partition above and
below by fixed multiples of its maximum row sum. Timescale resets yield exact
twelve-periodic q values; budget=12 remains capped. Each periodic positive
matrix product therefore has a finite pressure limit, and the two-world law
has pressure `max(P_+,P_-)`. Its equal-weight gap is

`Delta(s) = abs(P_-(s)-P_+(s))/2`.

This is also the supremum pressure on the **forward-orbit carrier of these two
worlds**. Every orbit point has one of the two eventually periodic tails.
There are uniformly bounded transient lengths and finitely many tail phases.
Positivity bounds all phase-shift and transient products by fixed multiples
of the corresponding unshifted products. Taking a supremum over orbit points
preserves the maximum of the two tail pressures. This comparison does not
apply automatically to the larger carrier permitting arbitrary Cantor input
words at every phase.

The certificate evaluates s=1/2,3/4,1,5/4,3/2: the union of the two historical
positive pressure grids. For each original q definition, all these gaps are
strictly positive. At s=1, stochastic row sums give pressure exactly equal to
negative mean q and a gap greater than 1/2000. Across both grids and both q
definitions the minimum certified gap exceeds 0.00004846. The original branch
weights lie in [1/1000,4/5], so each pressure is 7-Lipschitz, as is half the
absolute difference. Thus radius 1/1000000 neighborhoods of all these grid
values retain a uniform gap greater than 0.00004.

For noninteger s, the pressure calculation retains the separate diagonal and
off-diagonal weights of all twenty states. Class-constant vectors form an
invariant three-dimensional subspace; each product's twenty-state row norm
equals the aggregate row norm. A positive rational test vector gives lower and
upper ratios `Bv/v` for the twelve-step aggregate product B. Iterating these
inequalities gives exponential lower and upper norm bounds, hence certified
pressure bounds `log(min_i (Bv)_i/v_i)/12` and
`log(max_i (Bv)_i/v_i)/12`. The numerical iteration merely proposes v; no
convergence assumption or eigenvalue approximation supplies the certificate.

The false-target controls matter. At s=0 all present edges have weight one,
so both pressures equal log(20) and the gap is exactly zero. For each original
q, the signed pressure difference is positive at 5/4 and negative at 3/2.
Continuity forces another zero gap between those values. This construction
supports finite grids and neighborhoods, not positivity at every parameter.
Keeping both current completion objects but assigning them a common future
also gives zero gap. Thus distinct completions do not suffice by themselves.

## Base coverage and remaining return

At the two warm states the family identifier, current tau/lens/phase/budget,
prototype data, support data, and all current entrywise row moments agree.
Their global forward-orbit pressure object is common. Hence a base retaining
those current descriptors and the global pressure has an exact collision with
distinct current completion outputs. However, the pointwise **future** pressure
profiles differ. This construction does not put both worlds in one fiber of
the stronger base retaining every pointwise scalar history profile from the
previous strictness witness. That earlier stronger witness remains valid with
a common continuation and a zero two-world pressure gap.

The constructed finite family is the two audit objects **over a common coarse
descriptor**. It is not the three lens-completion objects at one fixed kernel.
`conditional_pressure_disintegration_v1.md` used the former descriptor-fiber
description, while the manuscript and Foundations III also use a family
`F(x)` at a current state. Those meanings cannot be equated without a typed
definition. The receipt keeps this unresolved bridge false.

Next construction: extend the actual package-indexed world law over a Cantor
family while proving that its pressure equals the original continuous-shell
supremum. A candidate is to vary the warm skew magnitude continuously, use its
exact completion coordinate to recognize each object, and use legal periodic
continuations varying over the already certified continuous thickenings. One
must prove the actual object readout and descriptor fibers, construct a full
support reference measure, establish uniform transient comparisons and pressure
continuity, and prove equality of essential-supremum and shell-supremum pressure.
These are mathematical obligations, not fields supplied by this receipt.

## Self-review and mechanization

Premises → actual distinct audit outputs → legal object-correlated worlds →
fixed positive reference weights → exact same-potential finite disintegration
→ independently bounded conditional pressure limits → positive finite-grid gap.

The unresolved return is from this world law/forward-orbit carrier and coarse
base to the paper's single continuous-shell/base/current-family theorem. In
particular, declaring the full shell's global supremum pressure to be the law
pressure without proving equality would smuggle the central missing bridge.

`PackagedDisintegration.lean` proves exact object-fiber masses, conditional
expectations, finite disintegration, nonfactorization from a common base, and
the pressure/gap return. It takes the object distinction and actual conditional
limits as explicit hypotheses. The 20-state instantiation, source-semantic
return, full matrix aggregate identity, and Collatz estimates are analytic
plus exact rational interval evidence, not imported Lean data. Tests compare
the aggregate certificates to independent eighty-digit **full twenty-state**
matrix-vector products and enumerate original-reference finite path sums.

Local sources read: Foundations III, subsections 13.3.2--13.3.6, distinguishes
the strictness witness from the pressure-gap consequence and defines global
pressure by a shell supremum. *To Cast a Stone with Six Birds*, Proposition
`prop:cd-kl` and its proof, requires actual conditional probability laws for its
expected-KL identity; it supplies no implication from strictness to pressure
separation and is not used as a pressure theorem here.
