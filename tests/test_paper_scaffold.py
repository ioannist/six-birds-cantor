from pathlib import Path


def test_paper_scaffold_files_exist():
    required_paths = [
        "paper/main.tex",
        "paper/macros.tex",
        "paper/sections/00_title_abstract.tex",
        "paper/sections/01_introduction.tex",
        "paper/sections/02_preliminaries.tex",
        "paper/sections/03_canonical_object.tex",
        "paper/sections/04_lawfulness.tex",
        "paper/sections/05_cocycle_pressure.tex",
        "paper/sections/06_strict_extension.tex",
        "paper/sections/07_conditional_disintegration.tex",
        "paper/sections/08_related_work.tex",
        "paper/sections/09_discussion.tex",
        "paper/sections/appendix_a_supporting_evidence.tex",
        "paper/bib/references.bib",
        "docs/internal/paper_scaffold_v1.md",
    ]
    for path in required_paths:
        assert Path(path).exists(), path


def test_makefile_has_paper_targets():
    makefile = Path("Makefile").read_text()
    assert "paper-build" in makefile
    assert "paper-clean" in makefile
