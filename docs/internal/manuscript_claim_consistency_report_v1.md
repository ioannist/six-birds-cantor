# Manuscript claim consistency report v1

## Audit scope
This audit checks the manuscript against the frozen claim ledger, theorem traceability matrix, contribution delta map, publication risk audit, Level-3 theorem package, and figure manifest.

## Closed theoremlets checked
- `continuous_full_loop_lawfulness_theoremlet`
- `cocycle_pressure_closure_theoremlet`
- `strict_theory_extension_theoremlet`
- `conditional_pressure_disintegration_theoremlet`

## Allowed claims checked
The manuscript was checked for consistency with the four closed theoremlets above, along with the support-only status of the closure-deficit proxy table and the reserve/non-claim boundaries encoded in the frozen package.

## Non-claims protected
- no broader-class theorem beyond the audited shell
- no shell-general theorem
- no external/non-SFT breadth claim beyond what is closed
- no direct stratumwise root-separation theorem
- no packaging-induced broader theorem class claim

## Caption/figure binding audit
The integrated manuscript figures and tables match the frozen figure manifest. The five core figures/tables support only the four closed theoremlets, and the closure-deficit proxy table remains explicitly support-only in the appendix. The reserve stratumwise diagnostic is not included in the manuscript.

## Patches applied
No semantic claim patches were required in this pass. The manuscript already matched the frozen theorem package at the claim and caption level. This audit added only the consistency script, machine report, and test coverage.

## Remaining manual checks
- Overfull box warnings remain in some previously inserted figures/tables and in one appendix line; these are typographic rather than semantic.

## Final consistency decision
`consistent`
