from pathlib import Path
import re


TITLE = "Strict Theory Extension on a Lawful Continuous Cantor Shell"


def test_frontmatter_files_exist():
    assert Path("paper/sections/00_title_abstract.tex").exists()
    assert Path("docs/internal/paper_title_shortlist_v1.md").exists()
    assert Path("docs/internal/theorem_facing_summary_v1.md").exists()


def test_frontmatter_contains_required_title_and_phrases():
    text = Path("paper/sections/00_title_abstract.tex").read_text()
    normalized = re.sub(r"\\\\", " ", text)
    normalized = " ".join(normalized.split())
    assert TITLE in normalized
    assert "continuous Cantor substrates" in text
    assert "strict theory-extension theoremlet" in text
    assert "conditional pressure disintegration" in text
    assert "audited shell" in text
