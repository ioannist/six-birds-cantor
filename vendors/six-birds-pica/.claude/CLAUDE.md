# Six Birds Emergence Ladder — Claude Instructions

## CRITICAL PROTOCOL RULE: No Engineered Substrates

**NEVER construct substrates with pre-determined structure outside the six primitives.**

The only allowed substrate constructors are:
- `MarkovKernel::random(n, seed)` — random dense chain
- `MarkovKernel::random_reversible(n, seed)` — random reversible chain
- `MarkovKernel::random_doubly_stochastic(n, seed)` — doubly stochastic chain

All structure MUST emerge from applying P1-P6:
- P1 (rewrite): perturb or replace the kernel
- P2 (gating): delete edges and renormalize
- P3 (holonomy): measure route mismatch / prescribe protocol ordering
- P4 (sectors): detect blocks/components
- P5 (packaging): find fixed points of the packaging endomap
- P6 (audit/drive): measure arrow-of-time, DPI, ACC; OR drive dynamics via EP/budget

## Current Phase: Re-engineering (Phase 2)

The static algebraic cascade (Phase 1) produced rank-1 macro kernels under exact
computation. We are replacing it with a dynamical system. Key changes:

1. **P6 as active drive** (not just diagnostic) — protocol-compliant
2. **Self-modifying dynamics** (primitives applied iteratively, kernel evolves)
3. **Fast-slow separation** (trajectory = fast, kernel modifications = slow)
4. **Mixture kernel** (stochastic choice among P1-P6 per step)
5. **Cross-layer coupling** (upper level P6 audit modulates lower level P2 gating)
6. **Active P3** (protocol phase as internal state variable)
7. **Adaptive tau** (set below mixing time, not fixed at 20)

See `lab/reengineering_notebook.md` for the full plan and agent insights.

## Project Structure

- `crates/six_primitives_core/` — Rust library: substrate, primitives, helpers
- `crates/graph/` — DAG framework: nodes, edges, branch, merge, audit
- `crates/runner/` — CLI experiment runner
- `lab/ledger/` — JSONL ledger (Phase 2: HYP-100+, EXP-073+)
- `lab/reengineering_notebook.md` — Master plan
- `research/` — Research papers for reference

## Experiment Protocol

1. Form hypothesis
2. Implement experiment using ONLY the six primitives on random substrates
3. Run sweep (10 seeds × 4 scales = 40 runs)
4. Record results to ledger
5. If hypothesis supported → record closure

## Ledger Format

All ledger files are append-only JSONL. Never modify existing entries — only append
updates with new status fields. Phase 2 numbering starts at HYP-100, EXP-073.
