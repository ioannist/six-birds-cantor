from pathlib import Path


def test_related_work_section_contains_required_citations_and_phrases() -> None:
    path = Path("paper/sections/08_related_work.tex")
    assert path.exists()
    text = path.read_text()

    for key in [
        "FalconerFractalGeometry",
        "MauldinUrbanskiGDMS",
        "BarreiraNonadditiveTF",
        "OliveiraVarandasLocalIFS",
        "TsiokosFoundations",
        "TsiokosCreateStone",
        "TsiokosCastStone",
    ]:
        assert key in text

    for phrase in [
        "Cantor mathematics paper",
        "theorem of theory depth",
        "not a general six-birds framework paper",
        "does not prove a broader-class theorem beyond the audited shell",
        "does not prove a direct stratumwise root-separation theorem",
    ]:
        assert phrase in text


def test_bibliography_contains_required_keys() -> None:
    text = Path("paper/bib/references.bib").read_text()

    for key in [
        "FalconerFractalGeometry",
        "MauldinUrbanskiGDMS",
        "BarreiraNonadditiveTF",
        "OliveiraVarandasLocalIFS",
        "TsiokosFoundations",
        "TsiokosCreateStone",
        "TsiokosCastStone",
    ]:
        assert key in text
