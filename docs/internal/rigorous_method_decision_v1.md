# Rigorous Method Decision v1

## Decision
`partition_sums_plus_certified_bracketing` is the default project-wide method.

## Evidence used
- Transfer comparison regenerated from `scripts/run_transfer_operator_comparison.py`.
  - `classical.middle_thirds`: transfer abs error `7.85e-14`, partition abs error `8.79e-12`, runtime transfer `0.18 ms`, partition `29.18 ms`.
  - `finite_state.adjacency_no_consecutive_2_base3`: transfer abs error `7.31e-14`, partition abs error `1.44e-2`, runtime transfer `2.34 ms`, partition `2.95 ms`.
- Certified bracketing regenerated from `scripts/run_certified_bracketing.py`.
  - `classical.middle_thirds`: certified width `8.88e-16`, contains reference root = true.
  - `finite_state.adjacency_no_consecutive_2_base3`: certified width `3.55e-15`, contains reference root = true.
- Local-pressure regenerated on contextual family.
  - `contextual_local.feedback_lens_protocol_coupled`: final upper/lower `0.078866...`, last-step drift `2.63e-2`.

## Why this method wins now
- Coverage priority: local-pressure/partition path already runs classical + finite-state + contextual/feedback families.
- Rigor priority: T08 certified brackets are already integrated and successful on key baselines.
- Runtime/convenience: transfer is faster/very accurate on baselines, but it is still baseline-only in current code.
- Therefore transfer does not meet project-wide coverage needs for upcoming contextual/local work.

## What the other method is still good for
- Keep transfer operator as a secondary validator on baseline/control families.
- Use it to detect drift/regressions in partition estimates (especially finite-state controls).
- Keep it as a candidate for targeted extension after contextual/local priorities are stabilized.

## Risks / revisit triggers
- If partition estimates remain unstable on contextual/feedback families at target depths, revisit method split.
- If transfer-operator coverage is extended to contextual/local families with comparable rigor, reopen default decision.
- Revisit when T13+ claim ledger shows repeated disagreement between transfer controls and partition+certified outputs.
