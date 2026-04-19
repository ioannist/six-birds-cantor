#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAPER_DIR = ROOT / "paper"
BUILD_DIR = PAPER_DIR / "build"
LOG_PATH = BUILD_DIR / "main.log"
PDF_PATH = BUILD_DIR / "main.pdf"


def run_build() -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["make", "paper-build"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def findall(pattern: str, text: str) -> list[str]:
    return re.findall(pattern, text, flags=re.MULTILINE)


def parse_log(text: str) -> dict:
    undefined_citations = findall(r"LaTeX Warning: Citation `([^']+)'", text)
    undefined_references = findall(r"LaTeX Warning: Reference `([^']+)'", text)
    duplicate_labels = findall(r"LaTeX Warning: Label `([^']+)' multiply defined", text)
    latex_errors = findall(r"^! (.+)$", text)

    overfull_matches = re.findall(
        r"Overfull \\hbox \(([^)]+) too wide\).*?at lines? ([0-9]+(?:--[0-9]+)?)",
        text,
        flags=re.DOTALL,
    )
    underfull_matches = re.findall(
        r"Underfull \\hbox .*?at lines? ([0-9]+(?:--[0-9]+)?)",
        text,
        flags=re.DOTALL,
    )

    overfull_boxes = [
        {"amount": amount, "lines": lines} for amount, lines in overfull_matches
    ]
    underfull_boxes = [{"lines": lines} for lines in underfull_matches]

    major_warnings = []
    for item in overfull_boxes:
        try:
            width = float(item["amount"].replace("pt", ""))
        except ValueError:
            width = 0.0
        if width > 10.0:
            major_warnings.append(
                {
                    "type": "overfull_hbox",
                    "amount": item["amount"],
                    "lines": item["lines"],
                }
            )

    bibliography_toolchain_failures = []
    if "BibTeX, Version" not in text and "\\bibliography" in (PAPER_DIR / "main.tex").read_text():
        bibliography_toolchain_failures.append("bibtex_not_observed")

    return {
        "undefined_citations": undefined_citations,
        "undefined_references": undefined_references,
        "duplicate_labels": duplicate_labels,
        "latex_errors": latex_errors,
        "overfull_boxes": overfull_boxes,
        "underfull_boxes": underfull_boxes,
        "major_warnings": major_warnings,
        "bibliography_toolchain_failures": bibliography_toolchain_failures,
    }


def main() -> None:
    build = run_build()
    log_text = LOG_PATH.read_text(errors="ignore") if LOG_PATH.exists() else ""
    parsed = parse_log(log_text)

    theorem_labels = []
    for path in (PAPER_DIR / "sections").glob("*.tex"):
        theorem_labels.extend(re.findall(r"\\label\{(thm:[^}]+)\}", path.read_text()))

    report = {
        "build_exit_code": build.returncode,
        "pdf_exists": PDF_PATH.exists(),
        "pdf_path": str(PDF_PATH.relative_to(ROOT)),
        "undefined_citations": parsed["undefined_citations"],
        "undefined_references": parsed["undefined_references"],
        "duplicate_labels": parsed["duplicate_labels"],
        "latex_errors": parsed["latex_errors"],
        "major_warnings": parsed["major_warnings"],
        "overfull_boxes": parsed["overfull_boxes"],
        "underfull_boxes": parsed["underfull_boxes"],
        "bibliography_toolchain_failures": parsed["bibliography_toolchain_failures"],
        "theorem_labels": sorted(theorem_labels),
        "cross_reference_status": "stable"
        if not parsed["undefined_references"] and not parsed["duplicate_labels"]
        else "unstable",
        "citation_status": "stable"
        if not parsed["undefined_citations"] and not parsed["bibliography_toolchain_failures"]
        else "unstable",
        "final_readiness_decision": "near_final_clean_compile"
        if build.returncode == 0
        and PDF_PATH.exists()
        and not parsed["undefined_citations"]
        and not parsed["undefined_references"]
        and not parsed["duplicate_labels"]
        and not parsed["latex_errors"]
        and not parsed["major_warnings"]
        else "needs_cleanup",
    }

    results_dir = ROOT / "results/paper_compile_cleanup"
    results_dir.mkdir(parents=True, exist_ok=True)
    (results_dir / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True))

    csv_lines = ["kind,value,status"]
    for key in ["undefined_citations", "undefined_references", "duplicate_labels", "latex_errors"]:
        for value in report[key]:
            csv_lines.append(f"{key},{value},present")
    for item in report["overfull_boxes"]:
        csv_lines.append(f"overfull,{item['amount']}@{item['lines']},logged")
    for item in report["major_warnings"]:
        csv_lines.append(f"major_warning,{item['amount']}@{item['lines']},present")
    (results_dir / "report.csv").write_text("\n".join(csv_lines) + "\n")


if __name__ == "__main__":
    main()
