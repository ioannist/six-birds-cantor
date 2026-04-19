# Lower Pressure Bound v1

## Theorem target
Working target for the lower bound:

> For families in the core subclass
> `safe_finite_memory_local_subclass + lower_pressure_packaging_admissible=yes`,
> if `s < s^L`, then `H^s(K) > 0`, hence `dim_H K >= s`.

Equivalently, the lower-bound program aims at
`dim_H K >= s^L`,
where `s^L` is defined from the lower-pressure object built from fixed packaged stage-`n` geometry.

## Route selected
`cylinder_premeasure_carathéodory`

## Why the other two are not the default right now
- `frostman_style_measure`: would require a cleaner cylinder-to-ball comparison and mass distribution statement than the current core subclass has in hand.
- `gibbs_like_code_space`: this is too close to the equilibrium-measure stage (`T20`) and would force more symbolic/thermodynamic structure than the current theorem program has localized.
- `cylinder_premeasure_carathéodory` is the shortest route from the existing lower-pressure packaging object to a lower Hausdorff-content statement.

## Notation
- `A_n`: admissible words / branches of length `n`.
- `w = i_1 ... i_n`: an admissible branch.
- `K_w`: cylinder image corresponding to `w`.
- `U_n`: fixed packaged stage-`n` geometric family used for lower pressure.
- `Z_n^L(s) = sum_{I in U_n} |I|^s`.
- `P_n^L(s) = (1/n) log Z_n^L(s)`.
- `s^L`: lower root proxy defined from the lower-pressure sequence.
- `mu_n`: cylinder premeasure / stage premeasure built from normalized lower-pressure weights at depth `n`.

## Core subclass
The scaffold currently closes only for the following narrowed core subclass:
- families already in `safe_finite_memory_local_subclass`, and
- `lower_pressure_packaging_admissible = yes`, and
- `fixed_packaging = yes`, and
- `usable_separation = yes`.

This is narrower than the whole primary class. It is meant to cover families where the packaged stage-`n` geometry can be used directly in a Carathéodory-style lower bound without ambiguity from adaptive packaging.

## Witness families
Primary witness family:
- `contextual_local.prefix_memory_no_22_base3`

Control witnesses:
- `classical.middle_thirds`
- `classical.restricted_digits_base5_024`

## Lemma/Proposition chain

### Lemma 1: Cylinder mass / premeasure construction
**Claim.** For fixed `s < s^L` and depth `n`, define a stage premeasure on packaged depth-`n` pieces by
`mu_n(I) = |I|^s / Z_n^L(s)`
for `I in U_n`.
Then `mu_n` is a probability assignment on `U_n`.

**Assumptions used.**
- `uniform_contraction`
- `fixed_packaging`
- `lower_pressure_packaging_admissible`

**Scaffold.**
1. `U_n` is finite by finite-memory / finite-control stage construction.
2. `Z_n^L(s)` is finite and positive for the relevant depths.
3. Normalization gives total mass `1`.

### Lemma 2: Consistency / tightness step
**Claim.** Along a subsequence of depths, the stage premeasures `mu_n` admit a compatible limit object, or at least a Carathéodory lower-content estimate with uniform constants.

**Assumptions used.**
- `finite_memory_bound`
- `stationary_admissibility_rule`
- `feedback_free_admissibility`
- `fixed_packaging`
- `lower_pressure_packaging_admissible`

**Scaffold.**
1. Stationarity and finite memory imply that packaged descendants refine through a bounded family of contexts.
2. This gives a bounded-bridge / quasi-Bernoulli type comparison between masses across nearby levels.
3. Either extract a tight subsequence of stage premeasures, or use those comparisons directly inside a Carathéodory lower-content construction.

**Localized gap.**
The exact bounded-bridge compatibility constant is not yet written uniformly for all core-subclass families, especially the local-domain members.

### Lemma 3: Cylinder-to-ball comparison
**Claim.** For balls `B(x,r)` with `r` comparable to a packaged depth scale, the total premeasure of packaged cylinders intersecting `B(x,r)` is bounded above by `C r^s`.

**Assumptions used.**
- `bounded_distortion`
- `usable_separation`
- `uniform_contraction`
- `lower_pressure_packaging_admissible`

**Scaffold.**
1. Use diameter control to match packaged depth with radius scale.
2. Use separation/overlap control so that only uniformly many packaged cylinders of comparable scale can meet a given ball.
3. Sum their normalized masses and absorb constants into `C`.

**Localized gap.**
For simple local-domain families, one still needs a clean statement that packaged overlaps remain uniformly controlled at the relevant scales.

### Lemma 4: Dimension conclusion
**Claim.** The mass/premeasure control implies `dim_H K >= s` for `s < s^L`.

**Assumptions used.**
- `uniform_contraction`
- `bounded_distortion`
- `usable_separation`
- `fixed_packaging`
- `lower_pressure_packaging_admissible`

**Scaffold.**
1. Use Lemma 1 and Lemma 2 to obtain a consistent lower-content candidate.
2. Use Lemma 3 to compare that candidate with ball coverings.
3. Conclude that any `s`-dimensional cover of `K` must pay a positive lower cost.
4. Therefore `H^s(K) > 0` and `dim_H K >= s`.

## Where the lower bound currently breaks outside the core subclass
- **Overlap / packaging ambiguity:** if `lower_pressure_packaging_admissible` fails or packaging is adaptive, the stage geometry is not stable enough for the premeasure route.
- **Nonstationary admissibility:** the level-to-level consistency step breaks when the branch rule changes with stage.
- **Feedback into admissibility:** runtime state changes destroy the bounded-bridge control needed in Lemma 2.
- **Lack of a clean bounded-bridge / quasi-Bernoulli ingredient:** even in feedback-free local systems, the lower bound does not close unless the packaged cylinders can be compared across depths with uniform constants.
