# Hybrid Pressure Root Consequence v1

## Question being decided
Which thermodynamic consequence route on the canonical hybrid object is actually paper-native and theorem-usable on the audited shell?

## Canonical hybrid object underneath
The underlying theorem object is the canonical hybrid object on `continuous_full_loop_lawful_kernel_class_shell_stable`:

- the closed `T0` cocycle pressure object
- the `T1` packaging-completion endomap `E_{tau,f}`
- saturation and `P4<-P5` forcing
- packaged-object fibers / persistent packaged strata

The consequence theorem must sit on that hybrid object, not on the raw trajectory and not on the cocycle-only quotient.

## Candidate consequence routes
`stratumwise_pressure_existence_route`

- define a separate pressure/root object on each persistent `T1` stratum
- status: `rejected`
- rejection reason: conceptually wrong for the papers; packaged strata are fibers of a global thermodynamic object, not thermodynamically autonomous systems

`root_separation_within_T0_route`

- prove distinct `T1` strata inside one `T0` class have distinct roots/profiles
- status: `rejected`
- rejection reason: the papers do not use independent stratum roots as the main consequence object, and the audited shell does not support stable direct separation

`conditional_pressure_disintegration_route`

- decompose the global `T0` pressure nontrivially over `T1` packaging fibers / packaged futures
- status: `working`

## Selected working consequence route
`conditional_pressure_disintegration_route`

This is the paper-native route. The global `T0` pressure is the starting thermodynamic object, and the packaged `T1` fibers conditionally disintegrate it through weighted fiber contributions.

## Selected stretch consequence route
None.

The earlier stretch framing is retired here. The route choice is no longer “working vs stretch”; it is a pivot away from the wrong object.

## Pressure/root object on packaged strata
Historical stratumwise pressure profiles remain useful as supporting diagnostics, but they are not the theorem object. The theorem object is now a conditional disintegration quantity built from:

- the global `T0` pressure proxy `P_T0(s)`
- the package-conditioned fiber weights `w_{d,Sigma}`
- the fiber-conditioned stratum profiles `P_Sigma(s)`
- the weighted package-conditioned gap

`Delta_{T0->T1}(d,s) = P_T0(s) - sum_Sigma w_{d,Sigma} P_Sigma(s)`

where `d` is an audited `T0` descriptor class.

## Compatibility with the closed T0 cocycle pressure
Compatibility is structural:

- `P_T0(s)` is exactly the closed cocycle pressure object from the pressure theoremlet
- the `T1` disintegration uses the same cocycle observable, but conditions it on packaging fibers / packaged futures
- so the consequence is a nontrivial decomposition of the same thermodynamic object, not a competing observable

## Candidate theorem statement
Working theorem target:

On the canonical hybrid object over the audited shell, the global `T0` cocycle pressure admits a nontrivial package-conditioned disintegration over `T1` packaging fibers. Equivalently, the audited gap

`Delta_{T0->T1}(d,s)`

is bounded away from zero on the audited descriptor fibers and `s`-grid, so `T0` is not sufficient for the `T1` packaged future in the audited thermodynamic sense.

## What the support diagnostics test
The support diagnostics test:

- whether the weighted package-conditioned pressure gap is nontrivial on both witnesses
- whether a closure-deficit / KL-style proxy is positive on the same descriptor fibers
- whether macro-admissibility failure aligns with that nontrivial gap
- whether the quantity is stable across the audited shell

Current support outcome:

- `conditional_pressure_disintegration_route`: supported
- `stratumwise_pressure_existence_route`: rejected
- `root_separation_within_T0_route`: rejected

Decision:

`consequence_route_plausible`

## What the next closure ticket must prove
The next closure ticket must prove the package-conditioned disintegration theoremlet itself:

- well-posedness of the package-fiber-conditioned quantity
- non-`tau`-closedness / macro-admissibility obstruction
- positivity / nontriviality of the disintegration quantity
- and the relation between nontrivial disintegration and `T0` insufficiency for the packaged future
