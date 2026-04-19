# arXiv Submission Dry-Run Checklist --- Six Birds: Cantor

Paper: **Strict Theory Extension on a Lawful Continuous Cantor Shell**
Version: v2 (arXiv resubmission; paper footer carries no external DOI).

## Section A --- Build + integrity

- [x] `latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex` succeeds (exit 0).
- [x] Undefined citations count = 0.
- [x] Undefined references count = 0.
- [x] Output: `paper/build/main.pdf` (22 pages, 380 KB).

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
- [x] Keywords file exists: `paper/submission/keywords.txt` (7 keywords, hyphenated only).
- [x] AI disclosure file exists: `paper/submission/ai_disclosure.txt`.

Highlights line-length table:

| # | Length | Text |
|---:|---:|---|
| 1 | 77 | Audited-shell theorem package for a canonical hybrid continuous Cantor object |
| 2 | 74 | Lawful full-loop theoremlet for six-primitive continuous Cantor substrates |
| 3 | 76 | Cocycle pressure closure proved on a shell-stable class of lawful substrates |
| 4 | 80 | Strict theory extension from a packaging/completion endomap, not a redescription |
| 5 | 84 | Thermodynamic consequence: conditional pressure disintegration over packaging fibers |

## Section C --- Figures and sources

- [x] All figures are TikZ `.tex` fragments under `paper/figures/` (no bitmap assets).
- [x] All tables are LaTeX `.tex` fragments under `paper/tables/`.
- [x] No EPS files; no `\includegraphics` bitmap dependencies.
- [x] All `\input` targets in `main.tex` resolve inside the bundle (sections/figures/tables + macros).
- [x] Bibliography embedded via `main.bbl`; `bib/references.bib` also included for verification.

Figure inventory:

| File | Type | Referenced in |
|---|---|---|
| figures/fig_full_loop_continuous_substrate_regime.tex | TikZ | sections/04_lawfulness.tex |
| figures/fig_primitive_knockout_closure.tex | TikZ | sections/04_lawfulness.tex |

Table inventory:

| File | Referenced in |
|---|---|
| tables/tbl_pressure_closure_support.tex | sections/05_cocycle_pressure.tex |
| tables/tbl_strict_theory_extension.tex | sections/06_strict_extension.tex |
| tables/tbl_conditional_disintegration.tex | sections/07_conditional_disintegration.tex |
| tables/tbl_closure_deficit_proxy_diagnostic.tex | sections/appendix_a_supporting_evidence.tex |

## Section D --- Bundle verification

- [x] Bundle built with `bash scripts/package_arxiv.sh`.
- [x] Output: `paper/build/arxiv_source_upload.zip`.
- [x] Staging tree: `paper/build/arxiv_source_staging/`.
- [x] Isolated compile (`cd paper/build/arxiv_source_staging && latexmk -pdf main.tex`) produces a byte-identical 22-page PDF with 0 undefined citations and 0 undefined references.
- [x] Manifest with sha256 hashes: `paper/submission/arxiv_source_manifest.txt`.

Bundle contents (21 files):
```
main.tex
macros.tex
main.bbl
bib/references.bib
sections/00_title_abstract.tex  ...  sections/appendix_a_supporting_evidence.tex  (11 files)
figures/fig_full_loop_continuous_substrate_regime.tex
figures/fig_primitive_knockout_closure.tex
tables/tbl_closure_deficit_proxy_diagnostic.tex
tables/tbl_conditional_disintegration.tex
tables/tbl_pressure_closure_support.tex
tables/tbl_strict_theory_extension.tex
```

## Section E --- Metadata sanity

- [x] `pdftitle` matches manuscript title.
- [x] `pdfauthor` matches author (Ioannis Tsiokos, ORCID 0009-0009-7659-5964).
- [x] Footer on first page carries affiliation, email, copyright, CC-BY 4.0, preprint notice (no external DOI).
- [x] Date line carries version marker: `\today  \textperiodcentered  v2`.
- [x] `CC-BY 4.0` declared in footer.
