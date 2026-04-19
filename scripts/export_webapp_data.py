#!/usr/bin/env python3
"""Export frozen internal theorem data to web-safe JSON for cantor-web."""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
INTERNAL = REPO_ROOT / "docs" / "internal"
OUTPUT_DIR = REPO_ROOT / "apps" / "cantor-web" / "public" / "data" / "v1"

SOURCE_FILES = {
    "level3_theorem_package": INTERNAL / "level3_theorem_package_v1.json",
    "claim_ledger": INTERNAL / "final_paper_core_claim_ledger_v1.json",
    "traceability": INTERNAL / "theorem_traceability_matrix_v1.json",
    "figure_manifest": INTERNAL / "figure_manifest_v1.json",
    "canonical_hybrid": INTERNAL / "canonical_hybrid_theorem_object_v1.json",
    "risk_audit": INTERNAL / "publication_risk_audit_v1.json",
    "pressure_closure": REPO_ROOT / "results" / "continuous_pressure_closure" / "report.json",
    "conditional_disintegration": REPO_ROOT / "results" / "conditional_disintegration" / "report.json",
    "pilot_report": REPO_ROOT / "results" / "continuous_kernel_pilot" / "report.json",
}


def load_source(key: str) -> dict:
    path = SOURCE_FILES[key]
    if not path.exists():
        print(f"ERROR: source file missing: {path}", file=sys.stderr)
        sys.exit(1)
    with open(path) as f:
        return json.load(f)


def export_index(timestamp: str) -> dict:
    continuous_datasets = [
        {
            "name": f"continuous/{wid}",
            "path": f"continuous/{wid}.json",
        }
        for wid in WITNESS_CONFIGS
    ]
    t0_datasets = [
        {
            "name": f"t0/{wid}_t0",
            "path": f"t0/{wid}_t0.json",
        }
        for wid in WITNESS_CONFIGS
    ]
    t1_datasets = [
        {
            "name": f"t1/{wid}_t1",
            "path": f"t1/{wid}_t1.json",
        }
        for wid in WITNESS_CONFIGS
    ]
    extension_datasets = [
        {
            "name": f"extension/{wid}_extension",
            "path": f"extension/{wid}_extension.json",
        }
        for wid in WITNESS_CONFIGS
    ]
    disintegration_datasets = [
        {
            "name": f"disintegration/{wid}_disintegration",
            "path": f"disintegration/{wid}_disintegration.json",
        }
        for wid in WITNESS_CONFIGS
    ]
    knockout_datasets = [
        {
            "name": f"knockouts/{wid}_knockouts",
            "path": f"knockouts/{wid}_knockouts.json",
        }
        for wid in WITNESS_CONFIGS
    ]
    return {
        "schema_version": "v1",
        "generated_at_utc": timestamp,
        "datasets": [
            {"name": "theorem-package", "path": "theorem-package.json"},
            {"name": "claim-ledger", "path": "claim-ledger.json"},
            {"name": "traceability", "path": "traceability.json"},
            {"name": "figure-manifest", "path": "figure-manifest.json"},
            {"name": "witnesses", "path": "witnesses.json"},
            *continuous_datasets,
            *t0_datasets,
            *t1_datasets,
            *extension_datasets,
            *disintegration_datasets,
            *knockout_datasets,
            {"name": "policy/annotation_policy", "path": "policy/annotation_policy.json"},
        ],
    }


def export_theorem_package(pkg: dict, hybrid: dict, risk: dict) -> dict:
    return {
        "schema_version": "v1",
        "package_id": pkg["package_id"],
        "paper_core_positioning": pkg["paper_core_positioning"],
        "canonical_object_id": pkg["canonical_object_id"],
        "core_class_id": pkg["core_class_id"],
        "selected_routes": pkg["selected_routes"],
        "included_theoremlets": [
            {
                "theoremlet_id": t["theoremlet_id"],
                "status": t["status"],
                "class_scope": t["class_scope"],
                "note": t["note"],
            }
            for t in pkg["included_theoremlets"]
        ],
        "nonclaims": pkg["nonclaims"],
        "reserve_routes": pkg["reserve_routes"],
        "canonical_hybrid_object": {
            "object_id": hybrid["object_id"],
            "base_theory_id": hybrid["base_theory_id"],
            "extended_theory_id": hybrid["extended_theory_id"],
            "decision": hybrid["decision"],
            "object_identity_verdict": hybrid["object_identity_verdict"],
            "factorization_verdict": hybrid["factorization_verdict"],
        },
        "claim_posture": risk["claim_posture"],
    }


def export_claim_ledger(ledger: dict) -> dict:
    return {
        "schema_version": "v1",
        "ledger_id": ledger["ledger_id"],
        "claim_counts": ledger["claim_counts"],
        "claims": [
            {
                "claim_id": c["claim_id"],
                "claim_status": c["claim_status"],
                "claim_type": c["claim_type"],
                "allowed_final_paper_use": c["allowed_final_paper_use"],
                "object_scope": c["object_scope"],
                "class_scope": c["class_scope"],
                "statement_short": c["statement_short"],
            }
            for c in ledger["claims"]
        ],
    }


