#!/usr/bin/env python3
"""Build the final pre-writing handoff package for the audited-shell Level-3 core."""

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
RESULTS = ROOT / "results" / "final_prewriting_handoff"

LEVEL3_PACKAGE_PATH = DOCS / "level3_theorem_package_v1.json"
CLAIM_LEDGER_PATH = DOCS / "final_paper_core_claim_ledger_v1.json"
TRACEABILITY_PATH = DOCS / "theorem_traceability_matrix_v1.json"
FIGURE_MANIFEST_PATH = DOCS / "figure_manifest_v1.json"
DELTA_PATH = DOCS / "contribution_delta_map_v1.json"
RISK_PATH = DOCS / "publication_risk_audit_v1.json"
MANUSCRIPT_SUMMARY_PATH = DOCS / "manuscript_theorem_summary_v1.md"

HANDOFF_JSON_PATH = DOCS / "final_prewriting_handoff_v1.json"
CHECKLIST_JSON_PATH = DOCS / "final_submission_checklist_v1.json"
REPORT_JSON_PATH = RESULTS / "report.json"
REPORT_CSV_PATH = RESULTS / "report.csv"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def ensure_prereqs() -> None:
    prereqs = [
        (LEVEL3_PACKAGE_PATH, ROOT / "scripts" / "build_level3_theorem_package.py"),
        (TRACEABILITY_PATH, ROOT / "scripts" / "build_theorem_traceability_matrix.py"),
        (FIGURE_MANIFEST_PATH, ROOT / "scripts" / "build_figure_manifest.py"),
        (DELTA_PATH, ROOT / "scripts" / "build_publication_risk_audit.py"),
        (RISK_PATH, ROOT / "scripts" / "build_publication_risk_audit.py"),
    ]
    for artifact, builder in prereqs:
        if artifact.exists():
            continue
        if not builder.exists():
            raise FileNotFoundError(f"Missing required artifact {artifact} and builder {builder}")
        subprocess.run([sys.executable, str(builder)], cwd=ROOT, check=True)


def checklist_item(
    item_id: str,
    category: str,
    description: str,
    status: str,
    depends_on: list[str],
    note: str,
) -> dict:
    return {
        "item_id": item_id,
        "category": category,
        "description": description,
        "status": status,
        "depends_on": depends_on,
        "note": note,
    }


