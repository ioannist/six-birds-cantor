> Historical proof proposal, superseded by the [2026-10-01 mathematical review](mathematics_review_2026_10_01.md). Closure labels below are workflow provenance, not mathematical certification. Consult the review and restoration notes for valid statements and outstanding hypotheses.

# Strict Theory Extension Scaffold v1

## Target strict-extension theorem
On the closed six-primitive shell-stable class, the hybrid theory `T1` is a strict theory extension of the cocycle theory `T0`: after saturation of the packaging completion rule, material `P4<-P5` forcing produces packaged strata that are not definable from the `T0` lens/observable structure, and the macro-admissibility obstruction shows that `T0` is too coarse for closed macro-dynamics at that depth.

## Base theory T0
`T0` is the closed cocycle theory on `continuous_full_loop_lawful_kernel_class_shell_stable`. Its theorem object is the closed selector-weighted cocycle pressure route together with the shell-stable cocycle-level lens/observable structure already used by the pressure closure.

## Extended theory T1
`T1` keeps the same underlying shell-stable six-primitive class, but adjoins:

- the packaging completion endomap `E_{tau,f}`
- its fixed-point strata
- saturation of the completion rule
- `P4<-P5` forcing/lens refinement
- packaging-based macro-admissibility as an extension-pressure witness

`T1` is not `T0` plus another scalar diagnostic. It changes the theory object by adjoining completion-generated strata and a forcing step that can change which packaged objects are expressible.

## Selected extension route
`forcing_lemma_nondefinability_route`

The main route is: saturation of the completion rule forces a refinement step, and the resulting packaged strata are then shown to be non-definable from `T0`. Fixed-point stratification and macro-admissibility obstruction are supporting ingredients.

## Theorem object versus simulation object
The theorem object is the pair `(T0, T1)` on the closed shell-stable six-primitive class, together with the extension relation between them. The simulation trajectories and audits are witnesses for the theorem scaffold; they are not the theorem object.

## Saturation and fixed-point strata
The completion object is well-defined on the same closed class as the cocycle theorem. The audited completion reports show:

- saturation on both frozen witnesses
- stable packaged-strata structure
- multiple fixed-point strata across `tau`, lens, and initial-condition panels

This is the emergence/stability side of the extension scaffold.

## P4<-P5 forcing step
The extension mechanism is the material feedback loop `P4<-P5`: packaging saturation/refinement changes the active lens and yields new packaged strata after forcing. This is the scaffolded anti-saturation move.

## Definability / non-definability criterion
A packaged stratum is definable from `T0` if it is a deterministic function of the cocycle-level theory structure already carried by `T0`: family/config id, shell-stable `tau`, active `T0` lens, and the closed cocycle pressure/growth descriptors.

The audited proxy says the same `T0` descriptor tuple can support multiple distinct packaged strata. The scaffold uses that as the working non-definability witness, but the formal theorem still needs a sharper non-definability argument than the current audit proxy.

## Macro-admissibility obstruction
Macro-admissibility fails throughout the audited `T0` shell. The scaffold reads this as evidence that `T0` is too coarse to support closed macro-dynamics at the completion depth, so the forcing step is not optional bookkeeping but part of the strict-extension mechanism.

## Core theorem blocks
1. `ST-LEM-1` base-theory closure lemma
2. `ST-LEM-2` completion endomap well-posedness lemma
3. `ST-LEM-3` saturation / fixed-point stratification lemma
4. `ST-LEM-4` `P4<-P5` forcing lemma
5. `ST-LEM-5` non-definability lemma
6. `ST-COR-6` macro-admissibility obstruction corollary
7. `ST-THM-7` strict theory extension theoremlet

## Witness configs
- `generated.continuous_full_loop_kernel`
- `generated.continuous_full_loop_kernel_shell`

## Where P1-P6 remain essential
- `P1`: rewrite changes the cocycle theory beneath `T0`
- `P2`: gating changes support and admissibility beneath `T0`
- `P3`: timescale selects the completion scale `tau`
- `P4`: lens is part of `T0` and is refined by forcing in `T1`
- `P5`: completion endomap and fixed-point strata are the extension object
- `P6`: budget pressure enters route viability and forcing context

The extension theorem is not a `P4/P5` side story detached from the full six-primitive class. It lives on the already-closed six-primitive background class and depends on that closure.

## What the next closure ticket must prove
The next closure ticket must sharpen the audited non-definability witness into a theorem-grade argument. The likely hard point is `ST-LEM-5`: proving that the new packaged strata are genuinely not definable from `T0`, rather than only non-reconstructible under the current audited descriptor proxy.
