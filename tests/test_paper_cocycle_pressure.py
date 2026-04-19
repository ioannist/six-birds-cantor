from pathlib import Path


def test_cocycle_pressure_section_exists_and_contains_required_content() -> None:
    path = Path("paper/sections/05_cocycle_pressure.tex")
    assert path.exists()
    text = path.read_text()

    assert "Fekete-sup cocycle route" in text
    assert "selector-weighted operator growth observable" in text
    assert r"\Phi_n(s)" in text
    assert r"P_{\Tzero}(s)" in text
    assert r"Theorem~\ref{thm:cocycle-pressure}" in text
    assert "audited shell" in text
    assert r"\label{thm:cocycle-pressure}" in text


def test_cocycle_pressure_section_contains_scope_limitations() -> None:
    text = Path("paper/sections/05_cocycle_pressure.tex").read_text()

    assert "does not yet define the packaged-object theory" in text
    assert "broader-class pressure theorem" in text
    assert "direct stratumwise thermodynamic distinction" in text
