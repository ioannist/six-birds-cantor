#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path
from typing import Any


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _ensure_file(repo_root: Path, path: str, script: str) -> None:
    full = repo_root / path
    if full.exists():
        return
    subprocess.run(["python", script], cwd=repo_root, check=True)


def build() -> int:
    repo_root = Path(__file__).resolve().parent.parent

    prereqs = {
        "docs/internal/level3_theorem_package_v1.json": "scripts/build_level3_theorem_package.py",
        "docs/internal/final_paper_core_claim_ledger_v1.json": "scripts/build_level3_theorem_package.py",
        "results/level3_theorem_package/report.json": "scripts/build_level3_theorem_package.py",
    }
    for path, script in prereqs.items():
        _ensure_file(repo_root, path, script)

    package = _load_json(repo_root / "docs/internal/level3_theorem_package_v1.json")
    ledger = _load_json(repo_root / "docs/internal/final_paper_core_claim_ledger_v1.json")

    claims = {item["claim_id"]: item for item in ledger["claims"]}
    core_claim_ids = [
        "continuous_full_loop_lawfulness_theoremlet",
        "cocycle_pressure_closure_theoremlet",
        "strict_theory_extension_theoremlet",
        "conditional_pressure_disintegration_theoremlet",
    ]
    support_claim_ids = ["closure_deficit_proxy_support"]
    nonclaim_ids = [item["claim_id"] for item in ledger["claims"] if item["claim_status"] == "nonclaim"]

    figures = [
        {
            "figure_id": "fig_full_loop_continuous_substrate_regime",
            "title_short": "Continuous Substrate Regime",
            "role": "core_figure",
            "supports_theoremlets": ["continuous_full_loop_lawfulness_theoremlet"],
            "allowed_claim_ids": ["continuous_full_loop_lawfulness_theoremlet"],
            "source_artifacts": [
                "docs/internal/continuous_full_loop_theorem_package_v1.md",
                "docs/internal/proof_dependency_continuous_full_loop_v1.json",
                "results/level3_theorem_package/report.json",
            ],
            "status": "ready",
            "note": "Manuscript-facing regime figure for the shell-stable six-primitive lawful object.",
        },
        {
            "figure_id": "fig_primitive_knockout_closure",
            "title_short": "Primitive Closure Evidence",
            "role": "core_figure",
            "supports_theoremlets": ["continuous_full_loop_lawfulness_theoremlet"],
            "allowed_claim_ids": ["continuous_full_loop_lawfulness_theoremlet"],
            "source_artifacts": [
                "docs/internal/proof_dependency_continuous_full_loop_v1.json",
                "docs/internal/level3_theorem_package_v1.md",
            ],
            "status": "ready",
            "note": "Closure/necessity figure for six-primitive activity within the lawfulness theoremlet.",
        },
        {
            "figure_id": "fig_stratumwise_root_separation_diagnostic",
            "title_short": "Rejected Stratumwise Route",
            "role": "reserve_figure",
            "supports_theoremlets": [],
            "allowed_claim_ids": [],
            "source_artifacts": [
                "docs/internal/stratumwise_thermodynamic_distinction_v1.md",
                "results/stratumwise_distinction/report.json",
            ],
            "status": "reserve",
            "note": "Reserve-only diagnostic showing why direct stratumwise separation must not be used for core claims.",
        },
    ]

    tables = [
        {
            "figure_id": "tbl_pressure_closure_support",
            "title_short": "Pressure Closure Support",
            "role": "core_table",
            "supports_theoremlets": ["cocycle_pressure_closure_theoremlet"],
            "allowed_claim_ids": ["cocycle_pressure_closure_theoremlet"],
            "source_artifacts": [
                "docs/internal/continuous_pressure_closure_v1.md",
                "docs/internal/proof_dependency_continuous_pressure_v1.json",
                "results/continuous_pressure_closure/report.json",
            ],
            "status": "ready",
            "note": "Pressure-closure support table for the closed cocycle theoremlet.",
        },
        {
            "figure_id": "tbl_strict_theory_extension",
            "title_short": "Strict Extension Summary",
            "role": "core_table",
            "supports_theoremlets": ["strict_theory_extension_theoremlet"],
            "allowed_claim_ids": ["strict_theory_extension_theoremlet"],
            "source_artifacts": [
                "docs/internal/strict_theory_extension_closure_v1.md",
                "docs/internal/proof_dependency_strict_theory_extension_v1.json",
                "results/strict_theory_extension_closure/report.json",
            ],
            "status": "ready",
            "note": "Table covering saturation, forcing, non-definability, and macro-admissibility obstruction.",
        },
        {
            "figure_id": "tbl_conditional_disintegration",
            "title_short": "Conditional Disintegration",
            "role": "core_table",
            "supports_theoremlets": ["conditional_pressure_disintegration_theoremlet"],
            "allowed_claim_ids": ["conditional_pressure_disintegration_theoremlet"],
            "source_artifacts": [
                "docs/internal/conditional_pressure_disintegration_v1.md",
                "docs/internal/proof_dependency_conditional_disintegration_v1.json",
                "results/conditional_disintegration/report.json",
            ],
            "status": "ready",
            "note": "Table for the weighted package-conditioned pressure gap on the canonical hybrid object.",
        },
        {
            "figure_id": "tbl_closure_deficit_proxy_diagnostic",
            "title_short": "Closure-Deficit Proxy",
            "role": "support_table",
            "supports_theoremlets": ["conditional_pressure_disintegration_theoremlet"],
            "allowed_claim_ids": ["closure_deficit_proxy_support"],
            "source_artifacts": [
                "results/conditional_disintegration/report.json",
                "docs/internal/conditional_pressure_disintegration_v1.md",
            ],
            "status": "ready",
            "note": "Support-only table; may illustrate the interpretation but not serve as a closed KL theorem claim.",
        },
    ]

    allowed_claim_bindings = []
    mismatch_warnings = []
    for entry in figures + tables:
        for claim_id in entry["allowed_claim_ids"]:
            claim = claims.get(claim_id)
            if claim is None:
                mismatch_warnings.append(f"{entry['figure_id']} references missing claim {claim_id}")
                continue
            if claim["claim_status"] == "nonclaim":
                raise SystemExit(f"{entry['figure_id']} cannot bind nonclaim {claim_id}")
            if claim["claim_status"] == "reserve":
                raise SystemExit(f"{entry['figure_id']} cannot bind reserve claim {claim_id}")
            allowed_claim_bindings.append(
                {
                    "figure_id": entry["figure_id"],
                    "claim_id": claim_id,
                    "claim_status": claim["claim_status"],
                    "allowed_final_paper_use": claim["allowed_final_paper_use"],
                }
            )

    nonclaim_bindings = [
        {
            "figure_id": "fig_stratumwise_root_separation_diagnostic",
            "protected_nonclaim_id": "no_direct_stratumwise_root-separation_theorem",
            "binding_type": "reserve_only",
            "note": "This diagnostic may illustrate the rejected route internally but must not support a core claim.",
        },
        {
            "figure_id": "tbl_closure_deficit_proxy_diagnostic",
            "protected_nonclaim_id": "no_external/non-SFT_breadth_claim_beyond_what_is_actually_closed",
            "binding_type": "support_only_guardrail",
            "note": "The proxy table may support interpretation only; it must not be used as a broader external claim.",
        },
        {
            "figure_id": "fig_full_loop_continuous_substrate_regime",
            "protected_nonclaim_id": "no_shell-general_theorem_beyond_the_audited_shell-stable_class",
            "binding_type": "scope_guardrail",
            "note": "The regime figure is manuscript-safe only for the audited shell.",
        },
    ]

    manifest = {
        "schema_version": "v1",
        "manifest_id": "figure_manifest_v1",
        "generated_at_utc": "2026-03-19T00:00:00Z",
        "paper_core_positioning": package["paper_core_positioning"],
        "figures": figures,
        "tables": tables,
        "allowed_claim_bindings": allowed_claim_bindings,
        "nonclaim_bindings": nonclaim_bindings,
        "notes": [
            "The manifest is manuscript-facing and bound to the frozen Level-3 package only.",
            "Core figures/tables may bind only to closed theoremlets or support-only claims allowed by the ledger.",
        ],
    }

    missing_paths = []
    for entry in figures + tables:
        for artifact in entry["source_artifacts"]:
            if not (repo_root / artifact).exists():
                missing_paths.append(artifact)
                if entry["status"] == "ready":
                    entry["status"] = "needs_regeneration"

    out_manifest = repo_root / "docs/internal/figure_manifest_v1.json"
    out_manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    report = {
        "report_id": "manuscript_package_v1",
        "schema_version": "v1",
        "generated_at_utc": "2026-03-19T00:00:00Z",
        "paper_core_positioning": package["paper_core_positioning"],
        "theoremlet_count": len(core_claim_ids),
        "figure_count": len(figures),
        "table_count": len(tables),
        "allowed_claim_binding_count": len(allowed_claim_bindings),
        "nonclaim_binding_count": len(nonclaim_bindings),
        "missing_artifact_summary": {
            "missing_paths": missing_paths,
        },
        "claim_figure_mismatch_warnings": mismatch_warnings,
    }

    out_dir = repo_root / "results/manuscript_package"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with (out_dir / "report.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["metric", "value"])
        writer.writerow(["paper_core_positioning", package["paper_core_positioning"]])
        writer.writerow(["theoremlet_count", len(core_claim_ids)])
        writer.writerow(["figure_count", len(figures)])
        writer.writerow(["table_count", len(tables)])
        writer.writerow(["allowed_claim_binding_count", len(allowed_claim_bindings)])
        writer.writerow(["nonclaim_binding_count", len(nonclaim_bindings)])
        writer.writerow(["missing_artifact_count", len(missing_paths)])

    return 0


if __name__ == "__main__":
    raise SystemExit(build())
