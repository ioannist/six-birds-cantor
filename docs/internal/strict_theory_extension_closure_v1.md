# Strict Theory Extension Closure v1

## Decision
`closed_on_audited_shell_class`

## Class on which strict extension is closed
`continuous_full_loop_lawful_kernel_class_shell_stable`

The closure is on the audited shell class used by the strict-extension report. No additional narrowing beyond the audited shell is required.

## Base theory T0
`T0` is the closed cocycle theory on the shell-stable six-primitive class. Its definable structure is the cocycle-level descriptor algebra actually carried by the closed route:

- family/config id
- shell-stable `tau`
- active cocycle-level lens
- closed cocycle pressure/growth descriptors

## Extended theory T1
`T1` adjoins to `T0` the packaging completion endomap `E_{tau,f}`, its fixed-point strata, saturation, material `P4<-P5` forcing, and the packaged-object comparison relation induced by those strata.

## Selected extension route
`forcing_lemma_nondefinability_route`

## Definability notion used
On the audited shell class, a packaged stratum is `T0`-definable iff it is constant on the audited `T0` descriptor classes. Equivalently, there exists a deterministic map from the `T0` descriptor tuple to the packaged stratum.

This is the definability notion closed here. It is theory-level on the audited shell, not a free-form prediction score.

## Non-definability lemma
For both witness families, the same audited `T0` descriptor class maps to multiple distinct `T1` packaged strata. Therefore no deterministic `T0`-definable map to packaged strata exists on the audited shell.

This closes `SE-LEM-2` and `SE-LEM-4` on the audited shell class:

- `generated.continuous_full_loop_kernel`: `6` audited descriptor classes split into multiple packaged strata
- `generated.continuous_full_loop_kernel_shell`: `4` audited descriptor classes split into multiple packaged strata

Hence the new strata are not definable from `T0` on the audited shell.

## Saturation and forcing closure
The completion endomap saturates on both witnesses. After saturation, material `P4<-P5` forcing occurs on both witnesses and generates new packaged strata with persistence:

- `generated.continuous_full_loop_kernel`: `18` material forcing events, persistent forced strata present
- `generated.continuous_full_loop_kernel_shell`: `18` material forcing events, persistent forced strata present

This closes `SE-LEM-3` on the audited shell.

## Macro-admissibility obstruction
`T0` has zero admissible macro-transitions on both witnesses:

- `generated.continuous_full_loop_kernel`: `0/18` admissible
- `generated.continuous_full_loop_kernel_shell`: `0/18` admissible

So `T0` is too coarse to support closed macro-dynamics on the same packaged objects. This closes `SE-COR-5`.

## Closure of ST-LEM-5
`ST-LEM-5` is closed in note on the audited shell class.

Reason: with definability fixed to audited `T0` descriptor classes, the mismatch matrix gives a direct non-definability witness. The same `T0` descriptor class carrying multiple `T1` strata rules out `T0`-definability by definition.

## Closure of ST-THM-7
`ST-THM-7` is closed in note on the audited shell class.

`T1` is a strict theory extension of `T0` on that class because:

1. `T0` is a closed cocycle theory on the shell-stable six-primitive class.
2. The completion rule saturates.
3. Material `P4<-P5` forcing generates new packaged strata.
4. Those strata are not definable from `T0`.
5. `T0` is too coarse to support closed macro-dynamics on those objects.

Therefore `T1` is not `T0` plus another observable. It is a strict extension of `T0` at the same class.

## Why any narrowing is necessary
No extra narrowing is necessary. The closure is already stated on the audited shell class, and both required witnesses satisfy the closure conditions there.

## Outside the closed class
Outside the closed claim are:

- shells not covered by the audited `T0` descriptor algebra
- families where forcing is not material or does not generate persistent strata
- families where macro-admissibility obstruction does not hold
- any attempt to read this closure as a class-broadening theorem rather than a strict-extension theorem
