# Canonical Hybrid Theorem Object v1

## Why the object needed to be redefined
The old framing alternated between the cocycle object and the completion object. The canonical theorem object is the hybrid object itself: a closed cocycle theory together with a completion endomap, saturation/forcing structure, and packaged fixed-point strata on the same audited shell.

## Base object at T0
The `T0` object map is the cocycle-level object descriptor / quotient on the audited shell:

- family/config id
- audited `tau`
- active cocycle-level lens
- closed cocycle pressure descriptor
- closed cocycle growth descriptor

Two shell points are `T0`-equivalent when they have the same cocycle-level object descriptor.

## Extended object at T1
The `T1` object map assigns each shell point its packaged fixed-point stratum as determined by the completion endomap `E_{tau,f}`, together with the saturation/forcing regime that produces that stratum.

Two shell points are `T1`-equivalent when they land in the same packaged fixed-point stratum under the hybrid object.

## Canonical hybrid object
The canonical hybrid theorem object is the tuple

`(T0 object map, E_{tau,f}, saturation, P4<-P5 forcing, T1 packaged-object map)`

on `continuous_full_loop_lawful_kernel_class_shell_stable`.

This object keeps the thermodynamic cocycle structure and the packaging-completion structure in one theorem object instead of treating one as evidence for the other.

## Object map and equivalence notion
Let `pi_0` be the `T0` cocycle object map and `pi_1` be the `T1` packaged-object map.

- `pi_0` sends a shell point to its cocycle descriptor class.
- `pi_1` sends a shell point to its packaged fixed-point stratum.

The relevant equivalence notions are the fibers of `pi_0` and `pi_1`.

## Definability as factorization
`T1` is definable from `T0` on the audited shell iff there exists a deterministic map `g` such that

`pi_1 = g o pi_0`

on that shell.

Equivalently, each `T0` object class must map to a single `T1` packaged stratum.

## Intrinsic extension criterion
The hybrid object is an intrinsic strict extension on the audited shell iff no such factorization exists, while saturation, forcing, and macro-admissibility obstruction remain active.

That is the criterion used here. It is intrinsic because it is stated as a relation between the two object maps, not as a comparison of family coverage.

## Why this is more canonical than the previous framing
This framing is more canonical because:

- the theorem object is the hybrid object itself
- definability is stated intrinsically as factorization/non-factorization
- the extension claim is about object identity and theory depth
- the thermodynamic cocycle and the packaging completion structure live in one object

## Next consequence target
`hybrid_pressure_root_consequence`

The next theorem should sit on the canonical hybrid object and ask for a pressure/root consequence that respects both the cocycle and packaged-object structure.
