# Conditional Pressure Disintegration v1

## Question being proved
On the canonical hybrid object over `continuous_full_loop_lawful_kernel_class_shell_stable`, does the global `T0` cocycle pressure decompose nontrivially over `T1` packaging fibers so that `T0` is not sufficient for the packaged future?

## Canonical hybrid object underneath
The theorem object is the canonical hybrid object:

- `T0` closed cocycle-pressure theory
- `T1` packaging-completion theory with fixed-point fibers
- saturation and material `P4<-P5` forcing
- packaged-object strata over audited `T0` descriptor classes

The theorem is about that hybrid object, not about a raw trajectory and not about independent stratum systems.

## Global T0 pressure object
For each audited parameter value `s`, let `P_T0(s)` be the closed cocycle pressure proxy already fixed by the pressure-closure theoremlet.

This is the global thermodynamic object. It is defined before conditioning on packaging fibers.

## T1 packaging fibers / packaged future object
Fix an audited `T0` descriptor class `d`. Let `F_d` be the finite family of `T1` packaging fibers / packaged futures that appear over that descriptor on the audited shell.

Each fiber `Sigma in F_d` carries:

- a weight `w_{d,Sigma}` from its audited frequency inside the descriptor fiber
- a packaged future signature `mu_{d,Sigma}`
- a conditioned pressure profile `P_Sigma(s)` induced by the same cocycle observable, now restricted to that packaging fiber

The fiber-average packaged future is

`bar(mu)_d = sum_Sigma w_{d,Sigma} mu_{d,Sigma}`.

## Conditional disintegration quantity
The working consequence object is the weighted package-conditioned pressure gap

`Delta_{T0->T1}(d,s) = P_T0(s) - sum_Sigma w_{d,Sigma} P_Sigma(s)`.

This is the explicit theorem object used here.

Supportive closure-deficit analogue:

`CD_proxy(d) = sum_Sigma w_{d,Sigma} KL(mu_{d,Sigma} || bar(mu)_d)`.

The theoremlet is closed on `Delta_{T0->T1}`. The KL-style object is supporting evidence for the same interpretation.

## Closure-deficit / sufficiency interpretation
In this audited-shell theoremlet, `T0` is sufficient for the packaged future iff

`Delta_{T0->T1}(d,s) = 0`

for every audited descriptor `d` and audited `s` in the working grid.

So a positive gap is the theorem-grade proxy for a nontrivial closure-deficit signal:

- if the package-conditioned average reproduces `P_T0`, then `T0` already captures the packaged future thermodynamically
- if the gap is positive, `T0` is thermodynamically insufficient for that packaged future

This is the sufficiency notion closed here.

## Macro-admissibility and non-τ-closedness
On both required witnesses, macro-admissibility fails on every audited completion panel:

- `generated.continuous_full_loop_kernel`: `0/18` admissible
- `generated.continuous_full_loop_kernel_shell`: `0/18` admissible

This is the audited-shell non-`tau`-closedness witness. The packaging fibers do not support closed macro-dynamics at the `T0` level, so a nontrivial conditional disintegration signal is expected rather than accidental.

## Candidate theorem statement
For every audited descriptor `d` and every audited `s` in the working grid on `continuous_full_loop_lawful_kernel_class_shell_stable`,

`Delta_{T0->T1}(d,s) > 0`.

Hence the global `T0` cocycle pressure decomposes nontrivially over `T1` packaging fibers, and `T0` is not sufficient for the packaged future on the audited shell.

## Closure of the consequence theoremlet
`conditional_disintegration_closed`

Closure ingredients:

1. The packaging-fiber / packaged-future object is well-defined on both witnesses.
2. The weighted package-conditioned pressure gap `Delta_{T0->T1}(d,s)` is well-defined because it uses the closed `T0` pressure object plus audited fiber weights and conditioned profiles.
3. The macro-admissibility obstruction gives non-`tau`-closedness on every audited panel.
4. The support report shows `Delta_{T0->T1}(d,s)` is bounded away from zero on both witnesses across the audited `s`-grid:
   - `generated.continuous_full_loop_kernel`: minimum audited gap `> 0.07`
   - `generated.continuous_full_loop_kernel_shell`: minimum audited gap `> 0.058`
5. The same report also provides a KL-style closure-deficit proxy as supporting evidence on nontrivial descriptor fibers, but the theoremlet is closed on `Delta_{T0->T1}` rather than on that auxiliary quantity.

Therefore the canonical hybrid object supports a nontrivial conditional pressure disintegration theoremlet on the audited shell.

## Outside the audited shell
Outside the closed claim are:

- shells not covered by the audited descriptor algebra
- any claim about the exact mutual-information closure deficit rather than the explicit pressure-gap theorem object closed here
- any claim that direct stratumwise root separation is needed
- families where macro-admissibility obstruction does not hold or the weighted package-conditioned gap is not bounded away from zero