def export_traceability(matrix: dict) -> dict:
    return {
        "schema_version": "v1",
        "matrix_id": matrix["matrix_id"],
        "paper_core_positioning": matrix["paper_core_positioning"],
        "decision": matrix["decision"],
        "theoremlets": [
            {
                "theoremlet_id": t["theoremlet_id"],
                "status": t["status"],
                "class_scope": t["class_scope"],
                "assumptions_used": t["assumptions_used"],
                "dependency_paths": t["dependency_paths"],
                "evidence_paths": t["evidence_paths"],
                "allowed_claim_ids": t["allowed_claim_ids"],
                "forbidden_claim_ids": t["forbidden_claim_ids"],
            }
            for t in matrix["theoremlets"]
        ],
        "claim_bindings": matrix["claim_bindings"],
        "scope_firewall": matrix["scope_firewall"],
    }


def export_figure_manifest(manifest: dict) -> dict:
    items = []
    for fig in manifest.get("figures", []) + manifest.get("tables", []):
        items.append(
            {
                "figure_id": fig["figure_id"],
                "title_short": fig["title_short"],
                "role": fig["role"],
                "status": fig["status"],
                "supports_theoremlets": fig["supports_theoremlets"],
                "allowed_claim_ids": fig["allowed_claim_ids"],
                "source_artifacts": fig["source_artifacts"],
            }
        )
    return {
        "schema_version": "v1",
        "manifest_id": manifest["manifest_id"],
        "figures": items,
        "allowed_claim_bindings": manifest["allowed_claim_bindings"],
        "nonclaim_bindings": manifest["nonclaim_bindings"],
    }


def export_witnesses(pkg: dict, matrix: dict) -> dict:
    witnesses = []
    for t in matrix["theoremlets"]:
        # Find matching theoremlet in package for witness families
        pkg_entry = next(
            (p for p in pkg["included_theoremlets"] if p["theoremlet_id"] == t["theoremlet_id"]),
            None,
        )
        families = pkg_entry["witness_families"] if pkg_entry else []
        witnesses.append(
            {
                "theoremlet_id": t["theoremlet_id"],
                "witness_families": families,
                "evidence_paths": t["evidence_paths"],
                "dependency_paths": t["dependency_paths"],
            }
        )
    return {
        "schema_version": "v1",
        "package_witness_families": pkg["witness_families"],
        "witnesses": witnesses,
    }


def export_t0_view(witness_id: str, hybrid: dict, pressure_report: dict, matrix: dict, pkg: dict) -> dict:
    """Build a T0 cocycle object view dataset for a specific witness."""
    family_id = f"generated.{witness_id}"

    # Find run data for this witness in the pressure closure report
    run = next((r for r in pressure_report["runs"] if r["family_id"] == family_id), None)

    # T0-scoped theoremlets: lawfulness + cocycle pressure only
    t0_allowed_theoremlet_ids = [
        "continuous_full_loop_lawfulness_theoremlet",
        "cocycle_pressure_closure_theoremlet",
    ]
    t0_theoremlets = [
        t for t in matrix["theoremlets"]
        if t["theoremlet_id"] in t0_allowed_theoremlet_ids
    ]

    # T0 allowed claims from the claim bindings
    t0_claim_bindings = [
        b for b in matrix["claim_bindings"]
        if b["theoremlet_id"] in t0_allowed_theoremlet_ids
    ]

    # T0 object map from hybrid
    t0_object_map = hybrid["base_object_map"]

    # Shell-stable class info
    core_class_id = pkg["core_class_id"]

    # Pressure object
    pressure_object = None
    if run:
        pressure_object = {
            "pressure_route": pressure_report["selected_pressure_route"],
            "observable_family": pressure_report["selected_observable_family"],
            "fekete_gap_proxy": run["fekete_gap_proxy"],
            "growth_bound_proxy": run["growth_bound_proxy"],
            "pressure_profiles": run["pressure_profiles"],
            "budget_range": run["budget_range"],
            "tau_range": run["tau_range"],
            "shell_exit_count": run["shell_exit_count"],
            "min_lens_margin": run["min_lens_margin"],
            "min_packaging_margin": run["min_packaging_margin"],
            "all_six_primitives_active": run["all_six_primitives_active"],
        }

    # Comparison-only T1 hint (minimal, clearly labeled)
    t1_comparison = {
        "_scope": "comparison_only",
        "object_identity_verdict": hybrid["object_identity_verdict"],
        "factorization_verdict": hybrid["factorization_verdict"],
        "macro_admissibility_verdict": hybrid["macro_admissibility_verdict"],
    }

    return {
        "schema_version": "v1",
        "witness_id": family_id,
        "theory_id": hybrid["base_theory_id"],
        "core_class_id": core_class_id,
        "shell_stable": True,
        "t0_object_map": t0_object_map,
        "theoremlets": [
            {
                "theoremlet_id": t["theoremlet_id"],
                "status": t["status"],
                "class_scope": t["class_scope"],
                "assumptions_used": t["assumptions_used"],
                "allowed_claim_ids": t["allowed_claim_ids"],
            }
            for t in t0_theoremlets
        ],
        "claim_bindings": [
            {
                "theoremlet_id": b["theoremlet_id"],
                "allowed_claim_ids": b["allowed_claim_ids"],
                "figure_ids": b["figure_ids"],
            }
            for b in t0_claim_bindings
        ],
        "pressure_object": pressure_object,
        "shell_uniform_bounds": pressure_report.get("support_summary", {}).get("shell_uniform_bounds"),
        "t1_comparison": t1_comparison,
    }


