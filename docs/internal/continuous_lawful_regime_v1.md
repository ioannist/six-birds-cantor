> Historical proof proposal, superseded by the [2026-10-01 mathematical review](mathematics_review_2026_10_01.md). Closure labels below are workflow provenance, not mathematical certification. Consult the review and restoration notes for valid statements and outstanding hypotheses.

# Continuous Lawful Regime v1

## Question being tested
Whether the continuous PICA-style Cantor substrate has a stable lawful regime class that is robust under small parameter variation and supported by primitive knockouts, or whether the pilot is still too brittle to support theorem assumptions.

## Sweep performed
We ran a 12-trajectory neighborhood sweep around the continuous kernel pilot:
- 3 seeds
- 2 kernel sizes
- 2 small parameter settings for hysteresis, budget scaling, and initial tau

The sweep used the continuous-kernel pilot as the engine and the existing knockout audit as the necessity reference.

## Stable regime features
The runs consistently showed:
- persistent nontrivial kernel variation
- three-way lens competition
- three-way packaging competition
- active tau adaptation
- budget replenishment and cost pressure
- no finite-state-like collapse in the sweep window

All 12 runs were labeled `lawful_exploratory`.

## Primitive necessity findings
The knockout audit supports causal necessity for all six primitives:
- P1: yes
- P2: yes
- P3: yes
- P4: yes
- P5: yes
- P6: yes

The most direct necessity signals were:
- P4 knockout collapses lens switching
- P5 knockout collapses packaging switching and weakens the loop materially
- P6 knockout collapses budget dynamics

## Candidate theorem assumptions
The following assumptions are supported as theorem candidates:
- persistent kernel variation above a nontrivial threshold
- nondegenerate lens competition
- nondegenerate packaging competition
- active tau adaptation
- nontrivial budget replenishment / cost balance
- primitive-knockout fragility
- hysteresis persistence
- no fast collapse

These are regime evidence, not yet theorem statements.

## Working regime class
`lawful_exploratory_full_loop_class`

## Stretch regime class
`lawful_exploratory_full_loop_class_with_wider_parameter_shell`

## Decision
`lawful_regime_extracted`

## What the theorem branch should target next
The next theorem branch should target a lawfulness statement for the continuous full-loop exploratory regime, using the observed nondegeneracy conditions as assumptions and keeping the six-primitive causal loop explicit.

