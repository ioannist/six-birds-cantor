# P5 Causal Closure v1

## What was missing before
- We treated P5 as a packaging summary field instead of a causal producer.
- That let the rewrite bundle look strong without making packaging indispensable.
- A six-birds target must fail if P5 is removed.

## Active P5 semantics for Cantor substrates
- P5 is active only if it produces candidate packagings and the selected packaging changes the next substrate update.
- The selected packaging must drive both rewrite targeting and gating.
- P5 must therefore be a producer, selector, and downstream driver.

## Packaging producers
- P5<-P3 produces route/protocol-derived packagings.
- P5<-P4 produces lens/sector-derived packagings.
- P5<-P6 produces budget/audit-derived packagings.

## Packaging selector
- One packaging is selected by a hysteresis best-score rule.
- The selected packaging is retained unless a new candidate improves the score beyond threshold.

## P1 consumes P5
- P1 rewrite targets depend on active packaging boundaries and package defect score.
- Removing P5 must remove the selected packaging signal from rewrite targeting.

## P2 consumes P5
- P2 gating depends on package viability and cross-package leakage under the selected packaging.
- Removing P5 must qualitatively alter the admissible gating path.

## What counts as causal closure for P5
- P5 is causal only if changing or removing the active packaging changes the next-step lawful substrate.
- P5 is not causal if it only reports structure already determined elsewhere.
- The knockout audit must show a material loop change under P5 removal.

## Decision rule
- `p5_causally_closed` only if the selected full-loop candidate has at least two active packaging producers, feeds P5 into both P1 and P2, and the P5 knockout materially breaks the loop.
- Otherwise P5 remains observational or only partially causal.
