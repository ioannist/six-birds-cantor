#!/usr/bin/env bash
# Build an arXiv source upload bundle for the Cantor paper.
#
# Adapted from six-birds-agent/scripts/package_arxiv.sh. Differences:
#   - main source is paper/main.tex (not agency.tex)
#   - preamble lives inline in main.tex; shared macros are in paper/macros.tex
#   - figures are TikZ .tex files under paper/figures/ (no bitmap assets)
#   - tables are LaTeX fragments under paper/tables/
#   - bib file is paper/bib/references.bib
#   - main.bbl is sourced from paper/build/
#
# Output: paper/build/arxiv_source_upload.zip
#         paper/build/arxiv_source_staging/   (staging tree used for the zip)

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PAPER_DIR="$ROOT_DIR/paper"
BUILD_DIR="$PAPER_DIR/build"
STAGE_DIR="$BUILD_DIR/arxiv_source_staging"
ZIP_PATH="$BUILD_DIR/arxiv_source_upload.zip"

if [[ ! -f "$PAPER_DIR/main.tex" ]]; then
  echo "[package_arxiv] ERROR: $PAPER_DIR/main.tex not found." >&2
  exit 2
fi

if [[ ! -f "$BUILD_DIR/main.bbl" ]]; then
  echo "[package_arxiv] ERROR: $BUILD_DIR/main.bbl not found; build the paper first (latexmk)." >&2
  exit 3
fi

rm -rf "$STAGE_DIR"
mkdir -p "$STAGE_DIR/sections" "$STAGE_DIR/figures" "$STAGE_DIR/tables" "$STAGE_DIR/bib"

cp "$PAPER_DIR/main.tex"    "$STAGE_DIR/main.tex"
cp "$PAPER_DIR/macros.tex"  "$STAGE_DIR/macros.tex"
cp "$BUILD_DIR/main.bbl"    "$STAGE_DIR/main.bbl"
cp "$PAPER_DIR/bib/references.bib" "$STAGE_DIR/bib/references.bib"

if compgen -G "$PAPER_DIR/sections/*.tex" > /dev/null; then
  cp "$PAPER_DIR/sections/"*.tex "$STAGE_DIR/sections/"
fi

if compgen -G "$PAPER_DIR/figures/*.tex" > /dev/null; then
  cp "$PAPER_DIR/figures/"*.tex "$STAGE_DIR/figures/"
fi

if compgen -G "$PAPER_DIR/tables/*.tex" > /dev/null; then
  cp "$PAPER_DIR/tables/"*.tex "$STAGE_DIR/tables/"
fi

for ext in png jpg pdf; do
  if compgen -G "$PAPER_DIR/figures/*.$ext" > /dev/null; then
    cp "$PAPER_DIR/figures/"*.$ext "$STAGE_DIR/figures/"
  fi
done

if compgen -G "$PAPER_DIR/figures/*.eps" > /dev/null; then
  echo "[package_arxiv] ERROR: EPS figures detected; convert to PDF/PNG." >&2
  exit 4
fi

find "$STAGE_DIR" -name "*.aux" -o -name "*.log" -o -name "*.out" -o -name "*.toc" -o -name "*.fls" -o -name "*.fdb_latexmk" -o -name "*.blg" | xargs -r rm -f

rm -f "$ZIP_PATH"
(
  cd "$STAGE_DIR"
  zip -r "$ZIP_PATH" . >/dev/null
)

echo "[package_arxiv] Wrote $ZIP_PATH"
(cd "$STAGE_DIR" && find . -type f | sort | sed 's|^\./|  |')
