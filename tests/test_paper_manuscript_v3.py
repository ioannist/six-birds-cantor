"""Structural checks for the v3 manuscript (paper/)."""

from pathlib import Path
import re

PAPER = Path("paper")
TITLE = "Strict Theory Extension on a Lawful Continuous Cantor Shell"
SECTIONS = [
    "00_title_abstract",
    "01_introduction",
    "02_substrate",
    "03_controlled_shell",
    "04_growth_pressure",
    "05_completion_objects",
    "06_strict_extension",
    "07_pressure_disintegration",
    "08_verification",
    "09_related_work",
    "10_discussion",
    "appendix_a_witness_data",
    "appendix_b_version_history",
]


def _body() -> str:
    return "\n".join((PAPER / "sections" / f"{name}.tex").read_text() for name in SECTIONS)


def _all_tex() -> str:
    parts = [_body()]
    for folder in ("figures", "tables"):
        parts += [p.read_text() for p in sorted((PAPER / folder).glob("*.tex"))]
    return "\n".join(parts)


def test_main_includes_every_section_in_order() -> None:
    main = (PAPER / "main.tex").read_text()
    positions = [main.index(f"\\input{{sections/{name}}}") for name in SECTIONS]
    assert positions == sorted(positions)
    assert main.index("\\appendix") < positions[SECTIONS.index("appendix_a_witness_data")]


def test_title_and_version_line() -> None:
    front = (PAPER / "sections" / "00_title_abstract.tex").read_text()
    assert TITLE in " ".join(front.replace("\\\\", " ").split())
    assert "v1: 31 March 2026" in front
    assert "v2: 19 April 2026" in front
    assert "v3: 3 October 2026" in front


def test_main_results_are_labelled_and_referenced() -> None:
    text = _all_tex()
    for label in ("thm:shell", "thm:pressure", "thm:strict-extension", "thm:blindness",
                  "prop:finite-disintegration", "prop:zero-gap", "prop:positive-gap"):
        assert f"\\label{{{label}}}" in text, label
        assert f"\\ref{{{label}}}" in text, label


def test_every_input_and_reference_resolves() -> None:
    text = _all_tex()
    for path in re.findall(r"\\input\{((?:figures|tables)/[^}]+)\}", text):
        assert (PAPER / f"{path}.tex").exists(), path
    labels = set(re.findall(r"\\label\{([^}]+)\}", text))
    for ref in re.findall(r"\\ref\{([^}]+)\}", text):
        assert ref in labels, ref


def test_citations_exist_in_bibliography() -> None:
    bib = (PAPER / "bib" / "references.bib").read_text()
    keys = set(re.findall(r"@\w+\{([^,]+),", bib))
    for group in re.findall(r"\\cite[pt]?(?:\[[^\]]*\])?\{([^}]+)\}", _all_tex()):
        for key in group.split(","):
            assert key.strip() in keys, key


def test_revision_language_confined_to_version_history() -> None:
    body = "\n".join(
        (PAPER / "sections" / f"{name}.tex").read_text()
        for name in SECTIONS
        if name != "appendix_b_version_history"
    )
    for phrase in ("theoremlet", "audited shell", "v1/v2", "previous version", "revised version"):
        assert phrase not in body, phrase


def test_withdrawn_gap_implication_is_not_asserted() -> None:
    text = _body()
    assert "does not force a conditional pressure gap" in text
    assert "zero gap" in text and "positive gap" in text
