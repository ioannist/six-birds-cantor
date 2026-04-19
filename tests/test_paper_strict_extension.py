from pathlib import Path


def test_strict_extension_section_exists_and_contains_required_content() -> None:
    path = Path("paper/sections/06_strict_extension.tex")
    assert path.exists()
    text = path.read_text()

    assert "strict theory extension" in text
    assert r"P4\leftarrow P5" in text
    assert r"\pi_1=\phi\circ \pi_0" in text
    assert "macro-admissibility obstruction" in text
    assert r"Theorem~\ref{thm:strict-extension}" in text
    assert "audited shell" in text
    assert r"\label{thm:strict-extension}" in text
    assert "theorem of theory depth" in text


def test_strict_extension_section_contains_scope_limitations() -> None:
    text = Path("paper/sections/06_strict_extension.tex").read_text()

    assert "does not claim a broader theorem class" in text
    assert "shell-general extension theorem" in text
    assert "external/non-SFT breadth theorem" in text
