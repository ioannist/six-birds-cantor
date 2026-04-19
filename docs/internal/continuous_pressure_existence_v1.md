# Continuous Pressure Existence Scaffold v1

## Target pressure object
The target is a pressure object for the switched full-loop operator cocycle on the closed class `continuous_full_loop_lawful_kernel_class_shell_stable`.

## Closed six-primitive class underneath
The pressure object sits on the six-birds-native closed full-loop class. It is not a pressure on the raw simulation trace and it is not a reduced finite-state proxy.

## Selected pressure route
`fekete_sup_cocycle_route`

## Selected observable family
`selector_weighted_operator_growth_observable`

## Thermodynamic object versus simulation object
The thermodynamic object is a cocycle-pressure candidate built from the closed regime class. The simulation trajectory is only evidence for the class and for the finite-horizon proxy behavior of the observable.

## Cocycle / sequence definition
Let `x_t` denote the cocycle state at time `t` on the closed class. Let `q_t` be the selected selector-weighted operator growth observable. Define the finite-horizon partition candidate
`a_n(s) = sum_{t=1}^n exp(-s q_t)`
or the equivalent branch-summed version over admissible cocycle histories on the closed class. The intended pressure is the Fekete-style limit of `P_n(s) = (1/n) log a_n(s)` once the comparison lemmas are in place.

## Pressure candidate
The pressure candidate is a switched-operator cocycle pressure on the closed full-loop class, with `s` weighting the operator-growth observable. The candidate is intended to be a true limit on the class, not merely a limsup on the sample trajectory.

## Why P1–P6 still matter here
- P1 changes the operator cocycle itself.
- P2 changes the support and gating structure seen by the cocycle.
- P3 changes the timescale and protocol state of the base dynamics.
- P4 changes the active lens and therefore the selector component of the observable.
- P5 changes the active packaging and therefore the observable and the P1/P2 targeting.
- P6 changes the budget weighting and action intensity that modulate the cocycle.

P5 remains causal because the active packaging drives both rewrite targeting (`P1<-P5`) and gating targeting (`P2<-P5`).

## Core theorem blocks
1. CP-LEM-1 cocycle observable well-posedness
2. CP-LEM-2 uniform finite-horizon control
3. CP-LEM-3 almost-subadditive or subadditive comparison
4. CP-LEM-4 pressure existence theorem
5. CP-LEM-5 monotonicity in `s`
6. CP-COR-6 root-supporting regularity
7. CP-THM-7 switched-operator cocycle pressure theoremlet

## Witness configs
- `generated.continuous_full_loop_kernel`
- `generated.continuous_full_loop_kernel_shell`

## What the next closure ticket must prove
The next ticket must turn the finite-horizon cocycle proxies into a pressure theorem on the closed class, then extract enough root-supporting regularity to support the later thermodynamic theorem.

