# Theorem Traceability Matrix v1

## What this matrix is for
This matrix is the package-integrity firewall for the audited-shell Level-3 core. It records, in one place, the exact assumption links, dependency links, evidence links, claim bindings, and scope guards for each closed theoremlet.

## Closed theoremlets covered
- `continuous_full_loop_lawfulness_theoremlet`
- `cocycle_pressure_closure_theoremlet`
- `strict_theory_extension_theoremlet`
- `conditional_pressure_disintegration_theoremlet`

All four are treated as `closed_in_note` on `continuous_full_loop_lawful_kernel_class_shell_stable`.

## Assumption-to-theoremlet traceability
The matrix indexes every assumption ID used by the four closed theoremlets and records:

- which theoremlets use it
- whether it is core-relevant or only support/restrictive
- whether it is shell-specific or generic inside the current closed class

This is the assumption-side scope guard.

## Dependency-to-theoremlet traceability
Each core theoremlet is linked to its governing dependency JSON, and the matrix records the theoremlet-to-dependency mapping explicitly. This prevents a manuscript draft from citing a closed theoremlet without its actual dependency object.

## Evidence-to-theoremlet traceability
Each core theoremlet is linked to concrete supporting artifacts and each artifact is marked as either:

- theorem-supporting
- or diagnostic-only

This prevents support-only diagnostics from being cited as if they were closed theoremlets.

## Claim-scope firewall
The matrix explicitly partitions:

- `core_closed_claims`
- `support_only_claims`
- `reserve_routes`
- `explicit_nonclaims`

Every core theoremlet lists the claim IDs it may support and the claim IDs it must never support.

## Audited-shell boundary
The matrix freezes the boundary at:

- audited shell only
- no broader-class theorem
- no shell-general theorem
- no direct stratumwise root-separation theorem
- no external/non-SFT breadth claim beyond what is actually closed

These guards are encoded both in the theoremlet entries and in the scope firewall.

## Failure modes the matrix prevents
- citing support-only diagnostics as closed theoremlets
- binding a figure or report to a non-claim
- widening the class scope beyond the audited shell
- reviving rejected stratumwise or broader-class routes as if they were core results
- detaching theoremlets from their dependency/evidence chain
