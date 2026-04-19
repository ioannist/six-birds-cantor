from pathlib import Path


def test_preliminaries_exists_and_contains_required_anchors():
    path = Path("paper/sections/02_preliminaries.tex")
    assert path.exists()
    text = path.read_text()

    for anchor in [
        r"\mathcal{S}_{\mathrm{aud}}",
        r"\pi_0",
        r"\pi_1",
        r"E_{\tau,\ell}",
        r"\mathfrak{H}(x)",
        r"P_{\Tzero}(s)",
        r"\Delta_{\Tzero\to \Tone}(s)",
    ]:
        assert anchor in text


def test_preliminaries_contains_required_phrases_and_nonclaims():
    text = Path("paper/sections/02_preliminaries.tex").read_text()

    for phrase in [
        "canonical hybrid object",
        "packaged stratum",
        "factorization",
        "macro-admissibility obstruction",
        "broader-class theorem",
        "direct stratumwise root-separation theorem",
    ]:
        assert phrase in text
