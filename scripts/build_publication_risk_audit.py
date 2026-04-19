#!/usr/bin/env python3
"""Build the Level-3 contribution delta map and publication-risk audit."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs" / "internal"
RESULTS = ROOT / "results" / "publication_risk_audit"

LEVEL3_PACKAGE_PATH = DOCS / "level3_theorem_package_v1.json"
CLAIM_LEDGER_PATH = DOCS / "final_paper_core_claim_ledger_v1.json"
TRACEABILITY_PATH = DOCS / "theorem_traceability_matrix_v1.json"
MANUSCRIPT_SUMMARY_PATH = DOCS / "manuscript_theorem_summary_v1.md"

DELTA_JSON_PATH = DOCS / "contribution_delta_map_v1.json"
RISK_JSON_PATH = DOCS / "publication_risk_audit_v1.json"
REPORT_JSON_PATH = RESULTS / "report.json"
REPORT_CSV_PATH = RESULTS / "report.csv"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def ensure_prereqs() -> None:
    prereqs = [
        (LEVEL3_PACKAGE_PATH, ROOT / "scripts" / "build_level3_theorem_package.py"),
        (TRACEABILITY_PATH, ROOT / "scripts" / "build_theorem_traceability_matrix.py"),
    ]
    for artifact, builder in prereqs:
        if artifact.exists():
            continue
        if not builder.exists():
            raise FileNotFoundError(f"Missing prerequisite artifact {artifact} and builder {builder}")
        subprocess.run([sys.executable, str(builder)], cwd=ROOT, check=True)


def timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def contribution(
    contribution_id: str,
    label: str,
    type_: str,
    novelty_status: str,
    baseline_refs: list[str],
    repo_evidence_paths: list[str],
    scope: str,
    note: str,
) -> dict:
    return {
        "contribution_id": contribution_id,
        "label": label,
        "type": type_,
        "novelty_status": novelty_status,
        "baseline_refs": baseline_refs,
        "repo_evidence_paths": repo_evidence_paths,
        "scope": scope,
        "note": note,
    }


def risk(
    risk_id: str,
    label: str,
    severity: str,
    type_: str,
    applies_to: list[str],
    mitigation: str,
    note: str,
) -> dict:
    return {
        "risk_id": risk_id,
        "label": label,
        "severity": severity,
        "type": type_,
        "applies_to": applies_to,
        "mitigation": mitigation,
        "note": note,
    }


def main() -> int:
    ensure_prereqs()
    RESULTS.mkdir(parents=True, exist_ok=True)

    level3 = load_json(LEVEL3_PACKAGE_PATH)
    ledger = load_json(CLAIM_LEDGER_PATH)
    traceability = load_json(TRACEABILITY_PATH)

    claim_by_id = {claim["claim_id"]: claim for claim in ledger["claims"]}
    nonclaim_ids = {
        claim["claim_id"]
        for claim in ledger["claims"]
        if claim["claim_status"] == "nonclaim"
    }

    baseline_candidates = {
        "vendor_pica_readme": "vendors/six-birds-pica/README.md",
        "vendor_pica_primitives": "vendors/six-birds-pica/theory/primitives.md",
        "vendor_pica_paper_workspace": "vendors/six-birds-pica/paper/README.md",
        "delayed_return_package": "docs/internal/delayed_return_theorem_package_v1.md",
        "bounded_overlap_branch": "docs/internal/bounded_overlap_class_v1.json",
        "induced_core_branch": "docs/internal/induced_core_class_v1.json",
        "quasimultiplicative_branch": "docs/internal/quasimultiplicative_class_v1.json",
        "attached_six_birds_papers_dir": "docs/papers",
    }
    missing_baselines = [
        path for path in baseline_candidates.values() if not (ROOT / path).exists()
    ]

    contributions = [
        contribution(
            "primitive_semantics_six_birds",
            "Primitive semantics and P1-P6 definitions",
            "object",
            "inherited",
            [
                "vendors/six-birds-pica/theory/primitives.md",
            ],
            [
                "docs/internal/continuous_full_loop_theorem_package_v1.md",
            ],
            "all audited-shell theoremlets",
            "The branch inherits the six-birds primitive semantics and the packaging-endomap viewpoint rather than inventing them.",
        ),
        contribution(
            "continuous_six_primitive_substrate_reset",
            "Continuous six-primitive substrate reset",
            "substrate_mechanism",
            "adapted",
            [
                "vendors/six-birds-pica/README.md",
                "vendors/six-birds-pica/theory/primitives.md",
                "docs/internal/delayed_return_theorem_package_v1.md",
            ],
            [
                "docs/internal/continuous_full_loop_theorem_package_v1.md",
                "docs/internal/proof_dependency_continuous_full_loop_v1.json",
            ],
            "audited shell-stable continuous class",
            "This branch adapts the vendor finite stochastic substrate ideas into the continuous full-loop kernel setting instead of reusing the earlier discrete or delayed-return packages.",
        ),
        contribution(
            "continuous_full_loop_lawfulness_theoremlet",
            "Continuous full-loop lawful kernel theoremlet",
            "theoremlet",
            "new_in_branch",
            [
                "docs/internal/delayed_return_theorem_package_v1.md",
                "docs/internal/bounded_overlap_class_v1.json",
            ],
            [
                "docs/internal/continuous_full_loop_theorem_package_v1.md",
                "docs/internal/proof_dependency_continuous_full_loop_v1.json",
            ],
            "continuous_full_loop_lawful_kernel_class_shell_stable",
            "This is the first closed continuous six-primitive lawfulness theoremlet in this repo branch.",
        ),
        contribution(
            "cocycle_pressure_closure_theoremlet",
            "Cocycle pressure closure theoremlet",
            "theoremlet",
            "new_in_branch",
            [
                "docs/internal/delayed_return_theorem_package_v1.md",
                "docs/internal/quasimultiplicative_class_v1.json",
            ],
            [
                "docs/internal/continuous_pressure_closure_v1.md",
                "docs/internal/proof_dependency_continuous_pressure_v1.json",
                "results/continuous_pressure_closure/report.json",
            ],
            "continuous_full_loop_lawful_kernel_class_shell_stable",
            "The closed cocycle-pressure route is new in this continuous audited-shell branch and is not inherited from the earlier induced/delayed branches.",
        ),
        contribution(
            "packaging_completion_endomap_as_object_generator",
            "Packaging completion endomap as theorem-object generator",
            "object",
            "adapted",
            [
                "vendors/six-birds-pica/theory/primitives.md",
            ],
            [
                "docs/internal/packaging_completion_endomap_v1.md",
                "src/contextual_cantor/continuous_kernel_substrate.py",
            ],
            "canonical hybrid object construction",
            "The endomap/fixed-point object idea is inherited from six-birds theory, but its continuous full-loop implementation and audit are adapted here.",
        ),
        contribution(
            "canonical_hybrid_object",
            "Canonical hybrid object",
            "object",
            "new_relative_to_prior_six_birds",
            [
                "vendors/six-birds-pica/theory/primitives.md",
                "vendors/six-birds-pica/README.md",
            ],
            [
                "docs/internal/canonical_hybrid_theorem_object_v1.md",
                "docs/internal/canonical_hybrid_theorem_object_v1.json",
                "results/canonical_hybrid_extension/report.json",
            ],
            "audited shell-stable continuous class",
            "The branch packages cocycle pressure, completion, saturation, forcing, and packaged strata into one intrinsic theorem object rather than leaving them as separate diagnostics.",
        ),
        contribution(
            "strict_theory_extension_theoremlet",
            "Strict theory extension theoremlet",
            "theoremlet",
            "new_relative_to_prior_six_birds",
            [
                "vendors/six-birds-pica/theory/primitives.md",
                "docs/internal/delayed_return_theorem_package_v1.md",
            ],
            [
                "docs/internal/strict_theory_extension_closure_v1.md",
                "docs/internal/proof_dependency_strict_theory_extension_v1.json",
                "results/strict_theory_extension_closure/report.json",
            ],
            "continuous_full_loop_lawful_kernel_class_shell_stable",
            "The abstract six-birds strict-extension idea is closed here as an audited-shell theoremlet on the canonical hybrid object.",
        ),
        contribution(
            "conditional_pressure_disintegration_theoremlet",
            "Conditional pressure disintegration theoremlet",
            "thermodynamic_consequence",
            "new_relative_to_prior_six_birds",
            [
                "vendors/six-birds-pica/theory/primitives.md",
                "vendors/six-birds-pica/README.md",
            ],
            [
                "docs/internal/conditional_pressure_disintegration_v1.md",
                "docs/internal/proof_dependency_conditional_disintegration_v1.json",
                "results/conditional_disintegration/report.json",
            ],
            "continuous_full_loop_lawful_kernel_class_shell_stable",
            "The branch closes a paper-native conditional disintegration consequence on the canonical hybrid object rather than on a raw trajectory or per-stratum root split.",
        ),
        contribution(
            "audited_shell_scope_restriction",
            "Audited-shell scope restriction",
            "audit_certificate",
            "new_in_branch",
            [
                "docs/internal/delayed_return_theorem_package_v1.md",
            ],
            [
                "docs/internal/level3_theorem_package_v1.md",
                "docs/internal/theorem_traceability_matrix_v1.json",
                "docs/internal/final_paper_core_claim_ledger_v1.json",
            ],
            "paper-core positioning",
            "The branch converts scope discipline into a first-class package artifact instead of leaving shell limits implicit.",
        ),
        contribution(
            "rejected_broader_class_claim",
            "Rejected broader-class claim",
            "audit_certificate",
            "new_in_branch",
            [
                "docs/internal/bounded_overlap_class_v1.json",
                "docs/internal/induced_core_class_v1.json",
            ],
            [
                "docs/internal/final_paper_core_claim_ledger_v1.json",
                "docs/internal/level3_theorem_package_v1.json",
            ],
            "paper-core positioning",
            "The branch explicitly records broader-class ambitions as reserve-only and prevents them from leaking into the core package.",
        ),
        contribution(
            "rejected_direct_stratumwise_separation_route",
            "Rejected direct stratumwise separation route",
            "audit_certificate",
            "new_in_branch",
            [
                "vendors/six-birds-pica/theory/primitives.md",
            ],
            [
                "docs/internal/stratumwise_thermodynamic_distinction_v1.md",
                "docs/internal/final_paper_core_claim_ledger_v1.json",
            ],
            "thermodynamic consequence route selection",
            "The branch turns the failed stratumwise route into an explicit non-claim and pivots to the paper-native conditional route.",
        ),
        contribution(
            "supporting_infrastructure_audit_chain",
            "Traceability, claim-ledger, and manuscript-firewall infrastructure",
            "supporting_infrastructure",
            "new_in_branch",
            [
                "vendors/six-birds-pica/README.md",
            ],
            [
                "docs/internal/level3_theorem_package_v1.json",
                "docs/internal/final_paper_core_claim_ledger_v1.json",
                "docs/internal/theorem_traceability_matrix_v1.json",
                "docs/internal/figure_manifest_v1.json",
            ],
            "publication-readiness controls",
            "The branch builds publication-facing package controls that the earlier theorem branches and vendor substrate do not provide in this form.",
        ),
    ]

    noncontributions = [
        {
            "label": "Primitive semantics origination",
            "reason": "Inherited from six-birds theory documents rather than created in this branch.",
        },
        {
            "label": "Vendor PICA finite stochastic substrate invention",
            "reason": "The vendor machinery is treated as baseline substrate/input, not as a new branch contribution.",
        },
        {
            "label": "Broader-class theorem beyond the audited shell",
            "reason": "Explicit non-claim in the frozen package.",
        },
        {
            "label": "Direct stratumwise root-separation theorem",
            "reason": "Explicitly rejected and not part of the core contribution set.",
        },
        {
            "label": "External/non-SFT breadth theorem",
            "reason": "Explicit non-claim in the frozen package.",
        },
    ]

    for item in contributions:
        if item["contribution_id"] in nonclaim_ids:
            raise ValueError(f"Non-claim {item['contribution_id']} cannot be classified as a contribution")
        missing_evidence = [
            path for path in item["repo_evidence_paths"] if not (ROOT / path).exists()
        ]
        if missing_evidence:
            raise FileNotFoundError(
                f"Contribution {item['contribution_id']} lacks evidence paths: {missing_evidence}"
            )

    required_contribution_ids = {
        "continuous_full_loop_lawfulness_theoremlet",
        "cocycle_pressure_closure_theoremlet",
        "strict_theory_extension_theoremlet",
        "conditional_pressure_disintegration_theoremlet",
        "canonical_hybrid_object",
        "continuous_six_primitive_substrate_reset",
        "packaging_completion_endomap_as_object_generator",
        "audited_shell_scope_restriction",
        "rejected_broader_class_claim",
        "rejected_direct_stratumwise_separation_route",
    }
    found_contribution_ids = {item["contribution_id"] for item in contributions}
    missing_required_contributions = sorted(required_contribution_ids - found_contribution_ids)
    if missing_required_contributions:
        raise ValueError(f"Missing required contribution items: {missing_required_contributions}")

    delta_decision = "delta_map_complete"
    contribution_delta = {
        "schema_version": "v1",
        "delta_id": "contribution_delta_map_v1",
        "generated_at_utc": timestamp(),
        "comparison_baselines": baseline_candidates,
        "contributions": contributions,
        "noncontributions": noncontributions,
        "decision": delta_decision,
        "notes": [
            "The delta map is conservative: primitive semantics are inherited, continuous substrate mechanics are adapted, and theorem closure is counted as new only where the branch actually closes it.",
            "The external docs/papers baseline directory is absent from this snapshot, so prior-paper comparison is limited to the vendor six-birds PICA materials and in-repo theorem branches.",
        ],
    }

    strengths = [
        {
            "label": "Four closed theoremlets on one audited-shell package",
            "note": "Lawfulness, cocycle pressure closure, strict theory extension, and conditional disintegration are all frozen in one package.",
        },
        {
            "label": "Canonical hybrid object is explicit",
            "note": "The branch no longer relies on an unstable object definition; the hybrid object is intrinsic and factorization-based.",
        },
        {
            "label": "Scope firewall is already frozen",
            "note": "Traceability and claim-ledger artifacts make overclaiming materially harder.",
        },
        {
            "label": "Paper-native thermodynamic consequence route closed",
            "note": "Conditional disintegration replaced the conceptually wrong direct stratumwise route.",
        },
    ]

    risks = [
        risk(
            "audited_shell_scope_only",
            "Audited-shell-only scope",
            "high",
            "shell_specificity",
            ["all core theoremlets"],
            "State the class as audited-shell only everywhere and block any shell-general phrasing.",
            "The package is strong on the audited shell but intentionally does not generalize to broader shells.",
        ),
        risk(
            "no_broader_class_theorem",
            "No broader-class theorem",
            "medium",
            "scope",
            ["strict_theory_extension_theoremlet", "conditional_pressure_disintegration_theoremlet"],
            "Keep broader-class ambitions in reserve-only language and do not market the result as a class-expansion theorem.",
            "Reviewer resistance will rise if the paper implies family breadth rather than audited-shell closure.",
        ),
        risk(
            "no_external_non_sft_breadth",
            "No external/non-SFT breadth claim",
            "medium",
            "non_sft_breadth_absence",
            ["paper-core positioning"],
            "Avoid universality rhetoric and keep non-SFT comparisons out of the core claim set.",
            "The package is six-birds-native and continuous, but not an external breadth theorem.",
        ),
        risk(
            "canonical_object_complexity",
            "Canonical hybrid object complexity",
            "medium",
            "object_complexity",
            ["canonical_hybrid_object"],
            "Use the frozen theorem summary and traceability matrix to keep the object definition tight and repeatable.",
            "A serious reviewer may find the hybrid object technically dense even if the internal package is coherent.",
        ),
        risk(
            "continuous_kernel_reset_dependence",
            "Dependence on the continuous-kernel reset rather than older discrete families",
            "medium",
            "simulation_dependence",
            ["continuous_full_loop_lawfulness_theoremlet", "cocycle_pressure_closure_theoremlet"],
            "Frame the reset as a deliberate branch reset and distinguish it cleanly from the earlier delayed/finite families.",
            "Some readers may prefer the older discrete baselines and treat the reset as a change of arena rather than a theorem advance.",
        ),
        risk(
            "pica_novelty_overlap",
            "Possible reviewer read of the result as adapted from PICA",
            "medium",
            "novelty_overlap",
            ["continuous_six_primitive_substrate_reset", "canonical_hybrid_object"],
            "Separate inherited substrate semantics from the new theoremlets and canonical hybrid closure in every internal summary.",
            "The vendor repo supplies substrate machinery and primitive semantics, so novelty has to be argued at the theorem-package level.",
        ),
        risk(
            "strict_extension_shell_specificity",
            "Strict extension theoremlet may look too shell-specific",
            "high",
            "shell_specificity",
            ["strict_theory_extension_theoremlet"],
            "Keep the claim on the audited shell and present the shell restriction as part of the theorem object rather than as a hidden weakness.",
            "The theoremlet is real, but a reviewer could still question how much of it survives outside the audited shell.",
        ),
        risk(
            "thermodynamic_consequence_proxy_reading",
            "Conditional disintegration may be read as too proxy-based if overstated",
            "high",
            "proof_presentation",
            ["conditional_pressure_disintegration_theoremlet"],
            "Claim the weighted package-conditioned pressure gap theoremlet only; mention KL-style closure-deficit proxies as support-only.",
            "Overstating the KL or exact information-theoretic layer would create avoidable reviewer pushback.",
        ),
        risk(
            "reviewer_confusion_about_negative_results",
            "Rejected routes may confuse reviewers about what is actually claimed",
            "medium",
            "reviewer_confusion",
            ["conditional_pressure_disintegration_theoremlet"],
            "Keep the rejected broader-class and stratumwise routes explicit as non-claims, not as partial claims.",
            "The branch contains several honest negative results that need to be framed as scope discipline rather than failed core claims.",
        ),
    ]

    for entry in risks:
        if entry["severity"] not in {"low", "medium", "high"}:
            raise ValueError(f"Risk {entry['risk_id']} has invalid severity")
        if not entry["type"]:
            raise ValueError(f"Risk {entry['risk_id']} is missing a type")

    objection_map = [
        {
            "objection_id": "obj_scope_shell_only",
            "targets": ["audited_shell_scope_only", "strict_extension_shell_specificity"],
            "objection": "The theorem package is only on a narrow audited shell.",
            "response": "That scope is explicit, frozen, and traceable; the package does not claim more than it closes.",
        },
        {
            "objection_id": "obj_pica_overlap",
            "targets": ["pica_novelty_overlap", "continuous_kernel_reset_dependence"],
            "objection": "This looks like an adaptation of vendor substrate work rather than a new theorem package.",
            "response": "The substrate reset is adapted, but the closed theoremlets, canonical hybrid object, strict extension, and conditional disintegration package are new in this branch.",
        },
        {
            "objection_id": "obj_proxy_thermodynamics",
            "targets": ["thermodynamic_consequence_proxy_reading"],
            "objection": "The thermodynamic consequence is too proxy-based.",
            "response": "The closed claim is only the weighted package-conditioned pressure gap theoremlet; KL-style closure-deficit language is support-only.",
        },
        {
            "objection_id": "obj_object_complexity",
            "targets": ["canonical_object_complexity", "reviewer_confusion_about_negative_results"],
            "objection": "The object is too complicated and the route changes are hard to follow.",
            "response": "The canonical object, traceability matrix, and non-claim firewall keep the final package auditable despite the development history.",
        },
    ]

    claim_posture = {
        "core_positioning": level3["paper_core_positioning"],
        "core_claim_ids": [
            "continuous_full_loop_lawfulness_theoremlet",
            "cocycle_pressure_closure_theoremlet",
            "strict_theory_extension_theoremlet",
            "conditional_pressure_disintegration_theoremlet",
        ],
        "support_only_claim_ids": [
            claim["claim_id"]
            for claim in ledger["claims"]
            if claim["claim_status"] == "supporting_evidence"
        ],
        "reserve_claim_ids": [
            claim["claim_id"]
            for claim in ledger["claims"]
            if claim["claim_status"] == "reserve"
        ],
        "nonclaim_ids": sorted(nonclaim_ids),
        "manuscript_posture": "State a Level-3 core on the audited shell, emphasize the canonical hybrid object and strict theory extension, and keep broader-scope ambitions outside the paper-core claim set.",
        "phrases_to_avoid": [
            "broader-class theorem",
            "shell-general result",
            "external/non-SFT breadth",
            "direct stratumwise root separation",
            "exact KL closure-deficit theorem",
        ],
    }

    decision = "ready_with_conservative_level3_positioning"
    if level3["paper_core_positioning"] != "level3_core_on_audited_shell":
        decision = "ready_but_level3_claim_should_be_softened"
    if traceability["decision"] not in {
        "traceability_complete",
        "traceability_complete_with_minor_gaps",
    }:
        decision = "not_publication_safe_yet"

    publication_risk = {
        "schema_version": "v1",
        "audit_id": "publication_risk_audit_v1",
        "generated_at_utc": timestamp(),
        "paper_core_positioning": level3["paper_core_positioning"],
        "strengths": strengths,
        "risks": risks,
        "objection_map": objection_map,
        "claim_posture": claim_posture,
        "decision": decision,
        "notes": [
            "The package is publication-ready only under conservative audited-shell claim discipline.",
            "The six-birds papers directory is absent from this snapshot, so the prior-paper baseline uses the in-repo vendor six-birds materials plus earlier internal theorem branches.",
        ],
    }

    contribution_counts = Counter(item["novelty_status"] for item in contributions)
    risk_counts = Counter(item["severity"] for item in risks)
    report = {
        "report_id": "publication_risk_audit_v1",
        "schema_version": "v1",
        "generated_at_utc": timestamp(),
        "contribution_counts_by_novelty_status": dict(contribution_counts),
        "risk_counts_by_severity": dict(risk_counts),
        "missing_baseline_comparison_summary": {
            "missing_paths": missing_baselines,
        },
        "claim_posture_summary": {
            "paper_core_positioning": claim_posture["core_positioning"],
            "core_claim_count": len(claim_posture["core_claim_ids"]),
            "support_only_claim_count": len(claim_posture["support_only_claim_ids"]),
            "reserve_claim_count": len(claim_posture["reserve_claim_ids"]),
            "nonclaim_count": len(claim_posture["nonclaim_ids"]),
        },
        "final_decision": decision,
    }

    DELTA_JSON_PATH.write_text(json.dumps(contribution_delta, indent=2) + "\n")
    RISK_JSON_PATH.write_text(json.dumps(publication_risk, indent=2) + "\n")
    REPORT_JSON_PATH.write_text(json.dumps(report, indent=2) + "\n")

    with REPORT_CSV_PATH.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["section", "key", "value"])
        for key, value in sorted(contribution_counts.items()):
            writer.writerow(["contribution_counts_by_novelty_status", key, value])
        for key, value in sorted(risk_counts.items()):
            writer.writerow(["risk_counts_by_severity", key, value])
        writer.writerow(["decision", "final_decision", decision])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
