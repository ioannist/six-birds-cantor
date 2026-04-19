from pathlib import Path


def test_discussion_section_contains_required_content() -> None:
    path = Path("paper/sections/09_discussion.tex")
    assert path.exists()
    text = path.read_text()

    for phrase in [
        "theorem of theory depth",
        "audited shell",
        "What the paper does not claim",
        "Reserve and stretch routes",
        "Future work",
        "broader-class theorem beyond the audited shell",
        "shell-general theorem",
        "external or non-SFT breadth theorem",
        "direct stratumwise root-separation theorem",
        "packaging-induced broader theorem class claim",
        "exact KL-based closure-deficit theorem",
        "Broader shell stability",
        "Further thermodynamic consequences",
        "Broader object classes",
    ]:
        assert phrase in text
