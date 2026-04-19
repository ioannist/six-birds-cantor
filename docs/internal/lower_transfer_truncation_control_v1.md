# Lower Transfer / Truncation Control v1

## Decision
- `working_class_narrowed_and_closed`

## Class on which lower transfer is closed
- Closed class: `bounded_return_full_core_delayed_gate_subclass`

This is the subclass of `bounded_return_delayed_gate_subclass` where, in addition to the FW-T3/FW-T5 assumptions, every surviving original branch/cylinder is represented by the delayed-return core up to uniformly bounded entry/exit correction. This narrowing is needed to turn the induced cylinder premeasure into an honest lower bound on the original attractor without uncontrolled truncation loss.

## Selected lower route
- `induced_cylinder_premeasure`

The route is not changed. The narrowing is used to make the premeasure transfer exact up to bounded multiplicative constants.

## Induced cylinder premeasure
Let `s_*` be the unique induced root from `induced_pressure_existence_v1.md`, so that
\[
\Lambda(s_*) = \sum_{w \in \mathcal R} |a(w)|^{s_*} = 1.
\]
For an induced cylinder `[w_1\cdots w_k]_{ind}`, define
\[
\mu_{ind}([w_1\cdots w_k]_{ind}) = \prod_{j=1}^k |a(w_j)|^{s_*}.
\]
Because the one-step induced weights sum to `1`, this is a consistent cylinder premeasure on the induced coding. No renormalization drift appears.

## Truncation-control mechanism
The main new narrowing is:
- `full_core_induction`
- `uniform_entry_exit_bound`

These imply:
1. every surviving original cylinder/set is represented by a bounded-prefix correction, then an induced cylinder, then a bounded-suffix correction;
2. the correction lengths are uniformly bounded by constants `L_in`, `L_out` independent of depth;
3. because of `strict_return_contraction`, these bounded corrections contribute only bounded multiplicative factors to diameters and cylinder masses.

Therefore, passing from the induced system back to the original one loses at most a fixed constant factor. In particular, the “truncation” from discarding non-return words is not exponential on this narrowed class.

## Return-to-original lower transfer
Given an induced cylinder `[w_1\cdots w_k]_{ind}`, let `X(w_1\cdots w_k)` be its image in the original attractor. By the narrowing assumptions,
\[
C_1 \mu_{ind}([w_1\cdots w_k]_{ind}) \le \operatorname{diam}(X(w_1\cdots w_k))^{s_*} \le C_2 \mu_{ind}([w_1\cdots w_k]_{ind})
\]
for constants `C_1,C_2 > 0` independent of `k`.

So the induced cylinder premeasure transfers to a lower mass estimate on original cylinder pieces with only bounded distortion from the entry/exit corrections.

## Cylinder-to-ball / content comparison
Using `usable_overlap_control`, every ball of radius comparable to an induced-cylinder image meets only boundedly many transferred pieces at the corresponding scale. Hence the transferred mass satisfies a Frostman-style estimate
\[
\mu(B(x,r)) \le C r^{s_*}
\]
for the pushforward measure `\mu` on the original attractor.

Equivalently, one gets a positive lower bound on `s_*`-Hausdorff content along the transferred covering scale. This closes the lower side.

## Final closure of DR-LEM-6
### LT-LEM-1 — induced cylinder premeasure construction
At the induced root, the product rule on return-block weights defines a consistent cylinder premeasure.

### LT-LEM-2 — truncation-control lemma
On `bounded_return_full_core_delayed_gate_subclass`, truncation loss is uniformly controlled by bounded entry/exit correction, so no exponential loss appears when transferring from induced cylinders to original cylinders.

### LT-LEM-3 — return-to-original mass transfer lemma
The induced premeasure pushes forward to original cylinder pieces with bounded multiplicative loss.

### LT-LEM-4 — lower content / ball comparison lemma
Using usable overlap control, the pushed-forward mass gives a Frostman-style ball estimate on the original attractor.

### LT-THM-5 — lower-transfer theoremlet
Therefore
\[
\dim_H K \ge s_*
\]
on the closed class.

## Final closure of DR-THM-7
### LT-COR-6 — final delayed-return Bowen closure
The induced pressure/root step already gives the upper side on the delayed-return branch. Combining that with `LT-THM-5` yields
\[
\dim_H K = s_*
\]
for `K` in `bounded_return_full_core_delayed_gate_subclass`.

So `DR-LEM-6` and `DR-THM-7` are both closed on the narrowed class.

## Why any narrowing is necessary
The broader working class only said the delayed-return core captured a nontrivial portion of the dynamics. That is enough for induced pressure, but not enough for lower transfer of the full attractor. To close the theorem, the induced tower must control every surviving branch up to bounded correction. Otherwise the truncation step could lose an uncontrolled part of the attractor.

## Outside the closed class
- `bounded_return_delayed_gate_subclass` remains the broader working class for diagnostics, but theorem closure is only proved here on the narrowed full-core subclass.
- The stretch class `countable_state_delayed_return_local_domain_class` is still outside this note.
- Families without `full_core_induction` or `uniform_entry_exit_bound` remain outside the closed theorem, even if their induced pressure exists.

## Witness families
- `frontier.fw_delayed_return_gate_a3`
- `frontier.fw_delayed_return_gate_a1`
- reserve stress witness still compatible: `frontier.fw_delayed_return_gate_a2`
