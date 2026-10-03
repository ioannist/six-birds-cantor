# Six Birds: Cantor

This repository contains the **Cantor instantiation** for the paper:

> **Strict Theory Extension on a Lawful Continuous Cantor Shell**
>
> DOI: [10.5281/zenodo.19189353](https://doi.org/10.5281/zenodo.19189353)
>
> Repository: https://github.com/ioannist/six-birds-cantor

This paper develops an audited-shell Cantor theorem package for a canonical hybrid object built from a cocycle-pressure base theory and a completion-based extension. The repository contains the frozen internal theorem-package artifacts, manuscript source, supporting diagnostics, publication ledgers, and the static web app scaffold used to package the audited outputs.

The active mathematical revision is documented in
[the revised theorem package](docs/internal/revised_main_theorem_package_2026_10_03.md).
It studies an explicitly constructed controlled continuous shell, its
multiplicative history pressure, and distinct completion objects invisible to
the specified growth observations. Structural extension does not imply a
positive pressure gap. The positive-gap reference law is a secondary
constructed example. The manuscript and frozen publication artifacts await
the later editing phase; their historical closure labels are not mathematical
certificates for the revised results.

## What this repository provides

- **Frozen theorem-package artifacts** under `docs/internal/` and `results/`, including the final claim ledger, traceability matrix, contribution delta map, publication-risk audit, and manuscript handoff bundle.
- **Core audited-shell theoremlets** for continuous full-loop lawfulness, cocycle pressure closure, strict theory extension, and conditional pressure disintegration.
- **Manuscript source** under `paper/`, including figures, tables, bibliography, compiled PDF output, and flattened TeX output at `paper/build/main_flat.tex`.
- **Static web app scaffold** under `apps/cantor-web/` for later data-driven visualization of frozen exported JSON.
- **Regression tests and builders** for theorem-package assembly, manuscript consistency, compile cleanup, and handoff generation.

## Scope and limitations

- The manuscript core is restricted to the audited shell; it does not claim a broader-class theorem beyond that shell-stable class.
- The paper does not claim a shell-general theorem, a non-SFT breadth theorem beyond what is closed, a direct stratumwise root-separation theorem, or a packaging-induced broader theorem class claim.
- Support-only diagnostics remain support-only; they do not enlarge the theorem package.
- The theorem-level contribution is theory depth on a fixed audited shell, not unrestricted family breadth.

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
