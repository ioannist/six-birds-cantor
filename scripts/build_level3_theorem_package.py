#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path
from typing import Any


REQUIRED_THEOREMLETS = {
    "continuous_full_loop_lawfulness_theoremlet": {
        "dependency_path": "docs/internal/proof_dependency_continuous_full_loop_v1.json",
        "lemma_id": "CK-THM-7",
        "status": "closed_in_note",
        "class_scope": "continuous_full_loop_lawful_kernel_class_shell_stable",
        "witness_families": [
            "generated.continuous_full_loop_kernel",
            "generated.continuous_full_loop_kernel_shell",
        ],
        "note": "Closed six-primitive lawfulness regime theoremlet on the shell-stable audited package.",
    },
    "cocycle_pressure_closure_theoremlet": {
        "dependency_path": "docs/internal/proof_dependency_continuous_pressure_v1.json",
        "lemma_id": "CP-THM-7",
        "status": "closed_in_note",
        "class_scope": "continuous_full_loop_lawful_kernel_class_shell_stable",
        "witness_families": [
            "generated.continuous_full_loop_kernel",
            "generated.continuous_full_loop_kernel_shell",
        ],
        "note": "Closed switched-operator cocycle pressure theoremlet on the shell-stable class.",
    },
    "strict_theory_extension_theoremlet": {
        "dependency_path": "docs/internal/proof_dependency_strict_theory_extension_v1.json",
        "lemma_id": "ST-THM-7",
        "status": "closed_in_note",
        "class_scope": "continuous_full_loop_lawful_kernel_class_shell_stable",
        "witness_families": [
            "generated.continuous_full_loop_kernel",
            "generated.continuous_full_loop_kernel_shell",
        ],
        "note": "Closed strict theory extension theoremlet for T1 over T0 on the audited shell.",
    },
    "conditional_pressure_disintegration_theoremlet": {
        "dependency_path": "docs/internal/proof_dependency_conditional_disintegration_v1.json",
        "lemma_id": "CDI-THM-7",
        "status": "closed_in_note",
        "class_scope": "continuous_full_loop_lawful_kernel_class_shell_stable",
        "witness_families": [
            "generated.continuous_full_loop_kernel",
            "generated.continuous_full_loop_kernel_shell",
        ],
        "note": "Closed conditional pressure disintegration theoremlet on the canonical hybrid object over the audited shell.",
    },
}

NONCLAIMS = [
    "no broader-class theorem beyond the audited shell",
    "no external/non-SFT breadth claim beyond what is actually closed",
    "no direct stratumwise root-separation theorem",
    "no packaging-induced broader theorem class claim",
    "no shell-general theorem beyond the audited shell-stable class",
]

RESERVE_ROUTES = [
    "packaging-completion broader-class ambitions",
    "hybrid object broadening beyond audited shell",
    "wider parameter shell theorem",
    "non-SFT breadth story not already closed",
]


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _ensure_file(repo_root: Path, path: str, script: str) -> None:
    full = repo_root / path
    if full.exists():
        return
    subprocess.run(["python", script], cwd=repo_root, check=True)


def _extract_lemma(dependency: dict[str, Any], lemma_id: str) -> dict[str, Any]:
    for item in dependency["lemmas"]:
        if item["lemma_id"] == lemma_id:
            return item
    raise RuntimeError(f"missing lemma {lemma_id} in {dependency.get('dependency_id')}")


