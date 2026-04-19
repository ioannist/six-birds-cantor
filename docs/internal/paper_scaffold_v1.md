# Paper Scaffold v1

- Paper workspace: `paper/`
- LaTeX class/toolchain: `article` with `latexmk` build target and `pdflatex`/`bibtex` fallback
- Main entrypoint: `paper/main.tex`
- Section files: `paper/sections/`
- Figures/tables directories:
  - `paper/figures/`
  - `paper/tables/`
- Bibliography file: `paper/bib/references.bib`
- Root build commands:
  - `make paper-build`
  - `make paper-clean`
  - `make paper-bib`
  - `make paper-rebuild`
- Future substantive content will go into the section files under `paper/sections/`
- Substantive prose is intentionally deferred; this ticket only establishes scaffold and compile wiring
