# Memory — Six Birds Emergence Ladder

## HARD RULES

### No Engineered Substrates (learned 2026-02-16)
NEVER create substrate constructors like `build_coupled_blocks()` that pre-determine
structure. All structure must emerge from P1-P6 applied to `MarkovKernel::random()`.
This was a protocol violation that the user caught. See CLAUDE.md for the full rule.

## Project State
- Layer 0: 10 closures (CLO-000 through CLO-009), 13 experiments (EXP-000 through EXP-012)
- Layer 1: 3 closures (CLO-010 through CLO-012), 4 experiments (EXP-013 through EXP-016)
  - EXP-013: RM emerges from P2 gating (supported 30/40)
  - EXP-014: Cross-layer DPI for ergodic chains (supported 24/40)
  - EXP-015: P1 trajectory rewrite reduces RM 55-93% (supported 33/40)
  - EXP-016: Theory extension inconclusive (needs multi-block, p=0.5 keeps chains connected)
- Protocol enforcement hook at `.claude/hooks/check_protocol.sh`
- EXP-006 required a bug fix: protocol trap needs random-scan coupling (not product kernel)
  and doubly stochastic conditional kernels

## Key Patterns
- `MarkovKernel::random(n, seed)` is the starting point for all experiments
- P2 gating at various deletion probabilities creates structure from randomness
- Modular lens `Lens::modular(n, macro_n)` is the generic observer choice
- `p3_route_mismatch()` in primitives.rs already implements route mismatch correctly
