# Lawful Substrate Diagnostics v1

## Question being tested
Do the two frozen generated substrates from SB-T1 support a real six-birds theorem branch, or are they only interesting generated families with no clean theorem target?

## Generated substrates frozen from SB-T1
- `generated.pg_protocol_lens` from `pg.protocol_lens`
- `generated.pg_rewrite_bundle` from `pg.rewrite_bundle`

## Lawfulness criteria
- stable rule family after finite updates
- low closure / idempotence defect
- nontrivial induced structure
- enough stationarity for a theorem class

## Primitive-interaction criteria
- the substrate should depend on more than static P2-style gating
- P1, P3, and P6 must matter somewhere in the active generation path
- the rule family should not collapse if the active bundle is simplified away

## Theorem-amenability criteria
- bounded return or bounded bridge should be plausible
- overlap / truncation should not obviously explode
- the substrate should support a concrete working theorem target, even if a richer stretch target remains open

## Working theorem target
- `primitive_generated_structural_class`
- anchored by `generated.pg_protocol_lens`
- this is the conservative theorem envelope: stable, lawful, and easy enough to freeze now

## Stretch target
- `primitive_generated_rewrite_protocol_class`
- anchored by `generated.pg_rewrite_bundle`
- this is the stronger primitive-generated branch: the first real P1/P3/P6 rewrite loop

## What still blocks the theorem
- the rewrite target is only finite-state-renewal-like at the current frozen depth
- the structural target is clean but does not yet prove a broader frontier claim
- a full theorem beyond these targets would need richer bundle space or new lower-transfer work

