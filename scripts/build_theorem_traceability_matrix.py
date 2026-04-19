#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any


THEOREMLET_SPECS = {
    "continuous_full_loop_lawfulness_theoremlet": {
        "dependency_path": "docs/internal/proof_dependency_continuous_full_loop_v1.json",
        "lemma_id": "CK-THM-7",
        "evidence_paths": [
            "docs/internal/continuous_full_loop_theorem_package_v1.md",
            "results/level3_theorem_package/report.json",
        ],
    },
    "cocycle_pressure_closure_theoremlet": {
        "dependency_path": "docs/internal/proof_dependency_continuous_pressure_v1.json",
        "lemma_id": "CP-THM-7",
        "evidence_paths": [
            "docs/internal/continuous_pressure_closure_v1.md",
            "results/continuous_pressure_closure/report.json",
        ],
    },
    "strict_theory_extension_theoremlet": {
        "dependency_path": "docs/internal/proof_dependency_strict_theory_extension_v1.json",
        "lemma_id": "ST-THM-7",
        "evidence_paths": [
            "docs/internal/strict_theory_extension_closure_v1.md",
            "results/strict_theory_extension_closure/report.json",
        ],
    },
    "conditional_pressure_disintegration_theoremlet": {
        "dependency_path": "docs/internal/proof_dependency_conditional_disintegration_v1.json",
        "lemma_id": "CDI-THM-7",
        "evidence_paths": [
            "docs/internal/conditional_pressure_disintegration_v1.md",
            "results/conditional_disintegration/report.json",
        ],
    },
}

