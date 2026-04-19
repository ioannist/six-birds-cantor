# Stratumwise Thermodynamic Distinction v1

## Question being decided
Can persistent `T1` packaged strata lying over the same `T0` object class be thermodynamically distinguished in a stable theorem-usable way on the canonical hybrid object?

## Canonical hybrid object underneath
The theorem object remains the canonical hybrid object on `continuous_full_loop_lawful_kernel_class_shell_stable`:

- the closed `T0` cocycle pressure object
- the `T1` packaged-object map from the completion endomap
- saturation and material `P4<-P5` forcing
- persistent packaged strata within `T0` fibers

The distinction question is asked inside a fixed `T0` descriptor class, not on the raw trajectory.

## Candidate distinction routes
`root_window_separation_route`

- distinct persistent `T1` strata inside one `T0` fiber have disjoint or stably separated root/sign windows

`profile_gap_route`

- distinct persistent `T1` strata inside one `T0` fiber have profile curves separated by a stable positive gap

`weighted_conditional_distinction_route`

- direct stratumwise separation fails, but a package-weighted conditional profile still differs from the base `T0` pressure in a stable way

## Selected working sharpening route
`weighted_conditional_distinction_route`

This is the only route supported across both required witnesses. The weighted package-conditioned profiles differ materially from `T0` pressure on both witnesses, while direct within-fiber root/profile separation remains absent.

## Selected reserve route
`profile_gap_route`

This remains the nearest direct stratumwise route, but the current audited shell only shows microscopic profile differences within a fixed `T0` class, not a stable theorem-usable gap.

## What counts as thermodynamic distinction
The comparison object is:

- a stratumwise pressure proxy `P_Sigma(s)`
- its sign/root window on the audited `s`-grid
- its normalized profile curve inside a fixed `T0` fiber
- and, when direct comparison fails, a weighted conditional profile obtained by package-conditioned averaging across persistent strata

Theorem-worthy distinction would mean either:

- disjoint root/sign windows inside one `T0` fiber
- a stable positive profile gap inside one `T0` fiber
- or, failing that, a stable weighted conditional profile that materially departs from the base `T0` pressure and therefore points to packaged conditional disintegration rather than plain stratumwise separation

## Within-T0-fiber comparison
On the audited shell:

- `generated.continuous_full_loop_kernel` has only `1` persistent packaged stratum, so direct within-fiber thermodynamic separation is unavailable there
- `generated.continuous_full_loop_kernel_shell` has multiple persistent strata within some `T0` descriptor classes, but the pairwise profile gaps are microscopic (`~10^-7`) and the sampled root windows/sign profiles coincide

So the direct stratumwise routes fail for different reasons on the two required witnesses:

- lack of multiple persistent strata on the core witness
- lack of stable thermodynamic profile separation on the shell witness

By contrast, the weighted conditional profiles differ materially from `T0` pressure on both witnesses across the audited `s`-grid.

## Candidate theorem statement
Rejected working theorem target:

Within each fixed `T0` descriptor class, distinct persistent `T1` strata carry stably separated root windows or profile curves.

Current supported theorem target:

On the canonical hybrid object, packaged conditional weighting induces a thermodynamic profile that is stable on the audited shell and materially different from the base `T0` pressure, even when direct stratum-to-stratum separation inside one `T0` fiber is not sharp enough.

This points toward the conditional disintegration route rather than closure of the current stratumwise distinction route.

## What the diagnostics test
The diagnostics test:

- persistent `T1` strata grouped by fixed `T0` classes
- stratumwise pressure curves on the audited `s`-grid
- root/sign windows for each persistent stratum
- pairwise profile-gap statistics inside one `T0` fiber
- stability of those gaps across the audited shell
- weighted conditional profiles when direct stratumwise separation fails

Observed outcome:

- `root_window_separation_route`: unsupported
- `profile_gap_route`: unsupported
- `weighted_conditional_distinction_route`: supported

Decision:

`stratumwise_route_not_viable`

## What the next closure ticket must prove
The next ticket should pivot to the packaged conditional theorem route and prove:

- theorem-grade package-conditioned thermodynamic profiles on the canonical hybrid object
- compatibility/disintegration with the closed `T0` cocycle pressure
- persistence of that conditional profile under forcing and saturation
- and a real conditional pressure theoremlet, rather than another attempt to force direct within-fiber root separation
