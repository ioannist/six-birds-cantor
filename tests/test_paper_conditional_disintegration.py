from pathlib import Path


def test_conditional_disintegration_section_exists_and_contains_required_content() -> None:
    path = Path("paper/sections/07_conditional_disintegration.tex")
    assert path.exists()
    text = path.read_text()

    assert "conditional pressure disintegration" in text
    assert r"\Delta_{\Tzero\to \Tone}(s)" in text
    assert "weighted package-conditioned pressure gap" in text
    assert r"Theorem~\ref{thm:conditional-disintegration}" in text
    assert "audited shell" in text
    assert r"\label{thm:conditional-disintegration}" in text
    assert r"\emph{not} the route taken here" in text
    assert "direct stratumwise root-separation theorem" in text


def test_conditional_disintegration_section_contains_scope_limitations() -> None:
    text = Path("paper/sections/07_conditional_disintegration.tex").read_text()

    assert "broader-class thermodynamic theorem" in text
    assert "shell-general theorem" in text
    assert "external/non-SFT breadth theorem" in text