def export_extension_view(witness_id: str, config: dict, hybrid: dict, matrix: dict) -> dict:
    """Build an extension certificate dataset from the canonical hybrid object and T1 completion."""
    sys.path.insert(0, str(REPO_ROOT / "src"))
    from contextual_cantor.continuous_kernel_substrate import (
        simulate_substrate,
        compute_packaging_fixed_points,
        detect_packaging_saturation,
        _completion_initial_distributions,
        PilotParameters,
    )

    family_id = f"generated.{witness_id}"
    pp = PilotParameters(**config["pilot_parameters"])

    # Run substrate
    result = simulate_substrate(
        steps=config["steps"],
        n=config["kernel_dim"],
        seed=config["seed"],
        pilot_parameters=pp,
    )
    state = result["state"]
    kernel = state.kernel

    tau_values = [0.6, 0.75, 0.9]
    lens_states = ["spectral_lens", "row_similarity_cluster_lens", "audit_flow_quantile_lens"]
    initial_dists = _completion_initial_distributions(kernel)

    fp_result = compute_packaging_fixed_points(
        kernel, tau_values=tau_values, lens_states=lens_states,
        initial_distributions=initial_dists,
    )
    saturation = detect_packaging_saturation(
        fp_result["runs"], tau_values=tau_values,
        lens_states=lens_states, initial_count=len(initial_dists),
    )

    # Compute forcing and macro-admissibility summaries
    forcing_count = 0
    macro_obstruction_count = 0
    fixed_point_count = 0
    cycle_count = 0
    nonconvergent_count = 0
    for run in fp_result["runs"]:
        cs = run["completion_summary"]
        if cs["status"] == "fixed_point":
            fixed_point_count += 1
        elif cs["status"] == "cycle":
            cycle_count += 1
        else:
            nonconvergent_count += 1
        if run["feedback"]["applied"]:
            forcing_count += 1
        if not run["macro_admissibility"]["admissible"]:
            macro_obstruction_count += 1

    # Extension-allowed theoremlet
    ext_theoremlet_id = "strict_theory_extension_theoremlet"
    ext_theoremlet = next(
        (t for t in matrix["theoremlets"] if t["theoremlet_id"] == ext_theoremlet_id), None
    )
    ext_claim_binding = next(
        (b for b in matrix["claim_bindings"] if b["theoremlet_id"] == ext_theoremlet_id), None
    )

    return {
        "schema_version": "v1",
        "witness_id": family_id,
        "base_theory_id": hybrid["base_theory_id"],
        "extended_theory_id": hybrid["extended_theory_id"],
        "base_object_map": hybrid["base_object_map"],
        "extended_object_map": hybrid["extended_object_map"],
        "factorization_test": hybrid["factorization_test"],
        "verdicts": {
            "factorization": hybrid["factorization_verdict"],
            "object_identity": hybrid["object_identity_verdict"],
            "saturation": hybrid["saturation_verdict"],
            "forcing": hybrid["forcing_verdict"],
            "macro_admissibility": hybrid["macro_admissibility_verdict"],
        },
        "saturation_summary": {
            "saturated": saturation["saturated"],
            "saturated_panel_count": saturation["saturated_panel_count"],
            "total_panels": saturation["total_panels"],
        },
        "forcing_summary": {
            "p4_from_p5_event_count": forcing_count,
            "total_runs": len(fp_result["runs"]),
        },
        "macro_admissibility_summary": {
            "obstruction_count": macro_obstruction_count,
            "total_runs": len(fp_result["runs"]),
        },
        "completion_summary": {
            "distinct_strata": fp_result["distinct_fixed_point_count"],
            "fixed_point_runs": fixed_point_count,
            "cycle_runs": cycle_count,
            "nonconvergent_runs": nonconvergent_count,
        },
        "scope": "audited_shell_only",
        "theoremlet": {
            "theoremlet_id": ext_theoremlet["theoremlet_id"],
            "status": ext_theoremlet["status"],
            "class_scope": ext_theoremlet["class_scope"],
            "allowed_claim_ids": ext_theoremlet["allowed_claim_ids"],
        } if ext_theoremlet else None,
        "claim_binding": {
            "theoremlet_id": ext_claim_binding["theoremlet_id"],
            "allowed_claim_ids": ext_claim_binding["allowed_claim_ids"],
            "figure_ids": ext_claim_binding["figure_ids"],
        } if ext_claim_binding else None,
    }


