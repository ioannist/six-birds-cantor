# Continuous Full-Loop Theorem Scaffold v1

## Target theorem
There exists a nonempty compact forward-invariant lawful regime class for the continuous full-loop kernel cocycle such that the six-primitive loop remains nondegenerate, lens and packaging competition remain active under hysteresis, and budget/timescale dynamics stay active without fast collapse.

## Theorem object versus simulation object
The theorem object is the continuous operator-state cocycle and its forward-invariant regime class. The simulation trajectory is only evidence for the class; it is not the theorem object.

## Working theorem class
`continuous_full_loop_lawful_kernel_class`

## Stretch theorem class
`continuous_full_loop_lawful_kernel_class_with_wider_parameter_shell`

## Selected theorem route
`deterministic_skew_product_with_budget_feedback`

## State space and update law
The state space consists of a continuous kernel/operator state together with active lens, active packaging, phase/protocol state, tau, budget/income ledger, action weights, and cache/informant state. The update law is a deterministic skew product with hysteretic selection and budget feedback.

## Where P1–P6 enter
- P1: continuous rewrite of the kernel/operator
- P2: gating/support modification of the kernel
- P3: timescale/protocol adaptation
- P4: competing lens computations
- P5: competing packaging computations, consumed by P1 and P2 through the active packaging
- P6: budget/income/cost dynamics and action-temperature control

P5 is essential because the active packaging drives both rewrite targeting (`P1<-P5`) and gating targeting (`P2<-P5`).

## Core theorem blocks
1. CK-LEM-1 state-space well-posedness
2. CK-LEM-2 refresh/invalidation lemma
3. CK-LEM-3 hysteretic selector lemma
4. CK-LEM-4 primitive-closure lemma
5. CK-LEM-5 forward-invariant regime lemma
6. CK-LEM-6 nondegenerate exploratory dynamics lemma
7. CK-THM-7 continuous full-loop lawfulness theoremlet

## Why the six-primitive closure is essential
The theorem target is not the trajectory and not a reduced finite-memory control model. It is the causal six-primitive loop itself. Dropping any primitive changes the update law materially, so the class is only meaningful if P1–P6 all remain active.

## Outside the class
Outside the class are trajectories that freeze, collapse, or lose causal closure in any primitive knockout. The control families and shell witness remain outside the theorem claim unless they satisfy the same full-loop conditions.

## What the next closure ticket must prove
The next ticket must prove forward invariance of the lawful regime class and noncollapse under the budgeted hysteretic switching law, rather than merely showing that a long simulation run exists.

