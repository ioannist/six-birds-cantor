# Equilibrium Measure Program v1

## Decision
- Thermodynamic core decision: `reduced_from_t19_class`
- The T19 Bowen class is reduced to a smaller subclass that admits a finite-state irreducible coding with a common contraction ratio along allowed edges and disjoint cylinder geometry after pushforward.

## Core class
- Core subclass ID: `markov_equal_ratio_affine_subclass`
- Description: families in the T19 class whose admissible branches are represented by an irreducible finite-state graph, with edge ratio `r` independent of edge, exact cylinder packaging, fixed lens/packaging, feedback-free stationary admissibility, and disjoint cylinder geometry on the attractor.
- This contains the current witness families:
  - `classical.middle_thirds`
  - `classical.restricted_digits_base5_024`
  - `contextual_local.prefix_memory_no_22_base3`

## Route selected
- Route: `markov_parry_style_measure`
- The default argument is constructed on code space and then pushed forward to the attractor.

## Measure construction
Let `A` be the irreducible adjacency matrix of the finite-state presentation, with Perron value `lambda > 1`, left/right Perron vectors `u,v > 0`, normalized by `sum_i u_i v_i = 1`. Let `P_{ij} = A_{ij} v_j / (lambda v_i)` be the Parry transition matrix and `pi_i = u_i v_i` the stationary law.

For a cylinder `[w_0 ... w_{n-1}]` on code space, define
`nu([w_0 ... w_{n-1}]) = pi_{w_0} P_{w_0 w_1} ... P_{w_{n-2} w_{n-1}}`.
This gives a consistent shift-invariant Markov probability measure `nu`. Push it forward by the coding map `pi_code` to obtain `mu = (pi_code)_* nu` on the attractor `K`.

Because the class has exact cylinder packaging and disjoint cylinder geometry, cylinder images in the attractor match code cylinders up to uniformly bounded geometry, so `mu(K_w)` is controlled by the Markov cylinder weight and the coding map is finite-to-one with no overlap ambiguity inside the class.

## Exact dimensionality statement
For `mu` on any family in `markov_equal_ratio_affine_subclass`, the local dimension exists for `mu`-a.e. `x` and is constant:

`dim_loc(mu, x) = h_mu / chi_mu = s_*`

for `mu`-almost every `x`, where `s_*` is the Bowen root from T19 restricted to this subclass. Hence `mu` is exact dimensional and `dim_H mu = s_*`.

## Entropy/Lyapunov formula
On code space, Shannon-McMillan-Breiman for the irreducible stationary Markov chain gives
`-(1/n) log nu([w_0 ... w_{n-1}]) -> h_mu`.
Since every edge contracts by the same ratio `r`, the Lyapunov exponent is
`chi_mu = -log r`.
The Perron relation gives `lambda r^{s_*} = 1`, hence
`s_* = log lambda / (-log r)`.
For the Parry measure, `h_mu = log lambda`, so

`dim_H mu = h_mu / chi_mu = log lambda / (-log r) = s_*`.

## Witness families
- `classical.middle_thirds`: one-state full shift with `lambda = 2`, `r = 1/3`, so `h_mu = log 2`, `chi_mu = log 3`.
- `classical.restricted_digits_base5_024`: one-state full shift with `lambda = 3`, `r = 1/5`, so `h_mu = log 3`, `chi_mu = log 5`.
- `contextual_local.prefix_memory_no_22_base3`: finite-state adjacency with Perron value `phi`, common ratio `r = 1/3`, so `h_mu = log phi`, `chi_mu = log 3`.

## Why any reduction is necessary
The T19 class only guaranteed Bowen-formula coincidence through exact cylinder packaging and disjoint cylinder geometry. That is enough for the dimension identity, but not yet enough for a canonical equilibrium measure with exact dimensionality on the whole class.

The reduction is needed because measure existence and `h_mu / chi_mu` require, in the current proof route, a genuine irreducible finite-state coding with a stationary Parry law and a single edge ratio. Without that reduction, one still needs an additional quasi-Bernoulli / thermodynamic-limit argument not yet closed in-note for the wider T19 class.

## Outside the proved class
Still outside this thermodynamic core subclass:
- families in the T19 class lacking a clean irreducible finite-state presentation;
- families with nonconstant edge ratios unless one upgrades to a more general thermodynamic-limit or Gibbs construction;
- stage-dependent / nonstationary families;
- any family with admissibility or packaging depending on runtime feedback;
- local-domain systems where cylinder-to-ball comparison is not presently controlled by the disjoint symbolic coding route.

## Why the other routes are not the default right now
- `explicit_cylinder_gibbs_measure`: plausible on the wider T19 class, but current note does not close consistency/exact-dimensionality there without extra quasi-Bernoulli input.
- `thermodynamic_limit_construction`: more flexible, but strictly heavier than needed for the current witness families and not the shortest route to a proved note-level theorem now.
