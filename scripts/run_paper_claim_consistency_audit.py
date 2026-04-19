#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

FROZEN_FILES = {
    "claim_ledger": ROOT / "docs/internal/final_paper_core_claim_ledger_v1.json",
    "traceability": ROOT / "docs/internal/theorem_traceability_matrix_v1.json",
    "delta_map": ROOT / "docs/internal/contribution_delta_map_v1.json",
    "risk_audit": ROOT / "docs/internal/publication_risk_audit_v1.json",
    "theorem_package": ROOT / "docs/internal/level3_theorem_package_v1.json",
    "figure_manifest": ROOT / "docs/internal/figure_manifest_v1.json",
}

MANUSCRIPT_FILES = [
    ROOT / "paper/sections/00_title_abstract.tex",
    ROOT / "paper/sections/01_introduction.tex",
    ROOT / "paper/sections/02_preliminaries.tex",
    ROOT / "paper/sections/03_canonical_object.tex",
    ROOT / "paper/sections/04_lawfulness.tex",
    ROOT / "paper/sections/05_cocycle_pressure.tex",
    ROOT / "paper/sections/06_strict_extension.tex",
    ROOT / "paper/sections/07_conditional_disintegration.tex",
    ROOT / "paper/sections/08_related_work.tex",
    ROOT / "paper/sections/09_discussion.tex",
    ROOT / "paper/sections/appendix_a_supporting_evidence.tex",
]