def export_disintegration_view(witness_id: str, disint_report: dict, pressure_report: dict, matrix: dict) -> dict:
    """Build a conditional disintegration dataset for a specific witness."""
    family_id = f"generated.{witness_id}"

    # Find per-config data
    per_config = next((c for c in disint_report["per_config"] if c["config_id"] == family_id), None)
    pressure_run = next((r for r in pressure_report["runs"] if r["family_id"] == family_id), None)

    # Build compact descriptor summaries (drop full fiber vectors for size)
    descriptor_summaries = []
    if per_config:
        for ds in per_config["descriptor_summaries"]:
            gap_at_1 = ds["package_conditioned_pressure_gap"].get("1.0", {})
            descriptor_summaries.append({
                "lens_state": ds["descriptor"]["lens_state"],
                "tau": ds["descriptor"]["tau"],
                "gap_bounded_away_from_zero": ds["gap_bounded_away_from_zero"],
                "closure_deficit_proxy": ds["closure_deficit_proxy"],
                "pressure_gap": ds["package_conditioned_pressure_gap"],
                "fiber_count": len(ds["package_fiber_weights"]),
            })

    # T0 pressure summary
    t0_pressure = None
    if pressure_run:
        t0_pressure = {
            "pressure_route": pressure_report["selected_pressure_route"],
            "fekete_gap_proxy": pressure_run["fekete_gap_proxy"],
            "pressure_profiles": pressure_run["pressure_profiles"],
        }

    # Disintegration theoremlet
    disint_theoremlet_id = "conditional_pressure_disintegration_theoremlet"
    disint_theoremlet = next(
        (t for t in matrix["theoremlets"] if t["theoremlet_id"] == disint_theoremlet_id), None
    )
    disint_claim_binding = next(
        (b for b in matrix["claim_bindings"] if b["theoremlet_id"] == disint_theoremlet_id), None
    )

    return {
        "schema_version": "v1",
        "witness_id": family_id,
        "base_theory_id": disint_report["base_theory_id"],
        "extended_theory_id": disint_report["extended_theory_id"],
        "selected_consequence_object": disint_report["selected_consequence_object"],
        "decision": disint_report["decision"],
        "scope": "audited_shell_only",
        "t0_pressure": t0_pressure,
        "descriptor_summaries": descriptor_summaries,
        "config_summary": {
            "disintegration_supported": per_config["disintegration_supported"] if per_config else False,
            "min_gap": per_config["min_gap_across_descriptors"] if per_config else None,
            "max_closure_deficit_proxy": per_config["max_closure_deficit_proxy"] if per_config else None,
            "descriptor_count": per_config["package_fiber_descriptor_count"] if per_config else 0,
            "macro_admissibility_summary": per_config["macro_admissibility_summary"] if per_config else None,
        },
        "shell_stability": {
            "gap_bounded_on_both_witnesses": disint_report["support_verdict_summary"]["gap_bounded_away_from_zero_on_both_witnesses"],
            "macro_failure_aligns": disint_report["support_verdict_summary"]["macro_admissibility_failure_aligns_with_disintegration"],
            "working_route": disint_report["support_verdict_summary"]["working_route"],
        },
        "rejected_routes": {
            "direct_stratumwise_separation": {
                "status": "rejected",
                "reason": "Direct stratumwise root separation was not closed; the consequence object is the weighted package-conditioned pressure gap instead.",
            },
            "exact_kl_closure_deficit": {
                "status": "support_only",
                "reason": "KL-style closure-deficit proxies are supporting evidence, not the closed theorem object.",
            },
        },
        "theoremlet": {
            "theoremlet_id": disint_theoremlet["theoremlet_id"],
            "status": disint_theoremlet["status"],
            "class_scope": disint_theoremlet["class_scope"],
            "allowed_claim_ids": disint_theoremlet["allowed_claim_ids"],
        } if disint_theoremlet else None,
        "claim_binding": {
            "theoremlet_id": disint_claim_binding["theoremlet_id"],
            "allowed_claim_ids": disint_claim_binding["allowed_claim_ids"],
            "figure_ids": disint_claim_binding["figure_ids"],
        } if disint_claim_binding else None,
    }


def export_annotation_policy(pkg: dict, ledger: dict, matrix: dict, risk: dict) -> dict:
    """Build an annotation policy dataset from the frozen package."""
    posture = risk["claim_posture"]

    # Per-theoremlet allowed bindings
    per_theoremlet = []
    for t in matrix["theoremlets"]:
        per_theoremlet.append({
            "theoremlet_id": t["theoremlet_id"],
            "allowed_claim_ids": t["allowed_claim_ids"],
            "forbidden_claim_ids": t["forbidden_claim_ids"],
        })

    # Per-claim classification
    claim_classifications = {}
    for c in ledger["claims"]:
        claim_classifications[c["claim_id"]] = {
            "status": c["claim_status"],
            "allowed_final_paper_use": c["allowed_final_paper_use"],
            "claim_type": c["claim_type"],
        }

    return {
        "schema_version": "v1",
        "paper_core_positioning": pkg["paper_core_positioning"],
        "core_claim_ids": posture["core_claim_ids"],
        "support_only_claim_ids": posture["support_only_claim_ids"],
        "reserve_claim_ids": posture["reserve_claim_ids"],
        "nonclaim_ids": posture["nonclaim_ids"],
        "scope_guards": matrix["scope_firewall"]["scope_boundaries"],
        "per_theoremlet_bindings": per_theoremlet,
        "claim_classifications": claim_classifications,
        "phrases_to_avoid": posture["phrases_to_avoid"],
    }


