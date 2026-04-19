from pathlib import Path


def test_lawfulness_section_exists_and_contains_required_content() -> None:
    path = Path("paper/sections/04_lawfulness.tex")
    assert path.exists()
    text = path.read_text()

    assert "continuous full-loop lawfulness" in text
    assert r"\mathcal{S}_{\mathrm{aud}}" in text
    assert "P1" in text
    assert "P6" in text
    assert r"Theorem~\ref{thm:lawfulness}" in text
    assert "audited shell" in text
    assert "nontrivial lawful exploratory regime" in text
    assert r"\label{thm:lawfulness}" in text


def test_lawfulness_section_contains_scope_limitations() -> None:
    text = Path("paper/sections/04_lawfulness.tex").read_text()

    assert "does not assert a shell-general lawfulness theorem" in text
    assert "broader-class theorem" in text
    assert "external/non-SFT breadth" in text
