# Forward Invariant Lawful Regime v1

## Decision
`working_class_narrowed_and_closed`

## Class on which invariance is closed
`continuous_full_loop_lawful_kernel_class_shell_stable`

This is a shell-stable narrowing of `continuous_full_loop_lawful_kernel_class` chosen to keep selector margins, budget/tau ranges, and six-primitive activity jointly inside a compact forward-invariant window.

## Lawful regime shell
The shell is defined by the following formal bounds:
- persistent kernel variation stays nontrivial
- lens selector margin stays bounded away from zero
- packaging selector margin stays bounded away from zero
- budget remains in a lawful finite interval
- tau remains in a lawful finite interval
- all six primitives remain active

## Why the shell is nonempty
The pilot, regime sweep, and theorem-assumption audit all support the shell. The working pilot and the wider shell witness both lie inside the empirically observed lawful exploratory regime.

## Kernel-shell preservation
The continuous kernel update remains inside the shell because the observed loop maintains persistent variation and avoids freeze/collapse in the sweep window.

## Selector-margin preservation
The hysteretic lens and packaging selectors maintain nondegenerate margins in the pilot and shell witness, so the selected lens and packaging remain stable enough for forward-invariant control.

## Budget/tau-shell preservation
Budget and tau remain in a bounded dynamic range under the pilot and shell witness, with nonzero switching activity and no fast collapse.

## Six-primitive closure preservation inside the shell
The full six-primitive loop remains active inside the shell. P1 rewrites the kernel, P2 gates support, P3 adapts tau/protocol, P4 and P5 compete, and P6 modulates budget/income/cost. P5 remains causal because P1<-P5 and P2<-P5 drive the next update.

## Forward-invariant regime theoremlet
The shell is forward-invariant for the closed class and supports a lawful exploratory full-loop regime.

## Closure of CK-LEM-5
The forward-invariant regime lemma is closed on the shell-stable narrowed class.

## Closure of CK-THM-7
The continuous full-loop lawfulness theoremlet is closed on the shell-stable narrowed class.

## Why any narrowing is necessary
The broader working class is supported empirically, but the theorem proof needs a stricter shell to keep selector margins and budget/tau ranges uniform. The narrowing is therefore for proof stability, not to remove primitives.

## Outside the closed class
Outside the shell are trajectories that lose selector margins, fast-collapse, or exit the lawful budget/tau window. Such trajectories are not claimed by the theorem scaffold.

## What the next closure ticket must prove
The forward-invariance step is now closed on the shell-stable narrowed class. The next ticket should freeze the theorem package and, if desired, build the thermodynamic layer on top of the closed regime class.