def build() -> int:
    repo_root = Path(__file__).resolve().parent.parent

    required_reports = {
        "results/continuous_pressure_closure/report.json": "scripts/run_continuous_pressure_closure_checks.py",
        "results/strict_theory_extension_closure/report.json": "scripts/run_strict_theory_extension_closure_checks.py",
        "results/conditional_disintegration/report.json": "scripts/run_conditional_disintegration_checks.py",
    }
    for path, script in required_reports.items():
        _ensure_file(repo_root, path, script)

    continuous_package = _load_json(repo_root / "docs/internal/continuous_full_loop_theorem_package_v1.json")
    canonical_object = _load_json(repo_root / "docs/internal/canonical_hybrid_theorem_object_v1.json")
    continuous_dep = _load_json(repo_root / "docs/internal/proof_dependency_continuous_full_loop_v1.json")
    pressure_dep = _load_json(repo_root / "docs/internal/proof_dependency_continuous_pressure_v1.json")
    extension_dep = _load_json(repo_root / "docs/internal/proof_dependency_strict_theory_extension_v1.json")
    disintegration_dep = _load_json(repo_root / "docs/internal/proof_dependency_conditional_disintegration_v1.json")

    dependency_map = {
        "docs/internal/proof_dependency_continuous_full_loop_v1.json": continuous_dep,
        "docs/internal/proof_dependency_continuous_pressure_v1.json": pressure_dep,
        "docs/internal/proof_dependency_strict_theory_extension_v1.json": extension_dep,
        "docs/internal/proof_dependency_conditional_disintegration_v1.json": disintegration_dep,
    }

    included_theoremlets = []
    missing = []
    for theoremlet_id, spec in REQUIRED_THEOREMLETS.items():
        dep = dependency_map[spec["dependency_path"]]
        lemma = _extract_lemma(dep, spec["lemma_id"])
        if lemma["status"] != spec["status"]:
            missing.append(f"{theoremlet_id}:{lemma['status']}")
        included_theoremlets.append(
            {
                "theoremlet_id": theoremlet_id,
                "status": lemma["status"],
                "class_scope": spec["class_scope"],
                "dependency_path": spec["dependency_path"],
                "witness_families": spec["witness_families"],
                "note": spec["note"],
            }
        )

    paper_core_positioning = (
        "level3_core_on_audited_shell"
        if not missing
        else "level2_with_level3_signal_only"
    )

    package = {
        "schema_version": "v1",
        "package_id": "level3_theorem_package_v1",
        "generated_at_utc": "2026-03-19T00:00:00Z",
        "core_class_id": "continuous_full_loop_lawful_kernel_class_shell_stable",
        "canonical_object_id": canonical_object["object_id"],
        "included_theoremlets": included_theoremlets,
        "selected_routes": {
            "lawfulness_route": continuous_dep["selected_route"],
            "pressure_route": pressure_dep["selected_pressure_route"],
            "extension_route": extension_dep["selected_extension_route"],
            "thermodynamic_consequence_route": "conditional_pressure_disintegration_route",
        },
        "witness_families": [
            "generated.continuous_full_loop_kernel",
            "generated.continuous_full_loop_kernel_shell",
        ],
        "assumption_paths": [
            "docs/internal/continuous_theorem_assumptions_v1.json",
        ],
        "dependency_paths": [
            "docs/internal/proof_dependency_continuous_full_loop_v1.json",
            "docs/internal/proof_dependency_continuous_pressure_v1.json",
            "docs/internal/proof_dependency_strict_theory_extension_v1.json",
            "docs/internal/proof_dependency_conditional_disintegration_v1.json",
        ],
        "evidence_paths": [
            "results/continuous_pressure_closure/report.json",
            "results/strict_theory_extension_closure/report.json",
            "results/conditional_disintegration/report.json",
        ],
        "paper_core_positioning": paper_core_positioning,
        "reserve_routes": RESERVE_ROUTES,
        "nonclaims": NONCLAIMS,
        "notes": [
            "The package is frozen around the audited-shell Level-3 core only.",
            "The conditional disintegration theoremlet is the thermodynamic consequence route retained in the paper-core package.",
        ],
    }

    claims = []
    evidence_paths = package["evidence_paths"]
    for theoremlet in included_theoremlets:
        claim_type = {
            "continuous_full_loop_lawfulness_theoremlet": "lawfulness",
            "cocycle_pressure_closure_theoremlet": "pressure",
            "strict_theory_extension_theoremlet": "strict_extension",
            "conditional_pressure_disintegration_theoremlet": "thermodynamic_consequence",
        }[theoremlet["theoremlet_id"]]
        claims.append(
            {
                "claim_id": theoremlet["theoremlet_id"],
                "claim_status": "closed_theoremlet",
                "claim_type": claim_type,
                "statement_short": theoremlet["note"],
                "object_scope": canonical_object["object_id"] if claim_type in {"strict_extension", "thermodynamic_consequence"} else continuous_package["package_id"],
                "class_scope": theoremlet["class_scope"],
                "witness_families": theoremlet["witness_families"],
                "dependency_paths": [theoremlet["dependency_path"]],
                "evidence_paths": evidence_paths,
                "allowed_final_paper_use": "core_claim",
                "note": "Closed theoremlet included in the frozen Level-3 core package.",
            }
        )

    claims.extend(
        [
            {
                "claim_id": "closure_deficit_proxy_support",
                "claim_status": "supporting_evidence",
                "claim_type": "thermodynamic_consequence",
                "statement_short": "KL-style closure-deficit proxies support the conditional disintegration interpretation but are not themselves the closed theorem object.",
                "object_scope": canonical_object["object_id"],
                "class_scope": "continuous_full_loop_lawful_kernel_class_shell_stable",
                "witness_families": package["witness_families"],
                "dependency_paths": ["docs/internal/proof_dependency_conditional_disintegration_v1.json"],
                "evidence_paths": ["results/conditional_disintegration/report.json"],
                "allowed_final_paper_use": "support_only",
                "note": "Support-only diagnostic; not a closed KL theorem.",
            }
        ]
    )

    for item in RESERVE_ROUTES:
        claim_type = "stretch_route" if "ambitions" not in item and "story" not in item else "future_work"
        claims.append(
            {
                "claim_id": item.replace(" ", "_"),
                "claim_status": "reserve",
                "claim_type": claim_type,
                "statement_short": item,
                "object_scope": canonical_object["object_id"],
                "class_scope": "outside_audited_shell_core",
                "witness_families": package["witness_families"],
                "dependency_paths": [],
                "evidence_paths": [],
                "allowed_final_paper_use": "reserve_only",
                "note": "Marked explicitly as reserve/stretch, not paper-core.",
            }
        )

    nonclaim_type_map = {
        NONCLAIMS[0]: "broader_class",
        NONCLAIMS[1]: "non_sft_scope",
        NONCLAIMS[2]: "thermodynamic_consequence",
        NONCLAIMS[3]: "broader_class",
        NONCLAIMS[4]: "future_work",
    }
    for item in NONCLAIMS:
        claims.append(
            {
                "claim_id": item.replace(" ", "_"),
                "claim_status": "nonclaim",
                "claim_type": nonclaim_type_map[item],
                "statement_short": item,
                "object_scope": canonical_object["object_id"],
                "class_scope": "outside_audited_shell_core",
                "witness_families": package["witness_families"],
                "dependency_paths": [],
                "evidence_paths": [],
                "allowed_final_paper_use": "nonclaim_only",
                "note": "Explicit anti-overclaim guardrail.",
            }
        )

    claim_counts = {
        "closed_theoremlet": sum(item["claim_status"] == "closed_theoremlet" for item in claims),
        "supporting_evidence": sum(item["claim_status"] == "supporting_evidence" for item in claims),
        "reserve": sum(item["claim_status"] == "reserve" for item in claims),
        "nonclaim": sum(item["claim_status"] == "nonclaim" for item in claims),
    }

    ledger = {
        "schema_version": "v1",
        "ledger_id": "final_paper_core_claim_ledger_v1",
        "generated_at_utc": "2026-03-19T00:00:00Z",
        "claims": claims,
        "claim_counts": claim_counts,
        "notes": [
            "The claim ledger is the anti-drift control for the final paper-core package.",
            "Only closed theoremlets are available for core theorem claims.",
        ],
    }

    package_path = repo_root / "docs/internal/level3_theorem_package_v1.json"
    ledger_path = repo_root / "docs/internal/final_paper_core_claim_ledger_v1.json"
    package_path.write_text(json.dumps(package, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    ledger_path.write_text(json.dumps(ledger, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    report = {
        "report_id": "level3_theorem_package_v1",
        "schema_version": "v1",
        "generated_at_utc": "2026-03-19T00:00:00Z",
        "final_positioning_decision": paper_core_positioning,
        "package_completeness_summary": {
            "required_theoremlets_present": len(included_theoremlets),
            "missing_or_inconsistent_theoremlets": missing,
            "canonical_object_closed": canonical_object["decision"] == "canonical_object_and_intrinsic_extension_closed",
        },
        "theoremlet_counts": {
            "closed_in_note": sum(item["status"] == "closed_in_note" for item in included_theoremlets),
            "support_only": sum(item["status"] == "support_only" for item in included_theoremlets),
        },
        "nonclaim_counts": {
            "required_nonclaims": len(NONCLAIMS),
            "present_nonclaims": len(NONCLAIMS),
        },
        "reserve_counts": {
            "reserve_items": len(RESERVE_ROUTES),
        },
        "missing_artifact_summary": {
            "missing_paths": missing,
        },
    }

    out_dir = repo_root / "results/level3_theorem_package"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with (out_dir / "report.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["metric", "value"])
        writer.writerow(["final_positioning_decision", paper_core_positioning])
        writer.writerow(["closed_theoremlets", report["theoremlet_counts"]["closed_in_note"]])
        writer.writerow(["support_only_theoremlets", report["theoremlet_counts"]["support_only"]])
        writer.writerow(["nonclaims", len(NONCLAIMS)])
        writer.writerow(["reserve_items", len(RESERVE_ROUTES)])

    if missing:
        raise SystemExit(f"missing or inconsistent theoremlets: {missing}")
    return 0


if __name__ == "__main__":
    raise SystemExit(build())
