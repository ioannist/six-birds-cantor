from pathlib import Path


def test_introduction_exists_and_contains_required_phrases():
    path = Path("paper/sections/01_introduction.tex")
    assert path.exists()
    text = path.read_text()

    for phrase in [
        "operator rewrite",
        "admissibility gating",
        "protocol/timescale adaptation",
        "lens selection",
        "packaging/completion",
        "budget/ledger dynamics",
        "continuous full-loop lawfulness theoremlet",
        "cocycle pressure closure theoremlet",
        "strict theory extension theoremlet",
        "conditional pressure disintegration theoremlet",
        "broader-class theorem",
        "direct stratumwise root-separation theorem",
    ]:
        assert phrase in text


def test_referenced_section_labels_exist_in_target_files():
    targets = {
        "paper/sections/02_preliminaries.tex": r"\label{sec:preliminaries}",
        "paper/sections/03_canonical_object.tex": r"\label{sec:canonical-object}",
        "paper/sections/04_lawfulness.tex": r"\label{sec:lawfulness}",
        "paper/sections/05_cocycle_pressure.tex": r"\label{sec:cocycle-pressure}",
        "paper/sections/06_strict_extension.tex": r"\label{sec:strict-extension}",
        "paper/sections/07_conditional_disintegration.tex": r"\label{sec:conditional-disintegration}",
        "paper/sections/08_related_work.tex": r"\label{sec:related-work}",
        "paper/sections/09_discussion.tex": r"\label{sec:discussion}",
        "paper/sections/appendix_a_supporting_evidence.tex": r"\label{sec:appendix-supporting-evidence}",
    }

    for file_path, label in targets.items():
        text = Path(file_path).read_text()
        assert label in text