PRIMITIVES = ["P1", "P2", "P3", "P4", "P5", "P6"]


def _run_knockout_simulation(config: dict, removed: str) -> dict:
    """Run a simulation with one primitive disabled and return summary metrics."""
    sys.path.insert(0, str(REPO_ROOT / "src"))
    from contextual_cantor.continuous_kernel_substrate import (
        simulate_substrate,
        PilotParameters,
    )

    pp = PilotParameters(**config["pilot_parameters"])
    activity = {p: (p != removed) for p in PRIMITIVES}

    result = simulate_substrate(
        steps=config["steps"],
        n=config["kernel_dim"],
        seed=config["seed"],
        primitive_activity=activity,
        pilot_parameters=pp,
    )
    state = result["state"]

    budget_min = min(state.budget_history) if state.budget_history else 0
    budget_max = max(state.budget_history) if state.budget_history else 0
    tau_min = min(state.tau_history) if state.tau_history else 0
    tau_max = max(state.tau_history) if state.tau_history else 0
    var_history = state.kernel_variation_history
    mean_var = sum(var_history) / len(var_history) if var_history else 0

    # Closure defect proxy: mean variation in last 10%
    tail = var_history[int(len(var_history) * 0.9):] if var_history else []
    defect_proxy = sum(tail) / len(tail) if tail else 0

    # Collapse detection
    collapsed_reasons = []
    if state.lens_switch_count == 0:
        collapsed_reasons.append("lens switching collapsed")
    if state.packaging_switch_count == 0:
        collapsed_reasons.append("packaging switching collapsed")
    if state.tau_switch_count <= 1:
        collapsed_reasons.append("tau switching collapsed")
    if budget_max - budget_min < 1.0:
        collapsed_reasons.append("budget range collapsed")
    if mean_var < 0.08:
        collapsed_reasons.append("variation damped")

    return {
        "removed": removed,
        "material_degradation": len(collapsed_reasons) > 0,
        "material_reasons": collapsed_reasons,
        "closure_defect_proxy": round(defect_proxy, 6),
        "summary": {
            "lens_switch_count": state.lens_switch_count,
            "packaging_switch_count": state.packaging_switch_count,
            "tau_switch_count": state.tau_switch_count,
            "budget_min": round(budget_min, 4),
            "budget_max": round(budget_max, 4),
            "tau_min": round(tau_min, 4),
            "tau_max": round(tau_max, 4),
            "mean_variation": round(mean_var, 6),
        },
    }


