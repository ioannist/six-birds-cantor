from pathlib import Path


def test_supporting_evidence_appendix_contains_required_content() -> None:
    path = Path("paper/sections/appendix_a_supporting_evidence.tex")
    assert path.exists()
    text = path.read_text()

    for phrase in [
        "continuous pilot",
        "regime diagnostics",
        "pressure-closure checks",
        "strict-extension audit",
        "conditional-disintegration support checks",
        "supportive rather than foundational",
        "audited shell",
        "not a direct stratumwise root-separation statement",
        r"\emph{not} part of any closed theorem statement",
        "broader-class theorem",
        "shell-general theorem",
        "external/non-SFT breadth theorem",
        "packaging-induced broader theorem-class claim",
    ]:
        assert phrase in text


def test_supporting_evidence_appendix_contains_required_references() -> None:
    text = Path("paper/sections/appendix_a_supporting_evidence.tex").read_text()

    assert "none of them enlarges the claim scope of the main text" in text
    assert r"\ref{fig:full-loop-regime}" in text
    assert r"\ref{fig:primitive-knockout-closure}" in text
    assert r"\ref{tbl:pressure-closure-support}" in text
    assert r"\ref{tbl:strict-theory-extension}" in text
    assert r"\ref{tbl:conditional-disintegration}" in text
    assert r"\input{tables/tbl_closure_deficit_proxy_diagnostic}" in text
