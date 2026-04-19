# Induced Pressure Existence v1

## Decision
- `pressure_closed_for_working_class`

## Class on which pressure is proved
- Proved pressure class: `bounded_return_delayed_gate_subclass`

No narrowing is needed for the pressure step. On this class, bounded return times plus stationary finite local-domain data make the first-return alphabet finite, and the induced pressure reduces to a finite weighted return-block partition function.

## Induced partition sums
Fix the delayed-return core `C` and let `\mathcal R` be the set of first-return blocks to `C`.

For `s \ge 0`, define the return-block weight
\[
\varphi_s(w) = |a(w)|^s,
\]
where `a(w)` is the contraction product along the return block `w`.

Define the one-step induced weight sum
\[
\Lambda(s) = \sum_{w \in \mathcal R} \varphi_s(w).
\]
Because the class has bounded return times and only finitely many local maps, `\mathcal R` is finite. Because `strict_return_contraction` holds, each `\varphi_s(w)` is finite and strictly decreases in `s`.

Define induced depth-`n` partition sums by
\[
Z_n^{ind}(s) = \sum_{(w_1,\dots,w_n)\in \mathcal R^n} \prod_{j=1}^n \varphi_s(w_j).
\]
Since each return block begins and ends on the same core, concatenation is exact, so
\[
Z_n^{ind}(s) = \Lambda(s)^n.
\]

## Subadditive / bounded-bridge estimate
The working class gives a stronger statement than bounded-bridge almost-subadditivity:
\[
\log Z_{n+m}^{ind}(s) = \log Z_n^{ind}(s) + \log Z_m^{ind}(s).
\]
So the bounded-bridge constant is `C = 0` on the proved pressure class.

This uses:
- `delayed_return_core_exists`
- `bounded_return_times`
- `stationary_local_admissibility`
- `local_domain_compatibility`
- `induced_alphabet_control`

The first four guarantee a well-defined finite return alphabet. The last one guarantees this is the intended class notion rather than an accidental witness-only property.

## Pressure existence theorem
Because `Z_n^{ind}(s) = \Lambda(s)^n`, the induced pressure exists as a true limit:
\[
P_{ind}(s) = \lim_{n\to\infty} \frac1n \log Z_n^{ind}(s) = \log \Lambda(s).
\]
So the pressure is not only a limsup or subadditive envelope; it is an explicit finite-sum pressure for the working class.

## Monotonicity and continuity in s
For each fixed return block `w`, the map `s \mapsto |a(w)|^s` is continuous and strictly decreasing because `strict_return_contraction` holds. Since `\mathcal R` is finite, `\Lambda(s)` is continuous and strictly decreasing, and hence so is
\[
P_{ind}(s) = \log \Lambda(s)
\]
on the region where `\Lambda(s) > 0`, which is all `s \ge 0` here.

## Root existence corollary
At `s = 0`,
\[
\Lambda(0) = \#\mathcal R.
\]
Because `nontrivial_induced_structure` excludes the size-1 collapse, `\#\mathcal R \ge 2`, hence `P_{ind}(0) > 0`.

As `s \to \infty`, each `|a(w)|^s \to 0`, so `\Lambda(s) \to 0` and `P_{ind}(s) \to -\infty`.

Therefore, by continuity and strict monotonicity, there exists a unique candidate root `s_*` such that
\[
P_{ind}(s_*) = 0.
\]

## Witness families
- `frontier.fw_delayed_return_gate_a3`
- `frontier.fw_delayed_return_gate_a1`
- `frontier.fw_delayed_return_gate_a2`

Support from diagnostics:
- all three witnesses have observed return lengths `2,3,4,5`
- all three show nontrivial induced structure rather than size-1 collapse
- all three satisfy the working-class tags in `delayed_return_theorem_assumptions_v1.json`

## Why any narrowing is necessary
- No narrowing is necessary for the pressure step itself.
- The class would need narrowing only if a future ticket shows that `induced_alphabet_control` does not hold uniformly or that some delayed-return witnesses produce unbounded return alphabets not covered by the current working-class definition.

## Outside the proved pressure class
- The old `contextual_local.domain_gated_two_map_local_ifs` is outside because its induced system collapses to a trivial one-symbol core.
- The stretch class is still outside this note because genuinely countable-state delayed-return behavior would require a different pressure theorem than the finite-return-alphabet argument used here.
- Lower-transfer / truncation control is still open; this ticket only closes induced pressure existence and the immediate root-supporting monotonicity/continuity step.

## Theorem blocks
### IP-LEM-1 — induced partition-sum finiteness
For the working class, induced partition sums are finite because the first-return alphabet is finite and each return-block weight is finite.

### IP-LEM-2 — bounded-bridge / almost-subadditivity lemma
In fact there is exact additivity: `Z_{n+m}^{ind}(s) = Z_n^{ind}(s) Z_m^{ind}(s)`.

### IP-LEM-3 — induced pressure existence theorem
The induced pressure exists as the true limit
\[
P_{ind}(s) = \log \Lambda(s).
\]

### IP-LEM-4 — monotonicity lemma
`P_{ind}(s)` is strictly decreasing in `s`.

### IP-COR-5 — continuity / root corollary
`P_{ind}(s)` is continuous and has a unique zero `s_*`.