def export_knockouts(witness_id: str, config: dict, pilot_report: dict | None, matrix: dict) -> dict:
    """Build knockout comparison dataset."""
    family_id = f"generated.{witness_id}"

    # Try to use pre-computed pilot report knockout data for the base witness
    pilot_knockouts = None
    if pilot_report and pilot_report.get("knockout_results"):
        # Check if this is the matching witness (seed/dim match)
        if (pilot_report.get("kernel_dimension") == config["kernel_dim"]
                and pilot_report.get("steps") == config["steps"]):
            pilot_knockouts = pilot_report["knockout_results"]

    # Full loop reference
    sys.path.insert(0, str(REPO_ROOT / "src"))
    from contextual_cantor.continuous_kernel_substrate import simulate_substrate, PilotParameters
    pp = PilotParameters(**config["pilot_parameters"])
    result = simulate_substrate(
        steps=config["steps"], n=config["kernel_dim"],
        seed=config["seed"], pilot_parameters=pp,
    )
    state = result["state"]
    var_h = state.kernel_variation_history
    tail = var_h[int(len(var_h) * 0.9):] if var_h else []

    full_loop = {
        "lens_switch_count": state.lens_switch_count,
        "packaging_switch_count": state.packaging_switch_count,
        "tau_switch_count": state.tau_switch_count,
        "budget_min": round(min(state.budget_history), 4),
        "budget_max": round(max(state.budget_history), 4),
        "tau_min": round(min(state.tau_history), 4),
        "tau_max": round(max(state.tau_history), 4),
        "mean_variation": round(sum(var_h) / len(var_h), 6),
        "closure_defect_proxy": round(sum(tail) / len(tail), 6) if tail else 0,
    }

    # Build knockouts
    knockouts = []
    if pilot_knockouts:
        for ko in pilot_knockouts:
            knockouts.append({
                "removed": ko["removed"],
                "material_degradation": ko["material_degradation"],
                "material_reasons": ko.get("material_reasons", []),
                "closure_defect_proxy": round(ko.get("closure_idempotence_defect_proxy", 0), 6),
                "summary": {
                    "lens_switch_count": ko["summary"]["lens_switch_count"],
                    "packaging_switch_count": ko["summary"]["packaging_switch_count"],
                    "tau_switch_count": ko["summary"].get("tau_switch_count", 0),
                    "budget_min": round(ko["summary"]["budget_min"], 4),
                    "budget_max": round(ko["summary"]["budget_max"], 4),
                    "tau_min": round(full_loop["tau_min"], 4),  # pilot doesn't store tau range per knockout
                    "tau_max": round(full_loop["tau_max"], 4),
                    "mean_variation": 0,  # not in pilot
                },
            })
    else:
        for p in PRIMITIVES:
            print(f"    knockout {p}...")
            knockouts.append(_run_knockout_simulation(config, p))

    # Lawfulness theoremlet claim binding
    lawful_id = "continuous_full_loop_lawfulness_theoremlet"
    lawful_theoremlet = next(
        (t for t in matrix["theoremlets"] if t["theoremlet_id"] == lawful_id), None
    )
    lawful_binding = next(
        (b for b in matrix["claim_bindings"] if b["theoremlet_id"] == lawful_id), None
    )

    return {
        "schema_version": "v1",
        "witness_id": family_id,
        "scope": "audited_shell_only",
        "full_loop": full_loop,
        "knockouts": knockouts,
        "theoremlet": {
            "theoremlet_id": lawful_theoremlet["theoremlet_id"],
            "status": lawful_theoremlet["status"],
            "allowed_claim_ids": lawful_theoremlet["allowed_claim_ids"],
        } if lawful_theoremlet else None,
        "claim_binding": {
            "theoremlet_id": lawful_binding["theoremlet_id"],
            "allowed_claim_ids": lawful_binding["allowed_claim_ids"],
            "figure_ids": lawful_binding["figure_ids"],
        } if lawful_binding else None,
    }


LENS_STATES = ["spectral_lens", "row_similarity_cluster_lens", "audit_flow_quantile_lens"]
TAU_SAMPLE_VALUES = [0.6, 0.75, 0.9]


def export_t1_view(witness_id: str, config: dict, hybrid: dict) -> dict:
    """Build a T1 completion/fixed-point object view by running the completion endomap."""
    sys.path.insert(0, str(REPO_ROOT / "src"))
    from contextual_cantor.continuous_kernel_substrate import (
        simulate_substrate,
        compute_packaging_fixed_points,
        detect_packaging_saturation,
        update_lens_from_packaging,
        packaging_macro_admissibility,
        _completion_initial_distributions,
        PilotParameters,
    )

    family_id = f"generated.{witness_id}"
    pp = PilotParameters(**config["pilot_parameters"])

    # Run substrate to get final kernel state
    result = simulate_substrate(
        steps=config["steps"],
        n=config["kernel_dim"],
        seed=config["seed"],
        pilot_parameters=pp,
    )
    state = result["state"]
    kernel = state.kernel

    # Run completion endomap across tau/lens/initial combos
    initial_dists = _completion_initial_distributions(kernel)
    fp_result = compute_packaging_fixed_points(
        kernel,
        tau_values=TAU_SAMPLE_VALUES,
        lens_states=LENS_STATES,
        initial_distributions=initial_dists,
    )

    # Detect saturation
    saturation = detect_packaging_saturation(
        fp_result["runs"],
        tau_values=TAU_SAMPLE_VALUES,
        lens_states=LENS_STATES,
        initial_count=len(initial_dists),
    )

    # Build per-run compact summaries (no full histories)
    run_summaries = []
    p4_from_p5_events = []
    packaging_identity_changes = []
    strata_signatures = set()

    for run in fp_result["runs"]:
        cs = run["completion_summary"]
        fb = run["feedback"]
        ma = run["macro_admissibility"]
        sig = tuple(cs["final_signature"])
        strata_signatures.add(sig)

        run_summaries.append({
            "tau": run["tau"],
            "lens_state": run["lens_state"],
            "initial_index": run["initial_index"],
            "status": cs["status"],
            "iterations": cs["iterations"],
            "residual": round(cs["residual"], 8),
            "final_signature_hash": hash(sig) % (10**8),
            "macro_admissible": ma["admissible"],
        })

        # Track P4←P5 lens feedback events
        if fb["applied"]:
            p4_from_p5_events.append({
                "tau": run["tau"],
                "from_lens": fb["from_lens"],
                "to_lens": fb["to_lens"],
                "trigger_status": cs["status"],
                "package_count": fb["package_count"],
            })

        # Track packaging name changes across lens states
        packaging_identity_changes.append({
            "tau": run["tau"],
            "lens_state": run["lens_state"],
            "packaging_name": run["packaging_state"]["name"],
            "packaging_score": round(run["packaging_state"]["score"], 4),
            "group_count": len(run["packaging_state"]["groups"]),
        })

    # Deduplicate packaging identity changes
    seen_pi = set()
    unique_pi = []
    for pi in packaging_identity_changes:
        key = (pi["tau"], pi["lens_state"], pi["packaging_name"])
        if key not in seen_pi:
            seen_pi.add(key)
            unique_pi.append(pi)

    # T0 comparison (minimal, clearly labeled)
    t0_comparison = {
        "_scope": "comparison_only",
        "base_theory_id": hybrid["base_theory_id"],
        "base_object_map_id": hybrid["base_object_map"]["map_id"],
        "object_identity_verdict": hybrid["object_identity_verdict"],
        "macro_admissibility_verdict": hybrid["macro_admissibility_verdict"],
    }

    return {
        "schema_version": "v1",
        "witness_id": family_id,
        "theory_id": hybrid["extended_theory_id"],
        "extended_object_map": hybrid["extended_object_map"],
        "completion_config": {
            "tau_values": TAU_SAMPLE_VALUES,
            "lens_states": LENS_STATES,
            "initial_distribution_count": len(initial_dists),
            "kernel_dim": config["kernel_dim"],
        },
        "fixed_point_strata": {
            "distinct_count": fp_result["distinct_fixed_point_count"],
            "signatures": fp_result["distinct_fixed_point_signatures"],
        },
        "saturation": {
            "saturated": saturation["saturated"],
            "saturated_panel_count": saturation["saturated_panel_count"],
            "total_panels": saturation["total_panels"],
            "panel_summaries": saturation["panel_summaries"],
        },
        "run_summaries": run_summaries,
        "p4_from_p5_events": p4_from_p5_events,
        "packaging_identity_changes": unique_pi,
        "t0_comparison": t0_comparison,
    }


