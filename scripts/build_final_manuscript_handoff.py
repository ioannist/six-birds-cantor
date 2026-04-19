#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_json(rel_path: str) -> dict:
    return json.loads((ROOT / rel_path).read_text())


def main() -> None:
    prewriting = load_json("docs/internal/final_prewriting_handoff_v1.json")
    theorem_package = load_json("docs/internal/level3_theorem_package_v1.json")
    claim_ledger = load_json("docs/internal/final_paper_core_claim_ledger_v1.json")
    traceability = load_json("docs/internal/theorem_traceability_matrix_v1.json")
    figure_manifest = load_json("docs/internal/figure_manifest_v1.json")
    contribution_delta = load_json("docs/internal/contribution_delta_map_v1.json")
    publication_risk = load_json("docs/internal/publication_risk_audit_v1.json")
    cleanup = load_json("results/paper_compile_cleanup/report.json")

    final_pdf_rel = "paper/build/main.pdf"
    final_pdf_path = ROOT / final_pdf_rel

    closed_theoremlets = prewriting["closed_theoremlets"]
    required_theoremlets = {
        "continuous_full_loop_lawfulness_theoremlet",
        "cocycle_pressure_closure_theoremlet",
        "strict_theory_extension_theoremlet",
        "conditional_pressure_disintegration_theoremlet",
    }
    found_theoremlets = {item["theoremlet_id"] for item in closed_theoremlets}

    nonclaims = theorem_package["nonclaims"]
    reserve_routes = theorem_package["reserve_routes"]

    decision = (
        "ready_with_minor_typographic_warnings"
        if theorem_package["paper_core_positioning"] == "level3_core_on_audited_shell"
        and found_theoremlets == required_theoremlets
        and final_pdf_path.exists()
        and cleanup["undefined_citations"] == []
        and cleanup["undefined_references"] == []
        and cleanup["duplicate_labels"] == []
        and cleanup["latex_errors"] == []
        and cleanup["major_warnings"] == []
        else "not_ready"
    )

    title_line = None
    title_text = (ROOT / "paper/sections/00_title_abstract.tex").read_text()
    for line in title_text.splitlines():
        if line.startswith(r"\title{"):
            title_line = line.removeprefix(r"\title{").removesuffix("}")
            break

    handoff = {
        "schema_version": "1.0",
        "handoff_id": "final_manuscript_handoff_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "paper_core_positioning": theorem_package["paper_core_positioning"],
        "title": title_line,
        "canonical_theorem_object": prewriting["canonical_theorem_object"],
        "closed_class": prewriting["closed_class"],
        "closed_theoremlets": [
            {
                "theoremlet_id": item["theoremlet_id"],
                "status": item["status"],
                "object_scope": item["object_scope"],
                "class_scope": item["class_scope"],
                "dependency_path": item["dependency_path"],
                "witness_families": item["witness_families"],
                "note": item["one_line_scope_limit"],
            }
            for item in closed_theoremlets
            if item["theoremlet_id"] in required_theoremlets
        ],
        "assumption_paths": prewriting["assumption_paths"],
        "dependency_paths": prewriting["dependency_paths"],
        "figure_manifest_path": "docs/internal/figure_manifest_v1.json",
        "claim_ledger_path": "docs/internal/final_paper_core_claim_ledger_v1.json",
        "traceability_matrix_path": "docs/internal/theorem_traceability_matrix_v1.json",
        "publication_risk_audit_path": "docs/internal/publication_risk_audit_v1.json",
        "main_tex_path": "paper/main.tex",
        "final_pdf_path": final_pdf_rel,
        "compile_status": {
            "pdf_exists": cleanup["pdf_exists"],
            "undefined_citations": cleanup["undefined_citations"],
            "undefined_references": cleanup["undefined_references"],
            "duplicate_labels": cleanup["duplicate_labels"],
            "latex_errors": cleanup["latex_errors"],
            "major_warnings": cleanup["major_warnings"],
        },
        "warning_summary": {
            "minor_overfull_boxes": cleanup["overfull_boxes"],
            "underfull_boxes": cleanup["underfull_boxes"],
        },
        "allowed_claim_ids": prewriting["allowed_claim_ids"],
        "support_only_ids": prewriting["support_only_ids"],
        "reserve_ids": prewriting["reserve_ids"],
        "nonclaim_ids": prewriting["nonclaim_ids"],
        "final_readiness_decision": decision,
        "notes": [
            "Final manuscript handoff is restricted to the audited shell.",
            "Only the four closed theoremlets are manuscript-core claims.",
            "Support-only, reserve, and non-claim boundaries are frozen from the internal package.",
        ],
    }

    report = {
        "theoremlet_count": len(handoff["closed_theoremlets"]),
        "allowed_claim_count": len(handoff["allowed_claim_ids"]),
        "support_only_count": len(handoff["support_only_ids"]),
        "reserve_count": len(handoff["reserve_ids"]),
        "nonclaim_count": len(handoff["nonclaim_ids"]),
        "pdf_exists": final_pdf_path.exists(),
        "compile_status": handoff["compile_status"],
        "warning_summary": handoff["warning_summary"],
        "paper_core_positioning": theorem_package["paper_core_positioning"],
        "risk_audit_decision": publication_risk["decision"],
        "traceability_decision": traceability["decision"],
        "contribution_delta_decision": contribution_delta["decision"],
        "figure_binding_count": len(figure_manifest["allowed_claim_bindings"]),
        "final_handoff_decision": decision,
    }

    out_json = ROOT / "docs/internal/final_manuscript_handoff_v1.json"
    out_json.write_text(json.dumps(handoff, indent=2, sort_keys=True))

    results_dir = ROOT / "results/final_manuscript_handoff"
    results_dir.mkdir(parents=True, exist_ok=True)
    (results_dir / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True))

    csv_lines = [
        "metric,value",
        f"theoremlet_count,{report['theoremlet_count']}",
        f"allowed_claim_count,{report['allowed_claim_count']}",
        f"support_only_count,{report['support_only_count']}",
        f"reserve_count,{report['reserve_count']}",
        f"nonclaim_count,{report['nonclaim_count']}",
        f"pdf_exists,{str(report['pdf_exists']).lower()}",
        f"final_handoff_decision,{report['final_handoff_decision']}",
    ]
    (results_dir / "report.csv").write_text("\n".join(csv_lines) + "\n")


if __name__ == "__main__":
    main()
