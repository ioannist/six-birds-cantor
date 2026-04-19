#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"required artifact missing: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def rel(repo_root: Path, path: Path) -> str:
    return path.relative_to(repo_root).as_posix()


def manifest_run_id(manifest: dict[str, Any]) -> str:
    run_id = manifest.get("run_id")
    if not isinstance(run_id, str) or not run_id:
        raise ValueError("manifest missing run_id")
    return run_id


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    out_path = repo_root / "docs" / "internal" / "observation_claim_ledger_v1.json"

    comp_json_path = repo_root / "results" / "transfer_operator" / "baseline_comparison.json"
    stability_summary_path = repo_root / "results" / "robustness" / "local_pressure_stability_v1" / "stability_summary.json"
    stability_table_path = repo_root / "results" / "robustness" / "local_pressure_stability_v1" / "stability_table.csv"
    decision_note_path = repo_root / "docs" / "internal" / "rigorous_method_decision_v1.md"

    mt_cert_path = repo_root / "results" / "certified_bracketing" / "middle-thirds-baseline" / "result_manifest.json"
    adj_cert_path = repo_root / "results" / "certified_bracketing" / "adjacency-no-consecutive-2-base3-baseline" / "result_manifest.json"
    mt_lp_path = repo_root / "results" / "local_pressure" / "middle-thirds-baseline" / "result_manifest.json"
    base5_lp_path = repo_root / "results" / "local_pressure" / "restricted-digits-base5-024-baseline" / "result_manifest.json"
    adj_lp_path = repo_root / "results" / "local_pressure" / "adjacency-no-consecutive-2-base3-baseline" / "result_manifest.json"
    prefix_lp_path = repo_root / "results" / "local_pressure" / "prefix-memory-no-22-base3" / "result_manifest.json"
    lens_lp_path = repo_root / "results" / "local_pressure" / "feedback-lens-protocol-coupled" / "result_manifest.json"
    budget_lp_path = repo_root / "results" / "local_pressure" / "feedback-budget-gate-and-packaging" / "result_manifest.json"
    lens_feedback_summary_path = repo_root / "results" / "feedback_contextual" / "feedback-lens-protocol-coupled" / "feedback-lens-protocol-coupled-run-0001_summary.json"
    budget_feedback_summary_path = repo_root / "results" / "feedback_contextual" / "feedback-budget-gate-and-packaging" / "feedback-budget-gate-and-packaging-run-0001_summary.json"

    comp_json = load_json(comp_json_path)
    stability_summary = load_json(stability_summary_path)
    mt_cert = load_json(mt_cert_path)
    adj_cert = load_json(adj_cert_path)
    mt_lp = load_json(mt_lp_path)
    base5_lp = load_json(base5_lp_path)
    adj_lp = load_json(adj_lp_path)
    prefix_lp = load_json(prefix_lp_path)
    lens_lp = load_json(lens_lp_path)
    budget_lp = load_json(budget_lp_path)
    lens_feedback_summary = load_json(lens_feedback_summary_path)
    budget_feedback_summary = load_json(budget_feedback_summary_path)
    if not decision_note_path.exists():
        raise FileNotFoundError(f"required artifact missing: {decision_note_path}")

    comparison_rows = {row["family_id"]: row for row in comp_json["rows"]}
    summary_by_family = stability_summary["summary_by_family"]
    unstable_cases = stability_summary["unstable_cases"]

    mt_ref = mt_cert["summary_metrics"]["reference_root"]
    adj_ref = adj_cert["summary_metrics"]["reference_root"]

    entries = [
        {
            "claim_id": "OBS-001",
            "status": "baseline_fact",
            "family_ids": ["classical.middle_thirds"],
            "run_ids": [manifest_run_id(mt_cert), manifest_run_id(mt_lp)],
            "artifact_paths": [rel(repo_root, mt_cert_path), rel(repo_root, mt_lp_path), rel(repo_root, comp_json_path)],
            "quantitative_support": {
                "reference_root": mt_ref,
                "certified_width": mt_cert["summary_metrics"]["certified_width"],
                "partition_abs_error": comparison_rows["classical.middle_thirds"]["abs_error_partition"],
                "transfer_abs_error": comparison_rows["classical.middle_thirds"]["abs_error_transfer"],
            },
            "qualitative_note": "Middle-thirds agrees across partition, certified, and transfer baselines at very small error scales.",
            "tags": ["baseline", "agreement", "classical"],
        },
        {
            "claim_id": "OBS-002",
            "status": "baseline_fact",
            "family_ids": ["classical.restricted_digits_base5_024"],
            "run_ids": [manifest_run_id(base5_lp)],
            "artifact_paths": [rel(repo_root, base5_lp_path), rel(repo_root, comp_json_path)],
            "quantitative_support": {
                "reference_root": comparison_rows["classical.restricted_digits_base5_024"]["reference_root"],
                "partition_abs_error": comparison_rows["classical.restricted_digits_base5_024"]["abs_error_partition"],
                "transfer_abs_error": comparison_rows["classical.restricted_digits_base5_024"]["abs_error_transfer"],
            },
            "qualitative_note": "Base-5 restricted-digit baseline also shows exact-method agreement at tested precision.",
            "tags": ["baseline", "agreement", "classical"],
        },
        {
            "claim_id": "OBS-003",
            "status": "baseline_fact",
            "family_ids": ["finite_state.adjacency_no_consecutive_2_base3"],
            "run_ids": [manifest_run_id(adj_cert), manifest_run_id(adj_lp)],
            "artifact_paths": [rel(repo_root, adj_cert_path), rel(repo_root, adj_lp_path), rel(repo_root, comp_json_path)],
            "quantitative_support": {
                "reference_root": adj_ref,
                "certified_width": adj_cert["summary_metrics"]["certified_width"],
                "partition_abs_error": comparison_rows["finite_state.adjacency_no_consecutive_2_base3"]["abs_error_partition"],
                "transfer_abs_error": comparison_rows["finite_state.adjacency_no_consecutive_2_base3"]["abs_error_transfer"],
            },
            "qualitative_note": "Finite-state adjacency exact value is certified and transfer-accurate, while partition remains biased upward.",
            "tags": ["baseline", "finite_state", "bias"],
        },
        {
            "claim_id": "OBS-004",
            "status": "empirical_pattern",
            "family_ids": ["classical.middle_thirds", "finite_state.adjacency_no_consecutive_2_base3", "classical.restricted_digits_base5_024"],
            "run_ids": [manifest_run_id(mt_lp), manifest_run_id(adj_lp), manifest_run_id(base5_lp)],
            "artifact_paths": [rel(repo_root, comp_json_path)],
            "quantitative_support": {
                "transfer_runtime_ms": {
                    "middle_thirds": comparison_rows["classical.middle_thirds"]["runtime_ms_transfer"],
                    "adjacency": comparison_rows["finite_state.adjacency_no_consecutive_2_base3"]["runtime_ms_transfer"],
                    "base5": comparison_rows["classical.restricted_digits_base5_024"]["runtime_ms_transfer"],
                },
                "partition_runtime_ms": {
                    "middle_thirds": comparison_rows["classical.middle_thirds"]["runtime_ms_partition"],
                    "adjacency": comparison_rows["finite_state.adjacency_no_consecutive_2_base3"]["runtime_ms_partition"],
                    "base5": comparison_rows["classical.restricted_digits_base5_024"]["runtime_ms_partition"],
                },
            },
            "qualitative_note": "Transfer operator is faster and more accurate on current baselines than partition estimates.",
            "tags": ["comparison", "runtime", "accuracy"],
        },
        {
            "claim_id": "OBS-005",
            "status": "empirical_pattern",
            "family_ids": ["contextual_local.prefix_memory_no_22_base3"],
            "run_ids": [manifest_run_id(prefix_lp)],
            "artifact_paths": [rel(repo_root, prefix_lp_path), rel(repo_root, stability_summary_path), rel(repo_root, stability_table_path)],
            "quantitative_support": {
                "final_upper_root": prefix_lp["summary_metrics"]["final_upper_root"],
                "final_lower_root": prefix_lp["summary_metrics"]["final_lower_root"],
                "max_spread": summary_by_family["contextual_local.prefix_memory_no_22_base3"]["max_spread"],
                "max_drift": summary_by_family["contextual_local.prefix_memory_no_22_base3"]["max_drift"],
            },
            "qualitative_note": "Prefix-memory family shows upper/lower equality at tested depths and moderate stability under OFAT ablations.",
            "tags": ["contextual", "memory", "stability"],
        },
        {
            "claim_id": "OBS-006",
            "status": "empirical_pattern",
            "family_ids": ["contextual_local.feedback_budget_gate_and_packaging"],
            "run_ids": [manifest_run_id(budget_lp), budget_feedback_summary["run_id"]],
            "artifact_paths": [rel(repo_root, budget_lp_path), rel(repo_root, budget_feedback_summary_path)],
            "quantitative_support": {
                "final_upper_root": budget_lp["summary_metrics"]["final_upper_root"],
                "final_lower_root": budget_lp["summary_metrics"]["final_lower_root"],
                "packaging_switches": budget_feedback_summary["switch_counts"]["packaging_switches"],
                "cells_fired": budget_feedback_summary["cells_fired_at_least_once"],
            },
            "qualitative_note": "Budget-driven feedback family yields tractable pressure outputs while recording explicit packaging and gating-driven state changes.",
            "tags": ["feedback", "budget", "tractable"],
        },
        {
            "claim_id": "OBS-007",
            "status": "empirical_pattern",
            "family_ids": ["contextual_local.feedback_lens_protocol_coupled"],
            "run_ids": [manifest_run_id(lens_lp), lens_feedback_summary["run_id"]],
            "artifact_paths": [rel(repo_root, lens_lp_path), rel(repo_root, lens_feedback_summary_path)],
            "quantitative_support": {
                "cells_fired": lens_feedback_summary["cells_fired_at_least_once"],
                "protocol_switches": lens_feedback_summary["switch_counts"]["protocol_switches"],
                "lens_switches": lens_feedback_summary["switch_counts"]["lens_switches"],
                "packaging_switches": lens_feedback_summary["switch_counts"]["packaging_switches"],
            },
            "qualitative_note": "Lens/protocol feedback family audibly realizes P2<-P4, P3<-P4, P4<-P3, and P5<-P4 in the recorded sample run.",
            "tags": ["feedback", "pica", "auditable"],
        },
        {
            "claim_id": "OBS-008",
            "status": "empirical_pattern",
            "family_ids": ["contextual_local.feedback_budget_gate_and_packaging"],
            "run_ids": [budget_feedback_summary["run_id"], manifest_run_id(budget_lp)],
            "artifact_paths": [rel(repo_root, budget_feedback_summary_path), rel(repo_root, budget_lp_path)],
            "quantitative_support": {
                "cells_fired": budget_feedback_summary["cells_fired_at_least_once"],
                "packaging_switches": budget_feedback_summary["switch_counts"]["packaging_switches"],
                "final_interval_root_width": budget_lp["summary_metrics"]["final_lower_root"] - budget_lp["summary_metrics"]["final_upper_root"],
            },
            "qualitative_note": "Budget family realizes auditable P2<-P6 and P5<-P6 while retaining usable pressure outputs.",
            "tags": ["feedback", "budget", "pica"],
        },
        {
            "claim_id": "OBS-009",
            "status": "empirical_pattern",
            "family_ids": ["finite_state.adjacency_no_consecutive_2_base3", "contextual_local.prefix_memory_no_22_base3"],
            "run_ids": [manifest_run_id(adj_lp), manifest_run_id(prefix_lp)],
            "artifact_paths": [rel(repo_root, stability_summary_path), rel(repo_root, stability_table_path)],
            "quantitative_support": {
                "adjacency_max_spread": summary_by_family["finite_state.adjacency_no_consecutive_2_base3"]["max_spread"],
                "adjacency_max_drift": summary_by_family["finite_state.adjacency_no_consecutive_2_base3"]["max_drift"],
                "prefix_max_spread": summary_by_family["contextual_local.prefix_memory_no_22_base3"]["max_spread"],
                "prefix_max_drift": summary_by_family["contextual_local.prefix_memory_no_22_base3"]["max_drift"],
            },
            "qualitative_note": "Adjacency and prefix-memory controls show depth-sensitive improvement patterns without crossing current instability thresholds.",
            "tags": ["ablation", "depth", "controls"],
        },
        {
            "claim_id": "OBS-010",
            "status": "risky_open",
            "family_ids": ["contextual_local.feedback_lens_protocol_coupled"],
            "run_ids": [manifest_run_id(lens_lp)] + [case["run_id"] for case in unstable_cases],
            "artifact_paths": [rel(repo_root, lens_lp_path), rel(repo_root, stability_summary_path), rel(repo_root, stability_table_path)],
            "quantitative_support": {
                "default_drift": lens_lp["summary_metrics"]["last_step_upper_root_drift"],
                "max_spread": summary_by_family["contextual_local.feedback_lens_protocol_coupled"]["max_spread"],
                "unstable_case_count": summary_by_family["contextual_local.feedback_lens_protocol_coupled"]["unstable_count"],
            },
            "qualitative_note": "Feedback lens/protocol family is depth-sensitive and currently unstable under the present OFAT thresholds.",
            "tags": ["risk", "feedback", "stability"],
        },
        {
            "claim_id": "OBS-011",
            "status": "baseline_fact",
            "family_ids": ["classical.middle_thirds", "finite_state.adjacency_no_consecutive_2_base3", "contextual_local.feedback_lens_protocol_coupled"],
            "run_ids": [manifest_run_id(mt_lp), manifest_run_id(adj_lp), manifest_run_id(lens_lp)],
            "artifact_paths": [rel(repo_root, decision_note_path), rel(repo_root, comp_json_path), rel(repo_root, lens_lp_path)],
            "quantitative_support": {
                "method_decision": "partition_sums_plus_certified_bracketing",
                "contextual_coverage_present": True,
                "transfer_contextual_coverage_present": False,
            },
            "qualitative_note": "Project default method remains partition sums plus certified bracketing because it covers contextual families now.",
            "tags": ["decision", "coverage", "method"],
        },
        {
            "claim_id": "OBS-012",
            "status": "risky_open",
            "family_ids": ["classical.middle_thirds", "finite_state.adjacency_no_consecutive_2_base3", "contextual_local.feedback_lens_protocol_coupled"],
            "run_ids": [manifest_run_id(mt_lp), manifest_run_id(adj_lp), manifest_run_id(lens_lp)],
            "artifact_paths": [rel(repo_root, comp_json_path), rel(repo_root, decision_note_path)],
            "quantitative_support": {
                "transfer_baseline_abs_errors": {
                    "middle_thirds": comparison_rows["classical.middle_thirds"]["abs_error_transfer"],
                    "adjacency": comparison_rows["finite_state.adjacency_no_consecutive_2_base3"]["abs_error_transfer"],
                },
                "transfer_contextual_support": None,
            },
            "qualitative_note": "Transfer route is a strong baseline validator but is not yet implemented for contextual/local families.",
            "tags": ["risk", "transfer", "coverage"],
        },
    ]

    ledger = {
        "schema_version": "1.0",
        "ledger_id": "observation_claim_ledger_v1",
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
        "entries": entries,
    }
    out_path.write_text(json.dumps(ledger, indent=2, sort_keys=True), encoding="utf-8")
    print(f"wrote {rel(repo_root, out_path)} with {len(entries)} entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