WITNESS_CONFIGS = {
    "continuous_full_loop_kernel": {
        "steps": 1000,
        "kernel_dim": 16,
        "seed": 17,
        "pilot_parameters": {
            "lens_hysteresis": 0.025,
            "packaging_hysteresis": 0.018,
            "budget_income_scale": 1.0,
            "budget_cost_scale": 1.0,
            "tau_initial": 1.0,
            "action_temperature_bias": 0.0,
            "lens_temperature_shift": 0.0,
        },
    },
    "continuous_full_loop_kernel_shell": {
        "steps": 600,
        "kernel_dim": 20,
        "seed": 5,
        "pilot_parameters": {
            "lens_hysteresis": 0.017,
            "packaging_hysteresis": 0.012,
            "budget_income_scale": 1.08,
            "budget_cost_scale": 0.96,
            "tau_initial": 0.88,
            "action_temperature_bias": 0.045,
            "lens_temperature_shift": 0.02,
        },
    },
}

# Kernel snapshot interval — every Nth step gets full kernel matrix
KERNEL_SNAPSHOT_INTERVAL = 10


def export_continuous_witness(witness_id: str, config: dict) -> dict:
    """Run simulate_substrate and build a compact web-safe trajectory."""
    sys.path.insert(0, str(REPO_ROOT / "src"))
    from contextual_cantor.continuous_kernel_substrate import (
        build_initial_state,
        step_substrate,
        _default_role_flags,
        PilotParameters,
    )
    import random as random_mod

    pp = PilotParameters(**config["pilot_parameters"])
    rng = random_mod.Random(config["seed"])
    state = build_initial_state(n=config["kernel_dim"], seed=config["seed"], pilot_parameters=pp)
    state.primitive_activity = _default_role_flags(None)

    timeline = []
    kernel_snapshots = []

    for i in range(config["steps"]):
        rec = step_substrate(state, rng, state.primitive_activity)
        step_data = {
            "step": rec["step"],
            "variation": round(rec["variation"], 6),
            "tau": round(state.tau_history[i], 6),
            "budget": round(state.budget_history[i], 6),
            "lens": rec["lens"]["name"],
            "packaging": rec["packaging"]["name"],
            "action_weights": {
                k: round(v, 4) for k, v in rec["action_weights"].items()
            },
            "primitive_activity": dict(state.primitive_activity),
        }
        timeline.append(step_data)

        if i % KERNEL_SNAPSHOT_INTERVAL == 0 or i == config["steps"] - 1:
            kernel_snapshots.append({
                "step": rec["step"],
                "kernel": [[round(v, 4) for v in row] for row in state.kernel],
            })

    return {
        "schema_version": "v1",
        "witness_id": f"generated.{witness_id}",
        "config": {
            "steps": config["steps"],
            "kernel_dim": config["kernel_dim"],
            "seed": config["seed"],
        },
        "total_steps": config["steps"],
        "kernel_snapshot_interval": KERNEL_SNAPSHOT_INTERVAL,
        "kernel_snapshots": kernel_snapshots,
        "timeline": timeline,
    }


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, sort_keys=False)
        f.write("\n")


