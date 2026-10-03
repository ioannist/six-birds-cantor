import Lake
open Lake DSL

package cantorAudit

require mathlib from git
  "https://github.com/leanprover-community/mathlib4" @ "v4.8.0"

@[default_target]
lean_lib CantorAudit where
  roots := #[`CantorAudit, `KernelCocycle, `KernelEscape, `CompletionWitness,
    `KernelLawfulness, `PressureExtension, `PressureRegularity, `RetainedMemory,
    `AffinityPressure, `MatrixPressure, `CompletionAffinityWitness,
    `CompletionDynamics, `CompletionForcing, `ConditionalPressure, `OriginalShell,
    `PrimitiveCompletion, `HistoryConditioning, `LoopExtension, `SparsePressure,
    `ControlledShell, `PackagedDisintegration]
