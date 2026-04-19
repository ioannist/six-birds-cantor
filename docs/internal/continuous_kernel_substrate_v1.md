# Continuous Kernel Substrate v1

## Why the previous substrate failed
The earlier Cantor substrate was built from a finite map list. That made the loop structurally discrete and too easy to collapse into finite-state or finite-renewal-like behavior. It could select among families, but it did not evolve a continuous operator state with endogenous competition.

## Continuous-kernel Cantor analogue of the PICA substrate
The reset pilot treats the substrate as a continuously evolving kernel/operator state. The kernel is updated each step and is interpreted as the active Cantor substrate. P1 rewrites the operator, P2 gates support/viability, P3 adapts the timescale, P4 computes competing lenses, P5 computes competing packagings, and P6 controls budget/income/cost and action temperature.

## State variables
The state vector includes:
- kernel/operator state `K`
- active lens
- active packaging
- timescale `tau`
- budget/income ledger
- phase / protocol state
- action weights / mixture weights
- cached informants
- cache invalidation counters and refresh rules

## Active P1–P6 roles
- P1: kernel rewrite driven by the selected packaging and active lens
- P2: gating of rows/support based on packaging viability and lens/informant data
- P3: timescale and protocol update driven by variation and switching pressure
- P4: competing lens computations on the current kernel
- P5: competing packaging computations on the current kernel
- P6: budget / income / cost update and stochastic temperature control

## Cache invalidation / refresh logic
Cached informants are invalidated when the kernel signature changes. Lens or packaging switches also increment invalidation counters. The refresh logic re-computes stationary, row/column, diagonal, imbalance, and support informants from the current kernel.

## Lens competition
Three active lens algorithms compete each step:
- spectral-style lens
- row/column similarity or clustering lens
- audit / flow / quantile lens

## Packaging competition
Three active packaging algorithms compete each step:
- partition / cluster packaging
- return-core / recurrence packaging
- budget / audit-shaped packaging

The active packaging is selected with explicit hysteresis and stochastic tie-breaking among near-best candidates.

## Budget / cost / stochastic action logic
P6 produces income from packaging score, lens score, and stability, and subtracts switching and phase-dependent cost. The resulting budget modulates the action temperature used for stochastic or near-stochastic choice among competing primitives.

## Decision rule for the reset pilot
The pilot is successful only if the continuous substrate supports a real full loop:
- all six primitives are causally active in one substrate
- P5 is consumed by P1 and P2
- knockout of any primitive materially degrades the loop
- the trajectory is not trivially finite-state-like by construction

Pilot outcome: the run supports `continuous_full_loop_working` on the current kernel size and horizon.
