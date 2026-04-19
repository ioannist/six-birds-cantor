# Manuscript Theorem Summary v1

## Paper-core positioning
`level3_core_on_audited_shell`

The manuscript-facing core is the audited-shell Level-3 package only. The paper may use the four closed theoremlets as theorem-facing claims and may use designated support-only diagnostics only as support.

## Canonical theorem object
- Base object: `T0_cocycle_pressure_theory`
- Extended object: `T1_hybrid_cocycle_plus_completion_theory`
- Canonical object id: `canonical_hybrid_theorem_object_v1`
- Object statement: the paper-core object is the hybrid object itself, not the raw trajectory and not the cocycle-only quotient

## Closed class and scope
- Closed class: `continuous_full_loop_lawful_kernel_class_shell_stable`
- Scope: audited shell only
- Witness configs:
  - `generated.continuous_full_loop_kernel`
  - `generated.continuous_full_loop_kernel_shell`

## Main closed theoremlets
### `L3-T1` Continuous Full-Loop Lawfulness
- Object scope: `continuous_full_loop_theorem_package_v1`
- Class scope: `continuous_full_loop_lawful_kernel_class_shell_stable`
- Dependency path: `docs/internal/proof_dependency_continuous_full_loop_v1.json`
- Witness configs:
  - `generated.continuous_full_loop_kernel`
  - `generated.continuous_full_loop_kernel_shell`
- Manuscript-safe claim: the continuous six-primitive loop supports a shell-stable lawful regime with all six primitives causally active
- Manuscript-safe limitation: no broader shell theorem beyond the audited shell-stable class

### `L3-T2` Cocycle Pressure Closure
- Object scope: `T0_cocycle_pressure_theory`
- Class scope: `continuous_full_loop_lawful_kernel_class_shell_stable`
- Dependency path: `docs/internal/proof_dependency_continuous_pressure_v1.json`
- Witness configs:
  - `generated.continuous_full_loop_kernel`
  - `generated.continuous_full_loop_kernel_shell`
- Manuscript-safe claim: the switched-operator cocycle pressure object is closed on the audited shell
- Manuscript-safe limitation: no broader pressure theorem beyond the audited shell-stable class

### `L3-T3` Strict Theory Extension
- Object scope: `canonical_hybrid_theorem_object_v1`
- Class scope: `continuous_full_loop_lawful_kernel_class_shell_stable`
- Dependency path: `docs/internal/proof_dependency_strict_theory_extension_v1.json`
- Witness configs:
  - `generated.continuous_full_loop_kernel`
  - `generated.continuous_full_loop_kernel_shell`
- Manuscript-safe claim: `T1` is a strict theory extension of `T0` on the audited shell through saturation, `P4<-P5` forcing, non-definability, and macro-admissibility obstruction
- Manuscript-safe limitation: no claim of broader class coverage; the theoremlet is audited-shell only

### `L3-T4` Conditional Pressure Disintegration
- Object scope: `canonical_hybrid_theorem_object_v1`
- Class scope: `continuous_full_loop_lawful_kernel_class_shell_stable`
- Dependency path: `docs/internal/proof_dependency_conditional_disintegration_v1.json`
- Witness configs:
  - `generated.continuous_full_loop_kernel`
  - `generated.continuous_full_loop_kernel_shell`
- Manuscript-safe claim: the global `T0` pressure decomposes nontrivially over `T1` packaging fibers on the audited shell via the weighted package-conditioned pressure gap
- Manuscript-safe limitation: no direct stratumwise root-separation theorem and no exact KL/mutual-information closure-deficit theorem are claimed

## How the theoremlets fit together
1. `L3-T1` supplies the closed six-primitive lawful shell-stable regime.
2. `L3-T2` closes the cocycle pressure object on that regime.
3. `L3-T3` upgrades the cocycle object to the canonical hybrid object by strict theory extension.
4. `L3-T4` gives the thermodynamic consequence on that canonical hybrid object through conditional disintegration.

## Allowed claims
- The paper may state the four closed theoremlets as the core theorem package.
- The paper may state that the canonical hybrid object is the core Level-3 object on the audited shell.
- The paper may use the weighted package-conditioned pressure gap as the closed thermodynamic consequence object.
- The paper may cite closure-deficit proxies only as support, not as an independent closed theorem.

## Explicit non-claims
- no broader-class theorem beyond the audited shell
- no external/non-SFT breadth claim beyond what is actually closed
- no direct stratumwise root-separation theorem
- no packaging-induced broader theorem class claim
- no shell-general theorem beyond the audited shell-stable class

## Reserve/stretch material
- packaging-completion broader-class ambitions
- hybrid object broadening beyond audited shell
- wider parameter shell theorem
- non-SFT breadth story not already closed

## Suggested theorem ordering for the manuscript
1. Continuous full-loop lawfulness theoremlet
2. Cocycle pressure closure theoremlet
3. Canonical hybrid object and strict theory extension theoremlet
4. Conditional pressure disintegration theoremlet

## What evidence each theoremlet cites
- `L3-T1`: `docs/internal/continuous_full_loop_theorem_package_v1.md`, `docs/internal/proof_dependency_continuous_full_loop_v1.json`
- `L3-T2`: `docs/internal/continuous_pressure_closure_v1.md`, `docs/internal/proof_dependency_continuous_pressure_v1.json`, `results/continuous_pressure_closure/report.json`
- `L3-T3`: `docs/internal/strict_theory_extension_closure_v1.md`, `docs/internal/proof_dependency_strict_theory_extension_v1.json`, `results/strict_theory_extension_closure/report.json`
- `L3-T4`: `docs/internal/conditional_pressure_disintegration_v1.md`, `docs/internal/proof_dependency_conditional_disintegration_v1.json`, `results/conditional_disintegration/report.json`
