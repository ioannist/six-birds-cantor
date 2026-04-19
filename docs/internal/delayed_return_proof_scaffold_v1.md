# Delayed-Return Proof Scaffold v1

## Target theorem
For `K` in the working class `bounded_return_delayed_gate_subclass`, define an induced return-block pressure `P_ind(s)` on the delayed-return core. The target theoremlet is:

\[
\dim_H K = s_* \quad \text{where } P_{\mathrm{ind}}(s_*) = 0.
\]

Here `P_ind` is a pressure on the induced coding over first-return blocks, and the last step of the scaffold transfers induced dimension control back to the original attractor.

## Working class
Use the class profile `bounded_return_delayed_gate_subclass` from `docs/internal/delayed_return_theorem_assumptions_v1.json`, with these active assumptions:
- `delayed_return_core_exists`
- `bounded_return_times`
- `stationary_local_admissibility`
- `local_domain_compatibility`
- `induced_alphabet_control`
- `bounded_bridge_property`
- `feedback_free_admissibility`
- `core_return_coverage`
- `nontrivial_induced_structure`
- `usable_overlap_control` only where needed for geometric transfer

## Witness families
- `frontier.fw_delayed_return_gate_a3`
- `frontier.fw_delayed_return_gate_a1`
- reserve stress witness: `frontier.fw_delayed_return_gate_a2`

Diagnostics support only:
- each witness shows observed return lengths `2,3,4,5`
- each witness shows growing induced alphabet across the checked cap
- the old `contextual_local.domain_gated_two_map_local_ifs` remains the outside-control because it collapses to a trivial induced core

## Induced coding objects
Fix a delayed-return core interval `C`.

- A **return block** is a first-return word `w = i_1 ... i_r` such that the image of `C` under the corresponding local maps intersects `C`, while no proper prefix already returns.
- The **induced alphabet** `A_ind` is the set of all return blocks.
- The **induced cylinder** `[w_1 ... w_k]_ind` is the concatenation of `k` return blocks in the induced coding.
- The **induced cylinder weight** is
  \[
  \varphi_s(w) := |a(w)|^s,
  \]
  where `a(w)` is the contraction product along the return block.
- The map from induced cylinders back to the original system sends `[w_1 ... w_k]_ind` to the original cylinder/set obtained by concatenating the underlying branch words and applying them to `C`.

## Pressure object
For induced depth `k`, define
\[
Z_k^{ind}(s) = \sum_{w_1...w_k \in A_{ind}^k} \prod_{j=1}^k \varphi_s(w_j).
\]
The intended induced pressure is
\[
P_{ind}(s) = \limsup_{k\to\infty} \frac{1}{k} \log Z_k^{ind}(s).
\]
On the working class, bounded return and bounded-bridge compatibility are supposed to make this a well-defined pressure object rather than just a formal limsup.

## Upper-bound route
1. Use the induced coding lemma to cover the delayed-return part of the attractor by induced cylinders.
2. Use bounded return to compare original depth and induced depth up to uniform constants.
3. If `P_ind(s) < 0`, induced partition sums decay exponentially in induced depth.
4. Transfer this decay to an original covering sequence of `K` via the induced-to-original cylinder map.
5. Conclude `dim_H K <= s`.

## Lower-bound / measure route
Selected lower route: `induced_cylinder_premeasure`.

1. Define a premeasure on induced cylinders by normalized induced weights at a subcritical/critical parameter.
2. Use bounded-bridge compatibility to make the premeasure quasi-consistent across induced concatenations.
3. Push the premeasure through the induced-to-original cylinder map.
4. Use bounded return and local-domain compatibility to compare pushed-forward cylinder mass with original geometric scale.
5. Apply a Carathéodory/Frostman-style lower-bound argument to conclude `dim_H K >= s` for the relevant root parameter.

## Return-to-original-system transfer
The transfer step uses two ingredients.

1. **Depth comparison**: because return times are bounded, `k` induced steps correspond to original depths between `k r_min` and `k r_max`.
2. **Geometry comparison**: the image of an induced cylinder is an original cylinder/set with contraction comparable to the product of return-block contractions.

This is where the scaffold converts a theorem on the induced system into a theorem for the original attractor. The transfer is the same place where the proof would fail if return times were unbounded or if the induced coding lost geometric control.

## Where bounded return is used
- In the depth-comparison lemma between induced length and original depth.
- In the pressure transfer from induced partition sums to original covers.
- In the lower-side mass transfer, preventing arbitrarily long waiting tails from destroying scale comparisons.
- In keeping the working class narrower than the stretch class.

## Where the proof could still fail outside the working class
- If `bounded_return_times` fails, induced depth no longer compares uniformly with original depth.
- If `induced_alphabet_control` fails, induced pressure existence may require a countable-state or renewal formalism not yet developed here.
- If `core_return_coverage` fails, the induced core may be too lossy to recover the whole attractor.
- If `local_domain_compatibility` fails, the induced cylinder map back to the original system stops being well-defined enough for geometry transfer.
- If `usable_overlap_control` fails badly, the lower-side premeasure route may not give a clean Frostman transfer.

## Core theorem blocks
### DR-LEM-1 — Induced coding lemma
The working class admits a well-defined first-return coding over return blocks on the delayed-return core.

### DR-LEM-2 — Bounded-return comparison lemma
Bounded return times give uniform comparison between induced depth and original depth.

### DR-LEM-3 — Induced pressure existence lemma
The induced partition sums define a well-behaved pressure object `P_ind(s)` for the working class.

### DR-LEM-4 — Induced Bowen root lemma
There is a candidate root `s_*` determined by `P_ind(s_*) = 0`.

### DR-LEM-5 — Transfer upper-bound lemma
Induced upper-pressure decay transfers to an upper dimension bound for the original attractor.

### DR-LEM-6 — Transfer lower-bound / measure lemma
An induced cylinder premeasure transfers to a lower bound on the original attractor.

### DR-THM-7 — Final delayed-return Bowen theoremlet
Combining the upper and lower transfer steps gives
\[
\dim_H K = s_*.
\]

## Localized next hard point
The likely next hard point is `DR-LEM-3`, the induced pressure existence step. The working-class diagnostics show bounded-return structure and clean bridge proxies on the checked cap, but the scaffold still needs an honest argument that the induced pressure is well-defined uniformly for the class rather than only for the frozen witnesses.
