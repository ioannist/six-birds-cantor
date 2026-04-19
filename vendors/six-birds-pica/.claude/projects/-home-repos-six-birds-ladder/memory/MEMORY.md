# Six Birds Ladder — Project Memory

## Project Overview
Emergent coarse-graining ladder built from 6 primitives (P1-P6) on random Markov kernels.
ALL structure must emerge from P1-P6 on `MarkovKernel::random()`. NO engineered substrates.

## Current State
- **Layers**: 0-7 complete (8 layers)
- **Closures**: CLO-000 to CLO-038 (39 total)
- **Experiments**: EXP-000 to EXP-040 (41 total)
- **Standing directive**: "keep going until really stuck"

## Critical Closures
- **CLO-027**: tau=20 rescues DPI to 87.5% — ALWAYS use tau=20
- **CLO-028**: Symmetrized P1 guarantees DPI at cost of 2x RM, 24% gap loss
- **CLO-033**: DPI-dynamics tension at scale (L6) — REVISED by CLO-038
- **CLO-034**: Tension is ratio-dependent: 52.5% find DPI+gap at some ratio
- **CLO-035**: Gap-constrained P3 search finds Pareto lenses (42.5%)
- **CLO-037**: tau=20 is free — gap often triples, no hidden cost
- **CLO-038**: CLO-033 REVISED: incompatibility is conditional, not fundamental

## Practical Recipe (7 layers of evidence)
1. Always tau=20 (CLO-027, CLO-037)
2. Try multiple ratios: n/2, n/3, 2n/3, 3n/4 (CLO-034)
3. Gap-constrained P3 search when DPI holds (CLO-035)
4. Symmetrization fallback if DPI still fails (CLO-028)

## Lens Notebook
Always consult `lab/ledger/lens_hypotheses.md` before designing lens experiments.
All 4 emergent candidates tested and closed in Layer 6.
Layer 7 showed ratio and search constraints matter more than lens type.

## Key Technical Parameters
- Scale-dependent gating: n≤16→0.90, n≤32→0.95, n≤64→0.97, n≤128→0.98, n>128→0.99
- Trajectories: n*200 (min 10000), RM samples: n/4 (min 30)
- Always tau=20 for DPI-critical measurements
- scale=4 and scale=8 are identical (both give n=8)

## File Structure
- `crates/six_primitives_core/src/` — Core (experiments_iter{1-9}.rs)
- `crates/runner/src/main.rs` — Runner (EXP-000 to EXP-040)
- `lab/ledger/` — hypotheses.jsonl, closures.jsonl, lens_hypotheses.md
- `lab/layers/layer_NNN/notes.md` — Per-layer analysis

## Process
1. Hypothesize → 2. Implement (experiments_iter*.rs) → 3. Sweep (40 runs) → 4. Analyze → 5. Close → 6. Notes
- Build: `cargo build --release` / `cargo run --release -p runner -- --exp EXP-NNN --sweep --scales 32,64,128,256`

## User Preferences
- Reject anything that sounds like engineering (e.g., spectral lens)
- 6Ps can be applied to anything emergent, not engineered
- Constants for tuning are OK as test hypotheses