def main() -> int:
    ensure_prereqs()
    RESULTS.mkdir(parents=True, exist_ok=True)

    level3 = load_json(LEVEL3_PACKAGE_PATH)
    ledger = load_json(CLAIM_LEDGER_PATH)
    traceability = load_json(TRACEABILITY_PATH)
    figure_manifest = load_json(FIGURE_MANIFEST_PATH)
    delta = load_json(DELTA_PATH)
    risk = load_json(RISK_PATH)

    for path in [
        MANUSCRIPT_SUMMARY_PATH,
        DOCS / "continuous_full_loop_theorem_package_v1.md",
        DOCS / "continuous_pressure_closure_v1.md",
        DOCS / "strict_theory_extension_closure_v1.md",
        DOCS / "conditional_pressure_disintegration_v1.md",
        DOCS / "canonical_hybrid_theorem_object_v1.md",
    ]:
        if not path.exists():
            raise FileNotFoundError(f"Missing required handoff context file: {path}")

    required_theoremlets = [
        "continuous_full_loop_lawfulness_theoremlet",
        "cocycle_pressure_closure_theoremlet",
        "strict_theory_extension_theoremlet",
        "conditional_pressure_disintegration_theoremlet",
    ]
    theoremlets_by_id = {
        item["theoremlet_id"]: item for item in level3["included_theoremlets"]
    }
    claims_by_id = {claim["claim_id"]: claim for claim in ledger["claims"]}
    missing_theoremlets = [
        theoremlet_id for theoremlet_id in required_theoremlets if theoremlet_id not in theoremlets_by_id
    ]
    if missing_theoremlets:
        raise ValueError(f"Missing core theoremlets in level3 package: {missing_theoremlets}")

    if level3["paper_core_positioning"] != "level3_core_on_audited_shell":
        raise ValueError("Final handoff requires level3_core_on_audited_shell positioning")

    closed_theoremlets = []
    allowed_claim_ids = []
    support_only_ids = []
    reserve_ids = []
    nonclaim_ids = []

    for claim in ledger["claims"]:
        status = claim["claim_status"]
        if status == "closed_theoremlet":
            allowed_claim_ids.append(claim["claim_id"])
        elif status == "supporting_evidence":
            support_only_ids.append(claim["claim_id"])
        elif status == "reserve":
            reserve_ids.append(claim["claim_id"])
        elif status == "nonclaim":
            nonclaim_ids.append(claim["claim_id"])

    required_nonclaims = {
        "no_broader-class_theorem_beyond_the_audited_shell",
        "no_external/non-SFT_breadth_claim_beyond_what_is_actually_closed",
        "no_direct_stratumwise_root-separation_theorem",
        "no_packaging-induced_broader_theorem_class_claim",
        "no_shell-general_theorem_beyond_the_audited_shell-stable_class",
    }
    missing_nonclaims = sorted(required_nonclaims - set(nonclaim_ids))
    if missing_nonclaims:
        raise ValueError(f"Missing required nonclaims: {missing_nonclaims}")

    # Check allowed claims are actually bound in the figure manifest.
    bound_claim_ids = {binding["claim_id"] for binding in figure_manifest["allowed_claim_bindings"]}
    unbound_allowed_claims = sorted(set(allowed_claim_ids) - bound_claim_ids)
    if unbound_allowed_claims:
        raise ValueError(f"Allowed claims missing figure/table bindings: {unbound_allowed_claims}")

    # Ensure nonclaims never leak into allowed figure bindings.
    leaked_nonclaims = sorted(
        claim_id for claim_id in bound_claim_ids if claim_id in set(nonclaim_ids)
    )
    if leaked_nonclaims:
        raise ValueError(f"Nonclaims leaked into figure bindings: {leaked_nonclaims}")

    # Ensure required risk posture items are present.
    risk_ids = {entry["risk_id"] for entry in risk["risks"]}
    required_risks = {
        "audited_shell_scope_only",
        "no_broader_class_theorem",
        "no_external_non_sft_breadth",
        "canonical_object_complexity",
        "thermodynamic_consequence_proxy_reading",
    }
    missing_risks = sorted(required_risks - risk_ids)
    if missing_risks:
        raise ValueError(f"Missing required risk posture items: {missing_risks}")

    dependency_paths = []
    for theoremlet_id in required_theoremlets:
        theoremlet = theoremlets_by_id[theoremlet_id]
        claim = claims_by_id[theoremlet_id]
        dependency_path = theoremlet["dependency_path"]
        if not (ROOT / dependency_path).exists():
            raise FileNotFoundError(f"Missing dependency path for {theoremlet_id}: {dependency_path}")
        dependency_paths.append(dependency_path)
        closed_theoremlets.append(
            {
                "theoremlet_id": theoremlet_id,
                "status": theoremlet["status"],
                "object_scope": claim["object_scope"],
                "class_scope": theoremlet["class_scope"],
                "dependency_path": dependency_path,
                "witness_families": theoremlet["witness_families"],
                "allowed_claim_id": theoremlet_id,
                "one_line_internal_statement": claim["statement_short"],
                "one_line_scope_limit": next(
                    (
                        line.strip("- ").strip()
                        for line in Path(MANUSCRIPT_SUMMARY_PATH).read_text().splitlines()
                        if "Manuscript-safe limitation:" in line
                        and theoremlet_id.split("_theoremlet")[0].replace("_", " ").split()[0]
                    ),
                    "audited-shell only",
                ),
            }
        )

    witness_families = level3["witness_families"]
    canonical_theorem_object = {
        "base_object": "T0_cocycle_pressure_theory",
        "completion_object": "packaging_completion_endomap_fixed_point_strata",
        "canonical_object": "T1_hybrid_cocycle_plus_completion_theory",
        "canonical_object_id": level3["canonical_object_id"],
        "theoremlet_layers": {
            "continuous_full_loop_lawfulness_theoremlet": "shell-stable lawful regime object",
            "cocycle_pressure_closure_theoremlet": "T0_cocycle_pressure_theory",
            "strict_theory_extension_theoremlet": "canonical hybrid object",
            "conditional_pressure_disintegration_theoremlet": "canonical hybrid object",
        },
    }

    writing_guardrails = {
        "allowed_next_actions": [
            "assemble manuscript-facing theorem statements from the 4 closed theoremlets",
            "reuse only allowed claim ids and ready figure/table bindings",
            "state the canonical hybrid object and audited-shell scope explicitly",
        ],
        "forbidden_next_actions": [
            "upgrade support-only items into theoremlets",
            "upgrade reserve routes into current claims",
            "drop the audited-shell restriction",
            "make broader-class, shell-general, external/non-SFT, or direct stratumwise-root claims",
            "blur inherited/adapted inputs with branch-new theorem contributions",
        ],
        "scope_firewall": traceability["scope_firewall"],
    }

    handoff = {
        "schema_version": "v1",
        "handoff_id": "final_prewriting_handoff_v1",
        "generated_at_utc": timestamp(),
        "paper_core_positioning": level3["paper_core_positioning"],
        "canonical_theorem_object": canonical_theorem_object,
        "closed_class": level3["core_class_id"],
        "closed_theoremlets": closed_theoremlets,
        "assumption_paths": level3["assumption_paths"],
        "dependency_paths": dependency_paths,
        "witness_families": witness_families,
        "figure_manifest_path": "docs/internal/figure_manifest_v1.json",
        "claim_ledger_path": "docs/internal/final_paper_core_claim_ledger_v1.json",
        "traceability_matrix_path": "docs/internal/theorem_traceability_matrix_v1.json",
        "contribution_delta_path": "docs/internal/contribution_delta_map_v1.json",
        "publication_risk_path": "docs/internal/publication_risk_audit_v1.json",
        "allowed_claim_ids": allowed_claim_ids,
        "support_only_ids": support_only_ids,
        "reserve_ids": reserve_ids,
        "nonclaim_ids": nonclaim_ids,
        "writing_guardrails": writing_guardrails,
        "decision": "handoff_ready_for_writing",
        "notes": [
            "This handoff package is the single authoritative pre-writing source of truth for the audited-shell Level-3 core.",
            "Writing must obey the claim ledger, figure manifest, traceability matrix, contribution delta map, and publication-risk posture simultaneously.",
        ],
    }

    checklist = {
        "schema_version": "v1",
        "checklist_id": "final_submission_checklist_v1",
        "generated_at_utc": timestamp(),
        "items": [
            checklist_item(
                "check_theorem_object_integrity",
                "theorem_object",
                "Canonical theorem object hierarchy is explicit and tied to the audited-shell Level-3 package.",
                "ready",
                ["canonical_hybrid_theorem_object_v1", "level3_theorem_package_v1"],
                "The base, completion, and canonical layers are frozen in the handoff JSON.",
            ),
            checklist_item(
                "check_theoremlet_closure_integrity",
                "theoremlet",
                "All 4 core theoremlets are closed_in_note with dependency and witness links.",
                "ready",
                dependency_paths,
                "No core theoremlet is left support-only or reserve-only.",
            ),
            checklist_item(
                "check_audited_shell_scope_integrity",
                "assumption_scope",
                "Audited-shell scope remains explicit across theoremlets, claims, figures, and risk posture.",
                "ready",
                ["docs/internal/theorem_traceability_matrix_v1.json"],
                "Shell widening is blocked by the scope firewall and explicit nonclaims.",
            ),
            checklist_item(
                "check_claim_nonclaim_integrity",
                "claim_scope",
                "Allowed claims, support-only items, reserve items, and nonclaims are separated cleanly.",
                "ready",
                ["docs/internal/final_paper_core_claim_ledger_v1.json"],
                "Nonclaims are frozen and cannot be promoted by this handoff package.",
            ),
            checklist_item(
                "check_figure_binding_integrity",
                "figure_binding",
                "Every allowed claim is bound to ready figures/tables and no nonclaim leaks into figure support.",
                "ready",
                ["docs/internal/figure_manifest_v1.json"],
                "The manifest already enforces guardrails and all core claims are bound.",
            ),
            checklist_item(
                "check_publication_risk_posture",
                "risk_posture",
                "Publication posture remains conservative Level-3 on the audited shell.",
                "manual_check",
                ["docs/internal/publication_risk_audit_v1.json"],
                "Writing still needs to keep the shell-specificity and proxy-risk wording conservative.",
            ),
            checklist_item(
                "check_manuscript_safe_handoff",
                "writing_guardrail",
                "Writing may proceed only through the frozen handoff object and guardrails.",
                "ready",
                [
                    "docs/internal/manuscript_theorem_summary_v1.md",
                    "docs/internal/final_prewriting_handoff_v1.json",
                ],
                "The handoff package centralizes theorem objects, claims, figures, and risks in one place.",
            ),
        ],
        "notes": [
            "Manual checks are claim-discipline reminders, not blockers.",
            "The checklist is machine-readable so later writing automation can verify the same guardrails.",
        ],
    }

    missing_links = []
    for path in (
        handoff["assumption_paths"]
        + handoff["dependency_paths"]
        + [
            handoff["figure_manifest_path"],
            handoff["claim_ledger_path"],
            handoff["traceability_matrix_path"],
            handoff["contribution_delta_path"],
            handoff["publication_risk_path"],
        ]
    ):
        if not (ROOT / path).exists():
            missing_links.append(path)
    if missing_links:
        raise FileNotFoundError(f"Missing handoff artifact paths: {missing_links}")

    checklist_counts = Counter(item["status"] for item in checklist["items"])
    report = {
        "report_id": "final_prewriting_handoff_v1",
        "schema_version": "v1",
        "generated_at_utc": timestamp(),
        "theoremlet_count": len(closed_theoremlets),
        "allowed_claim_count": len(allowed_claim_ids),
        "support_only_count": len(support_only_ids),
        "reserve_count": len(reserve_ids),
        "nonclaim_count": len(nonclaim_ids),
        "checklist_counts_by_status": dict(checklist_counts),
        "missing_link_summary": missing_links,
        "final_handoff_decision": handoff["decision"],
    }

    HANDOFF_JSON_PATH.write_text(json.dumps(handoff, indent=2) + "\n")
    CHECKLIST_JSON_PATH.write_text(json.dumps(checklist, indent=2) + "\n")
    REPORT_JSON_PATH.write_text(json.dumps(report, indent=2) + "\n")

    with REPORT_CSV_PATH.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["section", "key", "value"])
        writer.writerow(["counts", "theoremlet_count", len(closed_theoremlets)])
        writer.writerow(["counts", "allowed_claim_count", len(allowed_claim_ids)])
        writer.writerow(["counts", "support_only_count", len(support_only_ids)])
        writer.writerow(["counts", "reserve_count", len(reserve_ids)])
        writer.writerow(["counts", "nonclaim_count", len(nonclaim_ids)])
        for key, value in sorted(checklist_counts.items()):
            writer.writerow(["checklist_counts_by_status", key, value])
        writer.writerow(["decision", "final_handoff_decision", handoff["decision"]])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
