import json
from pathlib import Path


def test_compile_cleanup_report_exists_and_loads() -> None:
    path = Path("results/paper_compile_cleanup/report.json")
    assert path.exists()
    data = json.loads(path.read_text())

    for key in [
        "pdf_exists",
        "undefined_citations",
        "undefined_references",
        "duplicate_labels",
        "latex_errors",
        "major_warnings",
    ]:
        assert key in data


def test_compile_cleanup_report_is_near_final_clean() -> None:
    data = json.loads(Path("results/paper_compile_cleanup/report.json").read_text())

    assert data["pdf_exists"] is True
    assert data["undefined_citations"] == []
    assert data["undefined_references"] == []
    assert data["duplicate_labels"] == []
    assert data["latex_errors"] == []
    assert data["major_warnings"] == []