FIGURE_TABLE_FILES = sorted((ROOT / "paper/figures").glob("*.tex")) + sorted(
    (ROOT / "paper/tables").glob("*.tex")
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def main() -> None:
    frozen = {name: load_json(path) for name, path in FROZEN_FILES.items()}

    allowed_theoremlets = [
        t["theoremlet_id"] for t in frozen["theorem_package"]["included_theoremlets"]
    ]
    nonclaim_strings = frozen["theorem_package"]["nonclaims"]
    reserve_routes = frozen["theorem_package"]["reserve_routes"]
    claim_ledger = frozen["claim_ledger"]["claims"]
    support_only_ids = [
        c["claim_id"] for c in claim_ledger if c["claim_status"] == "supporting_evidence"
    ]

    theorem_labels = {
        "continuous_full_loop_lawfulness_theoremlet": r"\label{thm:lawfulness}",
        "cocycle_pressure_closure_theoremlet": r"\label{thm:cocycle-pressure}",
        "strict_theory_extension_theoremlet": r"\label{thm:strict-extension}",
        "conditional_pressure_disintegration_theoremlet": r"\label{thm:conditional-disintegration}",
    }

    manuscript_text = {rel(path): path.read_text() for path in MANUSCRIPT_FILES}
    figure_table_text = {rel(path): path.read_text() for path in FIGURE_TABLE_FILES}

    theoremlet_presence = {
        theoremlet_id: any(label in text for text in manuscript_text.values())
        for theoremlet_id, label in theorem_labels.items()
    }

    extra_theorem_labels = []
    allowed_label_values = set(theorem_labels.values())
    for file_path, text in manuscript_text.items():
        labels = re.findall(r"\\label\{thm:[^}]+\}", text)
        for label in labels:
            if label not in allowed_label_values:
                extra_theorem_labels.append({"file": file_path, "label": label})

    forbidden_positive_patterns = [
        "broad new theorem class",
        "general local-IFS theorem",
        "direct stratumwise thermodynamic distinction",
        "non-SFT breadth result in the strong external sense",
    ]
    forbidden_claim_hit_list = []
    for file_path, text in manuscript_text.items():
        lower = text.lower()
        for pattern in forbidden_positive_patterns:
            search = pattern.lower()
            start = 0
            while True:
                idx = lower.find(search, start)
                if idx == -1:
                    break
                window = lower[max(0, idx - 120) : idx]
                negated = any(
                    token in window
                    for token in ["does not", "do not", "not a", "not the", "rather than"]
                )
                negated = negated or any(
                    token in window for token in ["does not claim", "or any", "remain outside"]
                )
                if not negated:
                    forbidden_claim_hit_list.append(
                        {"file": file_path, "pattern": pattern}
                    )
                start = idx + len(search)

    scope_required_sections = [
        "paper/sections/00_title_abstract.tex",
        "paper/sections/01_introduction.tex",
        "paper/sections/02_preliminaries.tex",
        "paper/sections/04_lawfulness.tex",
        "paper/sections/05_cocycle_pressure.tex",
        "paper/sections/06_strict_extension.tex",
        "paper/sections/07_conditional_disintegration.tex",
        "paper/sections/09_discussion.tex",
    ]
    section_level_mismatch_summary = []
    for file_path in scope_required_sections:
        text = manuscript_text[file_path]
        if "audited shell" not in text:
            section_level_mismatch_summary.append(
                {"file": file_path, "issue": "missing audited-shell qualifier"}
            )

    figure_manifest = frozen["figure_manifest"]
    allowed_bindings = {
        binding["figure_id"]: binding["claim_id"]
        for binding in figure_manifest["allowed_claim_bindings"]
    }
    support_only_reference_only_hit_list = []
    figure_table_binding_summary = []
    for file_path, text in figure_table_text.items():
        stem = Path(file_path).stem
        if stem == "tbl_closure_deficit_proxy_diagnostic":
            if "support-only" in text:
                support_only_reference_only_hit_list.append(
                    {"file": file_path, "claim_id": support_only_ids[0], "status": "support-only"}
                )
            else:
                section_level_mismatch_summary.append(
                    {"file": file_path, "issue": "support-only table missing support-only marker"}
                )
        if stem in allowed_bindings:
            figure_table_binding_summary.append(
                {
                    "file": file_path,
                    "binding_claim_id": allowed_bindings[stem],
                    "status": "allowed",
                }
            )
        elif stem == "fig_stratumwise_root_separation_diagnostic":
            figure_table_binding_summary.append(
                {
                    "file": file_path,
                    "binding_claim_id": "no_direct_stratumwise_root-separation_theorem",
                    "status": "reserve-only",
                }
            )
        else:
            figure_table_binding_summary.append(
                {"file": file_path, "binding_claim_id": None, "status": "unbound"}
            )

    if any(
        r"\input{figures/fig_stratumwise_root_separation_diagnostic}" in text
        for text in manuscript_text.values()
    ):
        forbidden_claim_hit_list.append(
            {
                "file": "paper manuscript",
                "pattern": "reserve stratumwise diagnostic inserted into manuscript",
            }
        )

    patched_file_summary: list[str] = []
    remaining_manual_checks = [
        "Overfull hbox warnings remain in earlier inserted figures/tables and one appendix line; these are typographic rather than semantic.",
    ]

    consistency_decision = (
        "consistent"
        if not forbidden_claim_hit_list
        and not section_level_mismatch_summary
        and not extra_theorem_labels
        and all(theoremlet_presence.values())
        else "inconsistent"
    )

    report = {
        "paper_core_positioning": frozen["theorem_package"]["paper_core_positioning"],
        "decision": consistency_decision,
        "closed_theoremlet_count_found_in_manuscript": sum(theoremlet_presence.values()),
        "closed_theoremlets_found": theoremlet_presence,
        "allowed_claim_ids": allowed_theoremlets,
        "protected_nonclaims": nonclaim_strings,
        "reserve_routes": reserve_routes,
        "forbidden_claim_hit_list": forbidden_claim_hit_list,
        "support_only_reference_only_hit_list": support_only_reference_only_hit_list,
        "figure_table_binding_summary": figure_table_binding_summary,
        "section_level_mismatch_summary": section_level_mismatch_summary,
        "extra_theorem_labels": extra_theorem_labels,
        "patched_file_summary": patched_file_summary,
        "remaining_manual_checks": remaining_manual_checks,
    }

    results_dir = ROOT / "results/paper_claim_consistency"
    results_dir.mkdir(parents=True, exist_ok=True)
    (results_dir / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True))

    csv_lines = ["kind,file_or_id,status_or_note"]
    for theoremlet_id, present in theoremlet_presence.items():
        csv_lines.append(f"theoremlet,{theoremlet_id},{'present' if present else 'missing'}")
    for hit in forbidden_claim_hit_list:
        csv_lines.append(f"forbidden,{hit['file']},{hit['pattern']}")
    for item in support_only_reference_only_hit_list:
        csv_lines.append(f"support,{item['file']},{item['status']}")
    (results_dir / "report.csv").write_text("\n".join(csv_lines) + "\n")


if __name__ == "__main__":
    main()
