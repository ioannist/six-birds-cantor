# arXiv Submission Dry-Run Checklist --- Six Birds: Cantor

Paper: **Strict Theory Extension on a Lawful Continuous Cantor Shell**
Version: v3 (substantive mathematical revision; title page lists v1 31 March 2026, v2 19 April 2026, v3 3 October 2026; first-page footer carries the Zenodo v3 DOI 10.5281/zenodo.23126110).

## Section A --- Build + integrity

- [x] `latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex` succeeds (exit 0).
- [x] Undefined citations count = 0.
- [x] Undefined references count = 0.
- [x] Output: `paper/build/main.pdf` (28 pages, 496 KB).

Commands run:
```bash
cd paper && latexmk -pdf -g -interaction=nonstopmode -halt-on-error main.tex
grep -c "Citation.*undefined" build/main.log || true
grep -c "Reference.*undefined" build/main.log || true
grep -c "There were undefined references" build/main.log || true
```

Observed outcomes:
- build_exit_code: 0
- undefined_citations_count: 0
- undefined_references_count: 0
- undefined_references_banner_count: 0

## Section B --- Submission micro-assets

- [x] Highlights file exists: `paper/submission/highlights.txt` (5 lines, each <= 85 chars).
- [x] Keywords file exists: `paper/submission/keywords.txt` (8 keywords, hyphenated only).
- [x] AI disclosure file exists: `paper/submission/ai_disclosure.txt`.

Highlights line-length table:

| # | Length | Text |
|---:|---:|---|
| 1 | 84 | Explicit forward-invariant controlled Cantor shell for a self-rewriting 20-state law |
| 2 | 81 | Multiplicative growth pressure exists, decreases strictly, unique zero in (1/3,1) |
| 3 | 79 | Two shell states share every growth observation yet differ in completion object |
| 4 | 81 | Growth blindness: history matrices coincide from step two, so pressure cannot see |
| 5 | 84 | The pressure gap is set by the reference law: zero under one, positive under another |

## Section C --- Figures and sources

- [x] All figures are TikZ/pgfplots `.tex` fragments under `paper/figures/` (no bitmap assets).
- [x] All tables are LaTeX `.tex` fragments under `paper/tables/`.
- [x] No EPS files; no `\includegraphics` bitmap dependencies.
- [x] All `\input` targets in `main.tex` resolve inside the bundle (sections/figures/tables + macros).
- [x] Bibliography embedded via `main.bbl`; `bib/references.bib` also included for verification.

Figure inventory:

| File | Type | Referenced in |
|---|---|---|
| figures/fig_split_merge.tex | TikZ | sections/01_introduction.tex |
| figures/fig_update_loop.tex | TikZ | sections/02_substrate.tex |
| figures/fig_pressure.tex | pgfplots | sections/04_growth_pressure.tex |
| figures/fig_gap.tex | pgfplots | sections/07_pressure_disintegration.tex |

Table inventory:

| File | Referenced in |
|---|---|
| tables/tbl_shell_certificates.tex | sections/03_controlled_shell.tex |
| tables/tbl_nonredundancy.tex | sections/03_controlled_shell.tex |
| tables/tbl_verification.tex | sections/08_verification.tex |
| (inline) witness kernel and object tables | sections/appendix_a_witness_data.tex |

## Section D --- Bundle verification

- [x] Bundle built with `bash scripts/package_arxiv.sh`.
- [x] Output: `paper/build/arxiv_source_upload.zip`.
- [x] Staging tree: `paper/build/arxiv_source_staging/`.
- [x] Isolated compile (`cd paper/build/arxiv_source_staging && latexmk -pdf main.tex`) produces a 28-page PDF with 0 undefined citations and 0 undefined references (checked by unzipping the upload bundle into a clean directory and running pdflatex twice).
- [x] Manifest with sha256 hashes: `paper/submission/arxiv_source_manifest.txt`.

Bundle contents (24 files):
```
main.tex
macros.tex
main.bbl
bib/references.bib
sections/00_title_abstract.tex  ...  sections/appendix_b_version_history.tex  (13 files)
figures/fig_gap.tex
figures/fig_pressure.tex
figures/fig_split_merge.tex
figures/fig_update_loop.tex
tables/tbl_nonredundancy.tex
tables/tbl_shell_certificates.tex
tables/tbl_verification.tex
```

## Section E --- Metadata sanity

- [x] `pdftitle` matches manuscript title.
- [x] `pdfauthor` matches author (Ioannis Tsiokos, ORCID 0009-0009-7659-5964).
- [x] Footer on first page carries affiliation, email, copyright, CC-BY 4.0, preprint notice, and the Zenodo v3 DOI 10.5281/zenodo.23126110.
- [x] Date line carries version history: `v1: 31 March 2026 · v2: 19 April 2026 · v3: 3 October 2026`.
- [x] `CC-BY 4.0` declared in footer.
