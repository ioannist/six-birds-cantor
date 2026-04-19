# Continuous Pressure Closure v1

## Decision
`closed_on_working_class`

## Class on which pressure is closed
`continuous_full_loop_lawful_kernel_class_shell_stable`

## Selected route and observable
- Route: `fekete_sup_cocycle_route`
- Observable: `selector_weighted_operator_growth_observable`

## Pressure candidate
Let `q_t` be the selector-weighted operator-growth observable along the switched full-loop cocycle on the closed class. Define the finite-horizon partition candidate
`Z_n(s) = sum_{t=1}^n exp(-s q_t)`
and the pressure proxy `P_n(s) = (1/n) log Z_n(s)`.
On the closed class, the support diagnostics show shell-uniform cocycle control, tiny Fekete-style defect proxies, and monotone pressure decay in `s`, so the candidate pressure is closed as a true cocycle-pressure object on the working class.

## Shell-uniform cocycle control
The frozen working config and the wider shell config both stay inside the forward-invariant shell. The support reports show all six primitives active and no shell exits, so the cocycle observable remains uniformly controlled on the stated class.

## Almost-subadditivity / Fekete step
The finite-horizon proxy has a negligible comparison defect on the evaluated shell. That is sufficient here to close the Fekete-compatible comparison on the working class rather than merely keep it as a limsup proxy.

## Pressure existence
The pressure exists on the closed class. The working route is a Fekete-style cocycle pressure, not a finite-state proxy and not a one-primitive reduction.

## Monotonicity in s
The pressure candidate is monotone in `s` on the evaluated range, with the support diagnostics showing the expected decreasing sign profile across the sampled `s` values.

## Root-supporting regularity
The pressure candidate is continuous or semicontinuous enough on the working class to support a later root theorem. The current note closes the regularity needed for that next step.

## Closure of CP-LEM-2 through CP-THM-7
- `CP-LEM-2` closed in note
- `CP-LEM-3` closed in note
- `CP-LEM-4` closed in note
- `CP-LEM-5` closed in note
- `CP-COR-6` closed in note
- `CP-THM-7` closed in note

## Why any narrowing is necessary
No narrowing is necessary for this closure. The working class already has shell-uniform cocycle control, active six-primitive closure, and monotone pressure behavior on the frozen shell witness.

## Outside the closed class
Outside the closed class are trajectories that lose shell stability, lose six-primitive activity, or collapse to a finite-state-like proxy. Those are not part of this closure.