def main() -> None:
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    pkg = load_source("level3_theorem_package")
    ledger = load_source("claim_ledger")
    matrix = load_source("traceability")
    manifest = load_source("figure_manifest")
    hybrid = load_source("canonical_hybrid")
    risk = load_source("risk_audit")
    pressure_report = load_source("pressure_closure")
    disint_report = load_source("conditional_disintegration")
    pilot_report = load_source("pilot_report")

    exports = {
        "index.json": export_index(timestamp),
        "theorem-package.json": export_theorem_package(pkg, hybrid, risk),
        "claim-ledger.json": export_claim_ledger(ledger),
        "traceability.json": export_traceability(matrix),
        "figure-manifest.json": export_figure_manifest(manifest),
        "witnesses.json": export_witnesses(pkg, matrix),
    }

    for filename, data in exports.items():
        out_path = OUTPUT_DIR / filename
        write_json(out_path, data)
        print(f"  exported: {out_path.relative_to(REPO_ROOT)}")

    # Export annotation policy
    policy_dir = OUTPUT_DIR / "policy"
    policy_dir.mkdir(parents=True, exist_ok=True)
    policy_data = export_annotation_policy(pkg, ledger, matrix, risk)
    policy_path = policy_dir / "annotation_policy.json"
    write_json(policy_path, policy_data)
    print(f"  exported: {policy_path.relative_to(REPO_ROOT)}")
    policy_count = 1

    # Export continuous trajectory datasets
    continuous_dir = OUTPUT_DIR / "continuous"
    continuous_dir.mkdir(parents=True, exist_ok=True)
    continuous_count = 0
    for wid, config in WITNESS_CONFIGS.items():
        print(f"  simulating: {wid} ({config['steps']} steps)...")
        data = export_continuous_witness(wid, config)
        out_path = continuous_dir / f"{wid}.json"
        write_json(out_path, data)
        print(f"  exported: {out_path.relative_to(REPO_ROOT)}")
        continuous_count += 1

    # Export T0 view datasets
    t0_dir = OUTPUT_DIR / "t0"
    t0_dir.mkdir(parents=True, exist_ok=True)
    t0_count = 0
    for wid in WITNESS_CONFIGS:
        data = export_t0_view(wid, hybrid, pressure_report, matrix, pkg)
        out_path = t0_dir / f"{wid}_t0.json"
        write_json(out_path, data)
        print(f"  exported: {out_path.relative_to(REPO_ROOT)}")
        t0_count += 1

    # Export T1 view datasets
    t1_dir = OUTPUT_DIR / "t1"
    t1_dir.mkdir(parents=True, exist_ok=True)
    t1_count = 0
    for wid, config in WITNESS_CONFIGS.items():
        print(f"  computing T1 completion: {wid}...")
        data = export_t1_view(wid, config, hybrid)
        out_path = t1_dir / f"{wid}_t1.json"
        write_json(out_path, data)
        print(f"  exported: {out_path.relative_to(REPO_ROOT)}")
        t1_count += 1

    # Export knockout datasets
    ko_dir = OUTPUT_DIR / "knockouts"
    ko_dir.mkdir(parents=True, exist_ok=True)
    ko_count = 0
    for wid, config in WITNESS_CONFIGS.items():
        # Use pilot report for base witness only
        use_pilot = pilot_report if wid == "continuous_full_loop_kernel" else None
        print(f"  computing knockouts: {wid}...")
        data = export_knockouts(wid, config, use_pilot, matrix)
        out_path = ko_dir / f"{wid}_knockouts.json"
        write_json(out_path, data)
        print(f"  exported: {out_path.relative_to(REPO_ROOT)}")
        ko_count += 1

    # Export disintegration datasets
    disint_dir = OUTPUT_DIR / "disintegration"
    disint_dir.mkdir(parents=True, exist_ok=True)
    disint_count = 0
    for wid in WITNESS_CONFIGS:
        data = export_disintegration_view(wid, disint_report, pressure_report, matrix)
        out_path = disint_dir / f"{wid}_disintegration.json"
        write_json(out_path, data)
        print(f"  exported: {out_path.relative_to(REPO_ROOT)}")
        disint_count += 1

    # Export extension certificate datasets
    ext_dir = OUTPUT_DIR / "extension"
    ext_dir.mkdir(parents=True, exist_ok=True)
    ext_count = 0
    for wid, config in WITNESS_CONFIGS.items():
        print(f"  computing extension certificate: {wid}...")
        data = export_extension_view(wid, config, hybrid, matrix)
        out_path = ext_dir / f"{wid}_extension.json"
        write_json(out_path, data)
        print(f"  exported: {out_path.relative_to(REPO_ROOT)}")
        ext_count += 1

    # Remove old placeholder if present
    placeholder = OUTPUT_DIR / "placeholder.json"
    if placeholder.exists():
        placeholder.unlink()
        print(f"  removed:  {placeholder.relative_to(REPO_ROOT)}")

    total = len(exports) + policy_count + continuous_count + t0_count + t1_count + ko_count + disint_count + ext_count
    print(f"\nDone. {total} datasets exported to {OUTPUT_DIR.relative_to(REPO_ROOT)}/")


if __name__ == "__main__":
    main()
