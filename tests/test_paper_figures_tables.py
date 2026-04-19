from pathlib import Path


FIGURE_TABLE_FILES = [
    "paper/figures/fig_full_loop_continuous_substrate_regime.tex",
    "paper/figures/fig_primitive_knockout_closure.tex",
    "paper/tables/tbl_pressure_closure_support.tex",
    "paper/tables/tbl_strict_theory_extension.tex",
    "paper/tables/tbl_conditional_disintegration.tex",
    "paper/tables/tbl_closure_deficit_proxy_diagnostic.tex",
]


def test_figure_and_table_files_exist() -> None:
    for rel_path in FIGURE_TABLE_FILES:
        assert Path(rel_path).exists(), rel_path


def test_sections_and_appendix_include_required_inputs() -> None:
    assert r"\input{figures/fig_full_loop_continuous_substrate_regime}" in Path(
        "paper/sections/04_lawfulness.tex"
    ).read_text()
    assert r"\input{figures/fig_primitive_knockout_closure}" in Path(
        "paper/sections/04_lawfulness.tex"
    ).read_text()
    assert r"\input{tables/tbl_pressure_closure_support}" in Path(
        "paper/sections/05_cocycle_pressure.tex"
    ).read_text()
    assert r"\input{tables/tbl_strict_theory_extension}" in Path(
        "paper/sections/06_strict_extension.tex"
    ).read_text()
    assert r"\input{tables/tbl_conditional_disintegration}" in Path(
        "paper/sections/07_conditional_disintegration.tex"
    ).read_text()
    assert r"\input{tables/tbl_closure_deficit_proxy_diagnostic}" in Path(
        "paper/sections/appendix_a_supporting_evidence.tex"
    ).read_text()


def test_captions_are_theorem_safe() -> None:
    core_files = [
        "paper/figures/fig_full_loop_continuous_substrate_regime.tex",
        "paper/figures/fig_primitive_knockout_closure.tex",
        "paper/tables/tbl_pressure_closure_support.tex",
        "paper/tables/tbl_strict_theory_extension.tex",
        "paper/tables/tbl_conditional_disintegration.tex",
    ]
    forbidden_phrases = [
        "broader-class theorem",
        "non-SFT",
        "direct stratumwise root-separation theorem",
        "packaging-induced broader theorem class",
    ]

    for rel_path in core_files:
        text = Path(rel_path).read_text()
        assert "audited shell" in text, rel_path
        for phrase in forbidden_phrases:
            assert phrase not in text, (rel_path, phrase)

    support_text = Path(
        "paper/tables/tbl_closure_deficit_proxy_diagnostic.tex"
    ).read_text()
    assert "support-only" in support_text
    for phrase in forbidden_phrases:
        assert phrase not in support_text, phrase