SHELL_SPECIFIC_ASSUMPTIONS = {
    "parameter_shell_robustness",
    "lawful_exploratory_regime",
    "no_fast_collapse",
}


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
    prereqs = {
        "docs/internal/level3_theorem_package_v1.json": "scripts/build_level3_theorem_package.py",
        "docs/internal/final_paper_core_claim_ledger_v1.json": "scripts/build_level3_theorem_package.py",
        "docs/internal/figure_manifest_v1.json": "scripts/build_figure_manifest.py",
        "results/level3_theorem_package/report.json": "scripts/build_level3_theorem_package.py",
        "results/manuscript_package/report.json": "scripts/build_figure_manifest.py",
    }
    for path, script in prereqs.items():
        _ensure_file(repo_root, path, script)

    package = _load_json(repo_root / "docs/internal/level3_theorem_package_v1.json")
    ledger = _load_json(repo_root / "docs/internal/final_paper_core_claim_ledger_v1.json")
    manifest = _load_json(repo_root / "docs/internal/figure_manifest_v1.json")

    claim_map = {item["claim_id"]: item for item in ledger["claims"]}
    core_claim_ids = {
        item["claim_id"]
        for item in ledger["claims"]
        if item["claim_status"] == "closed_theoremlet"
    }
    support_claim_ids = {
        item["claim_id"]
        for item in ledger["claims"]
        if item["claim_status"] == "supporting_evidence"
    }
    reserve_claim_ids = {
        item["claim_id"]
        for item in ledger["claims"]
        if item["claim_status"] == "reserve"
    }
    nonclaim_ids = {
        item["claim_id"]
        for item in ledger["claims"]
        if item["claim_status"] == "nonclaim"
    }

    dependency_cache = {
        path: _load_json(repo_root / path) for path in package["dependency_paths"]
    }

    theoremlets = []
    assumption_usage: dict[str, set[str]] = defaultdict(set)
    dependency_index: dict[str, list[str]] = defaultdict(list)
    evidence_index: dict[str, dict[str, Any]] = {}
    claim_bindings = []
    missing_links = []
    firewall_violations = []

    allowed_bindings_by_claim: dict[str, list[str]] = defaultdict(list)
    for binding in manifest["allowed_claim_bindings"]:
        allowed_bindings_by_claim[binding["claim_id"]].append(binding["figure_id"])

    for item in package["included_theoremlets"]:
        theoremlet_id = item["theoremlet_id"]
        spec = THEOREMLET_SPECS[theoremlet_id]
        dep = dependency_cache[spec["dependency_path"]]
        lemma = _extract_lemma(dep, spec["lemma_id"])
        claim = claim_map.get(theoremlet_id)
        if claim is None:
            raise SystemExit(f"missing claim entry for theoremlet {theoremlet_id}")
        if claim["claim_status"] != "closed_theoremlet":
            raise SystemExit(f"theoremlet {theoremlet_id} not marked closed_theoremlet")

        assumptions_used = sorted(
            set(dep.get("assumptions_used", []))
            | set(lemma.get("assumptions_used", []))
        )
        if not assumptions_used:
            missing_links.append(f"{theoremlet_id}:no_assumptions")

        dependency_paths = sorted(
            set([spec["dependency_path"]]) | set(claim["dependency_paths"])
        )
        if not dependency_paths:
            missing_links.append(f"{theoremlet_id}:no_dependency_paths")

        evidence_paths = sorted(
            set(spec["evidence_paths"]) | set(claim["evidence_paths"])
        )
        if not evidence_paths:
            missing_links.append(f"{theoremlet_id}:no_evidence_paths")

        allowed_claim_ids = [theoremlet_id]
        forbidden_claim_ids = sorted(nonclaim_ids | reserve_claim_ids)

        for assumption_id in assumptions_used:
            assumption_usage[assumption_id].add(theoremlet_id)

        for dep_path in dependency_paths:
            dependency_index[dep_path].append(theoremlet_id)

        for evidence_path in evidence_paths:
            exists = (repo_root / evidence_path).exists()
            if not exists:
                missing_links.append(f"{theoremlet_id}:missing_evidence:{evidence_path}")
            artifact_role = "theorem_supporting"
            manuscript_safe = True
            if evidence_path.endswith("results/conditional_disintegration/report.json") and theoremlet_id != "conditional_pressure_disintegration_theoremlet":
                artifact_role = "diagnostic_only"
            if evidence_path.endswith("results/level3_theorem_package/report.json") or evidence_path.endswith("results/manuscript_package/report.json"):
                artifact_role = "diagnostic_only"
            evidence_entry = evidence_index.setdefault(
                evidence_path,
                {
                    "artifact_path": evidence_path,
                    "supports_theoremlets": [],
                    "artifact_role": artifact_role,
                    "manuscript_safe": manuscript_safe,
                },
            )
            evidence_entry["supports_theoremlets"].append(theoremlet_id)

        if any(claim_id in nonclaim_ids for claim_id in allowed_claim_ids):
            firewall_violations.append(f"{theoremlet_id}:allowed_nonclaim")
        if any(claim_id in reserve_claim_ids for claim_id in allowed_claim_ids):
            firewall_violations.append(f"{theoremlet_id}:allowed_reserve")

        theoremlets.append(
            {
                "theoremlet_id": theoremlet_id,
                "status": item["status"],
                "class_scope": item["class_scope"],
                "assumptions_used": assumptions_used,
                "dependency_paths": dependency_paths,
                "evidence_paths": evidence_paths,
                "allowed_claim_ids": allowed_claim_ids,
                "forbidden_claim_ids": forbidden_claim_ids,
                "witness_families": item["witness_families"],
                "note": item["note"],
            }
        )

        claim_bindings.append(
            {
                "theoremlet_id": theoremlet_id,
                "allowed_claim_ids": allowed_claim_ids,
                "forbidden_claim_ids": forbidden_claim_ids,
                "figure_ids": allowed_bindings_by_claim.get(theoremlet_id, []),
            }
        )

    assumption_index = []
    for assumption_id, theoremlet_ids in sorted(assumption_usage.items()):
        assumption_index.append(
            {
                "assumption_id": assumption_id,
                "theoremlets": sorted(theoremlet_ids),
                "relevance_category": "core",
                "scope_role": (
                    "shell_specific"
                    if assumption_id in SHELL_SPECIFIC_ASSUMPTIONS
                    else "generic_inside_current_class"
                ),
            }
        )

    dependency_index_list = [
        {"dependency_path": path, "theoremlets": sorted(ids)}
        for path, ids in sorted(dependency_index.items())
    ]
    evidence_index_list = [
        {
            **entry,
            "supports_theoremlets": sorted(set(entry["supports_theoremlets"])),
        }
        for _, entry in sorted(evidence_index.items())
    ]

    scope_firewall = {
        "core_closed_claims": sorted(core_claim_ids),
        "support_only_claims": sorted(support_claim_ids),
        "reserve_routes": sorted(reserve_claim_ids),
        "explicit_nonclaims": sorted(nonclaim_ids),
        "scope_boundaries": [
            "audited shell only",
            "no broader-class theorem",
            "no shell-general theorem",
            "no direct stratumwise root-separation theorem",
            "no external/non-SFT breadth claim beyond what is closed",
        ],
    }

    for binding in manifest["allowed_claim_bindings"]:
        claim_id = binding["claim_id"]
        if claim_id in nonclaim_ids:
            firewall_violations.append(f"manifest_allowed_nonclaim:{claim_id}")
        if claim_id in reserve_claim_ids:
            firewall_violations.append(f"manifest_allowed_reserve:{claim_id}")
        if claim_id not in core_claim_ids and claim_id not in support_claim_ids:
            firewall_violations.append(f"manifest_unknown_scope:{claim_id}")

    decision = "traceability_complete"
    if firewall_violations:
        decision = "traceability_not_yet_safe"
    elif missing_links:
        decision = "traceability_complete_with_minor_gaps"

    matrix = {
        "schema_version": "v1",
        "matrix_id": "theorem_traceability_matrix_v1",
        "generated_at_utc": "2026-03-19T00:00:00Z",
        "paper_core_positioning": package["paper_core_positioning"],
        "theoremlets": theoremlets,
        "assumption_index": assumption_index,
        "dependency_index": dependency_index_list,
        "evidence_index": evidence_index_list,
        "claim_bindings": claim_bindings,
        "scope_firewall": scope_firewall,
        "decision": decision,
        "notes": [
            "The matrix is formal and audit-oriented; it is not a manuscript outline.",
            "Core theoremlets may bind only to closed theoremlet claims; support-only and nonclaim entries are firewalled explicitly.",
        ],
    }

    out_matrix = repo_root / "docs/internal/theorem_traceability_matrix_v1.json"
    out_matrix.write_text(json.dumps(matrix, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    report = {
        "report_id": "theorem_traceability_v1",
        "schema_version": "v1",
        "generated_at_utc": "2026-03-19T00:00:00Z",
        "theoremlet_count": len(theoremlets),
        "assumption_coverage_count": len(assumption_index),
        "evidence_coverage_count": len(evidence_index_list),
        "firewall_violation_count": len(firewall_violations),
        "missing_link_summary": missing_links,
        "final_safety_decision": decision,
    }

    out_dir = repo_root / "results/theorem_traceability"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with (out_dir / "report.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["metric", "value"])
        writer.writerow(["theoremlet_count", len(theoremlets)])
        writer.writerow(["assumption_coverage_count", len(assumption_index)])
        writer.writerow(["evidence_coverage_count", len(evidence_index_list)])
        writer.writerow(["firewall_violation_count", len(firewall_violations)])
        writer.writerow(["missing_link_count", len(missing_links)])
        writer.writerow(["final_safety_decision", decision])

    if firewall_violations:
        raise SystemExit(f"firewall violations: {firewall_violations}")
    return 0


if __name__ == "__main__":
    raise SystemExit(build())
