# Six Birds: Cantor

This repository contains the **Cantor instantiation** for the paper:

> **Strict Theory Extension on a Lawful Continuous Cantor Shell**
>
> DOI: [10.5281/zenodo.19189353](https://doi.org/10.5281/zenodo.19189353)
>
> Repository: https://github.com/ioannist/six-birds-cantor

The manuscript (version v3, 3 October 2026; v1 31 March 2026, v2 19 April 2026) studies a twenty-state self-rewriting stochastic substrate driven by six coupled mechanisms. It proves four results:

1. **Controlled shell.** An explicitly constructed, forward-invariant controlled Cantor shell exists for the unmodified update law.
2. **Growth pressure.** The multiplicative growth pressure on this shell exists, is Lipschitz and strictly decreasing, and has a unique zero in (1/3, 1).
3. **Strict extension.** Two shell states have identical growth descriptions but different completion objects.
4. **Growth blindness.** For those two states, all weighted history matrices coincide from the second step onward.

Strict extension therefore does not force a conditional pressure gap. On the same shell, one reference law gives a zero gap and another gives a certified positive gap; the positive case is a secondary constructed example.

The mathematics follows [the revised theorem package](docs/internal/revised_main_theorem_package_2026_10_03.md). Historical closure labels in older internal ledgers (the v1/v2 "theoremlets") are not mathematical certificates for these results. Appendix B of the paper records the version history.

## What this repository provides

- **Manuscript source** under `paper/`, including figures, tables, bibliography, compiled PDF output, and flattened TeX output at `paper/build/main_flat.tex`.
- **Lean 4 development** under `lean/`, covering the twenty-state witness, the matrix-pressure and disintegration arguments, and the shell induction. See `lean/README.md`.
- **Exact rational and interval certificates** under `results/` (controlled shell, all-word pressure, common-input zero gap), together with their generators under `src/` and `scripts/`.
- **Internal notes** under `docs/internal/`, including the revised theorem package and the historical v1/v2 artifacts.
- **Static web app scaffold** under `apps/cantor-web/`.

## Scope and limitations

- The shell is a class of legally controlled orbits. The paper does not claim positive probability under the original independent innovation law, nor that seeded floating-point runs reach the shell.
- All statements concern the exact-real reading of the update formulas.
- Strictness is relative to the stated growth description. The full labelled kernel determines the completion object.
- The pressure is the growth pressure of a declared observable; no dimension identity is claimed.

## Install

```bash
python -m pip install -e .[dev]
```

Install the web app dependencies if you want to build the static frontend:

```bash
make web-install
```

## Test

```bash
make test
```

## Build paper

```bash
make paper-build
```

Outputs:

- `paper/build/main.pdf`
- `paper/build/main_flat.tex`

## Build web app

```bash
make web-build
make web-test
```

## Repository notes

- Active bibliography: `paper/bib/references.bib`
- Zenodo related-works CSV: `assets/zenodo_related_works.csv`
- Final manuscript handoff: `docs/internal/final_manuscript_handoff_v1.json`
- Final manuscript PDF: `paper/build/main.pdf`
