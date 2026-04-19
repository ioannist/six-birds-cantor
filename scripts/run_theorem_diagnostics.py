#!/usr/bin/env python3
from __future__ import annotations

import csv
import datetime as dt
import json
import math
import subprocess
import sys
from pathlib import Path
from typing import Any

ALLOWED_CLASSIFICATIONS = {"likely_in", "inconclusive", "likely_out"}
ALLOWED_V2_STATUSES = {"included", "excluded", "not_claimed", "plausible_next", "blocked"}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(repo_root: Path, path: Path) -> str:
    return path.relative_to(repo_root).as_posix()


def parse_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def mechanical_compatibility(profile: dict[str, Any], values: dict[str, str]) -> bool:
    permitted_unknowns = set(profile.get("permitted_unknowns", []))
    for aid, expected in profile.get("required_assumptions", {}).items():
        actual = values.get(aid, "unknown")
        if actual == "unknown" and aid in permitted_unknowns:
            continue
        if actual != expected:
            return False
    for aid, forbidden in profile.get("forbidden_assumptions", {}).items():
        if values.get(aid) == forbidden:
            return False
    return True


def run_local_pressure_if_needed(repo_root: Path, config_path: Path) -> tuple[dict[str, Any], Path, Path]:
    config = load_json(config_path)
    experiment_id = str(config["experiment_id"])
    out_dir = repo_root / "results" / "local_pressure" / experiment_id
    manifest_path = out_dir / "result_manifest.json"
    csv_path = out_dir / f"{experiment_id}-local-pressure-run-0001_summary.csv"
    if manifest_path.exists() and csv_path.exists():
        return config, manifest_path, csv_path

    cmd = [
        sys.executable,
        str(repo_root / "scripts" / "run_local_pressure.py"),
        "--config",
        config_path.relative_to(repo_root).as_posix(),
    ]
    proc = subprocess.run(cmd, cwd=repo_root, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(f"local pressure regeneration failed for {config_path}:\n{proc.stdout}\n{proc.stderr}")
    return config, manifest_path, csv_path


def compute_memory_growth_proxy(config: dict[str, Any], csv_rows: list[dict[str, str]]) -> dict[str, Any]:
    family_id = str(config["family_id"])
    params = config.get("parameters", {})
    if family_id.startswith("classical.") or family_id.startswith("control."):
        return {"value": 1, "method": "constant_single_rule"}
    if family_id == "finite_state.adjacency_no_consecutive_2_base3":
        states = params.get("states", [])
        return {"value": len(states) if isinstance(states, list) else 2, "method": "config_state_count"}
    if family_id.startswith("contextual_local.prefix_memory"):
        transitions = params.get("transition_digits", {})
        return {"value": len(transitions) if isinstance(transitions, dict) else 2, "method": "explicit_transition_context_count"}
    if family_id == "contextual_local.domain_gated_two_map_local_ifs":
        maps = params.get("maps", [])
        return {"value": len(maps) if isinstance(maps, list) else 2, "method": "local_domain_map_count"}
    if family_id == "toy.local_ifs.nested_three_map_local_ifs":
        maps = params.get("maps", [])
        return {"value": len(maps) if isinstance(maps, list) else 3, "method": "local_domain_map_count"}
    if family_id == "contextual_local.stage_dependent_alternating_removal":
        stage_sets = params.get("stage_digit_sets", [])
        return {"value": len(stage_sets) if isinstance(stage_sets, list) else 2, "method": "stage_schedule_count"}
    if family_id.startswith("contextual_local.feedback"):
        seen = {
            (
                row.get("protocol_state", ""),
                row.get("gating_state", ""),
                row.get("lens_mode", ""),
                row.get("packaging_mode", ""),
            )
            for row in csv_rows
        }
        return {"value": len(seen), "method": "observed_feedback_state_tuples"}
    return {"value": 1, "method": "fallback_single_context"}


def classification_from_metrics(
    compatible: bool,
    metrics: dict[str, Any],
    thresholds: dict[str, float],
    assumption_values: dict[str, str],
) -> tuple[str, str]:
    if not compatible:
        return "likely_out", "mechanically incompatible with class profile"

    unknown_count = sum(1 for value in assumption_values.values() if value == "unknown")
    qm = metrics["concatenation_quasimultiplicativity_defect"]["value"]
    overlap = metrics["overlap_defect"]["value"]
    gap = metrics["upper_lower_pressure_gap"]["value"]
    drift = metrics["depth_sensitivity"]["last_step_drift"]

    if drift is not None and drift > thresholds["drift_out"]:
        return "likely_out", "depth sensitivity exceeds out threshold"
    if qm is not None and qm > thresholds["qm_out"]:
        return "likely_out", "quasi-multiplicativity defect exceeds out threshold"
    if overlap is not None and overlap > thresholds["overlap_out"]:
        return "likely_out", "overlap defect exceeds out threshold"
    if gap is not None and gap > thresholds["gap_out"]:
        return "likely_out", "upper/lower gap exceeds out threshold"

    if unknown_count > thresholds["unknown_likely_in_max"]:
        return "inconclusive", "too many unknown assumption tags"
    if qm is not None and qm > thresholds["qm_in"]:
        return "inconclusive", "quasi-multiplicativity defect above likely-in threshold"
    if drift is not None and drift > thresholds["drift_in"]:
        return "inconclusive", "depth sensitivity above likely-in threshold"
    if overlap is not None and overlap > thresholds["overlap_in"]:
        return "inconclusive", "overlap defect above likely-in threshold"
    if gap is not None and gap > thresholds["gap_in"]:
        return "inconclusive", "upper/lower gap above likely-in threshold"

    return "likely_in", "mechanically compatible and empirical defects are small"


def compute_metrics(repo_root: Path, config_path: Path, assumptions_tags: dict[str, Any]) -> dict[str, Any]:
    src_path = repo_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    from contextual_cantor.local_pressure import analyze_config, default_depths_from_config, upper_partition_sum

    config, manifest_path, csv_path = run_local_pressure_if_needed(repo_root, config_path)
    manifest = load_json(manifest_path)
    csv_rows = parse_csv_rows(csv_path)
    family_id = str(config["family_id"])
    assumption_values = assumptions_tags[family_id]["assumption_values"]

    depths = default_depths_from_config(config)
    analysis = analyze_config(config, depths=depths, s_min=0.0, s_max=2.0, tol=1e-10)
    analysis_rows = analysis["rows"]
    deepest = analysis_rows[-1]
    prev = analysis_rows[-2] if len(analysis_rows) >= 2 else deepest

    root_proxy = manifest["summary_metrics"].get("reference_root")
    if root_proxy is None:
        root_proxy = deepest["upper_root"]

    split_n = max(2, int(deepest["depth"]) // 2)
    split_m = int(deepest["depth"]) - split_n
    z_n, _ = upper_partition_sum(config, depth=split_n, s=float(root_proxy))
    z_m, _ = upper_partition_sum(config, depth=split_m, s=float(root_proxy))
    z_nm, _ = upper_partition_sum(config, depth=split_n + split_m, s=float(root_proxy))
    qm_defect = abs(math.log(z_nm) - math.log(z_n) - math.log(z_m)) / float(split_n + split_m)

    overlap_defect = deepest["interval_root_width"]
    gap = None
    if deepest["upper_root"] is not None and deepest["lower_root"] is not None:
        gap = abs(float(deepest["upper_root"]) - float(deepest["lower_root"]))

    drift = None
    if deepest["upper_root"] is not None and prev["upper_root"] is not None and deepest["depth"] != prev["depth"]:
        drift = abs(float(deepest["upper_root"]) - float(prev["upper_root"]))

    memory_proxy = compute_memory_growth_proxy(config, csv_rows)
    metrics = {
        "concatenation_quasimultiplicativity_defect": {
            "value": qm_defect,
            "split_depths": [split_n, split_m],
            "root_proxy": root_proxy,
        },
        "overlap_defect": {
            "value": overlap_defect,
            "note": "deepest upper_root-lower_root gap when available",
        },
        "memory_growth_proxy": memory_proxy,
        "upper_lower_pressure_gap": {
            "value": gap,
            "note": "deepest root gap proxy",
        },
        "depth_sensitivity": {
            "last_step_drift": drift,
            "max_depth": deepest["depth"],
            "depth_series": [row["depth"] for row in analysis_rows],
        },
    }
    return {
        "config": config,
        "manifest": manifest,
        "csv_path": csv_path,
        "manifest_path": manifest_path,
        "metrics": metrics,
        "analysis_rows": analysis_rows,
    }


def build_v1_report(repo_root: Path, assumptions: dict[str, Any], family_records: list[dict[str, Any]]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    profiles = {profile["class_id"]: profile for profile in assumptions["class_profiles"]}
    thresholds = {
        "qm_in": 0.02,
        "qm_out": 0.04,
        "overlap_in": 0.01,
        "overlap_out": 0.03,
        "gap_in": 0.01,
        "gap_out": 0.03,
        "drift_in": 0.02,
        "drift_out": 0.03,
        "unknown_likely_in_max": 3,
    }
    families = []
    for rec in family_records:
        family_id = rec["config"]["family_id"]
        values = rec["assumption_values"]
        metrics = rec["metrics"]
        primary_classification, primary_note = classification_from_metrics(
            mechanical_compatibility(profiles[assumptions["primary_class_id"]], values), metrics, thresholds, values
        )
        stretch_classification, stretch_note = classification_from_metrics(
            mechanical_compatibility(profiles[assumptions["stretch_class_id"]], values), metrics, thresholds, values
        )
        families.append(
            {
                "family_id": family_id,
                "config_path": rec["config_path_rel"],
                "run_ids": [rec["manifest"]["run_id"]],
                "metrics": metrics,
                "primary_classification": primary_classification,
                "stretch_classification": stretch_classification,
                "classification_note": f"primary: {primary_note}; stretch: {stretch_note}",
                "artifact_paths": [rec["manifest_path_rel"], rec["csv_path_rel"]],
            }
        )

    summary = {
        "count_by_primary_classification": {
            label: sum(1 for entry in families if entry["primary_classification"] == label)
            for label in sorted(ALLOWED_CLASSIFICATIONS)
        },
        "count_by_stretch_classification": {
            label: sum(1 for entry in families if entry["stretch_classification"] == label)
            for label in sorted(ALLOWED_CLASSIFICATIONS)
        },
        "good_contextual_candidates": [
            entry["family_id"]
            for entry in families
            if entry["family_id"].startswith("contextual_local.") and entry["primary_classification"] == "likely_in"
        ],
        "likely_counterexamples": [
            entry["family_id"]
            for entry in families
            if entry["primary_classification"] == "likely_out"
            or (entry["stretch_classification"] == "likely_out" and entry["primary_classification"] != "likely_in")
        ],
    }

    report = {
        "schema_version": "1.0",
        "report_id": "theorem_diagnostics_v1",
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
        "based_on_assumptions_path": rel(repo_root, repo_root / "docs" / "internal" / "theorem_assumptions_v1.json"),
        "families": families,
        "thresholds_used": thresholds,
        "summary": summary,
    }
    return report, families


def build_v2_report(repo_root: Path, family_records: list[dict[str, Any]]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    bowen_v1 = load_json(repo_root / "docs" / "internal" / "bowen_class_v1.json")
    bowen_v2 = load_json(repo_root / "docs" / "internal" / "bowen_class_v2.json")
    non_sft = load_json(repo_root / "docs" / "internal" / "non_sft_witness_evidence_v1.json")
    prior_v1_report_path = repo_root / "results" / "theorem_diagnostics" / "classification_report.json"
    prior_v1_rows = {}
    if prior_v1_report_path.exists():
        data = load_json(prior_v1_report_path)
        prior_v1_rows = {entry["family_id"]: entry for entry in data.get("families", [])}

    included_v1 = set(bowen_v1["included_families"])
    included_v2 = set(bowen_v2["included_families"])
    excluded_v2 = set(bowen_v2["excluded_families"])
    not_claimed_v2 = set(bowen_v2["not_claimed_families"])

    families = []
    for rec in family_records:
        family_id = rec["config"]["family_id"]
        if family_id in included_v2:
            status = "included"
            note = "Included in the enlarged Bowen v2 class."
        elif family_id == "contextual_local.domain_gated_two_map_local_ifs":
            status = "plausible_next"
            note = "Not yet in class; overlap diagnostics are not obstructive, but the equal-scale / finite continuation-type overlap theoremlet does not yet cover this local-domain geometry."
        elif family_id in excluded_v2:
            status = "blocked"
            note = "Explicitly excluded from Bowen v2 by current theorem assumptions."
        elif family_id in not_claimed_v2:
            status = "not_claimed"
            note = "Left outside the geometric Bowen v2 statement."
        else:
            status = "not_claimed"
            note = "Not claimed in Bowen v2."

        if family_id == "contextual_local.stage_dependent_alternating_removal":
            status = "blocked"
            note = "Blocked by nonstationary admissibility, so the bounded-overlap patch does not apply."
        if family_id.startswith("contextual_local.feedback"):
            status = "blocked"
            note = "Blocked by runtime feedback into admissibility / packaging, outside the v2 theorem class."

        families.append(
            {
                "family_id": family_id,
                "primary_v1_status": prior_v1_rows.get(family_id, {}).get("primary_classification"),
                "bowen_v2_status": status,
                "changed_since_v1": family_id in included_v2 and family_id not in included_v1,
                "classification_note": note,
                "artifact_paths": [rec["manifest_path_rel"], rec["csv_path_rel"]],
            }
        )

    newly_included = sorted(included_v2 - included_v1)
    still_excluded = sorted(excluded_v2)
    plausible_next = [entry["family_id"] for entry in families if entry["bowen_v2_status"] == "plausible_next"]
    blocked_frontier = [entry["family_id"] for entry in families if entry["bowen_v2_status"] == "blocked"]
    non_sft_blocker_status = "remains"
    if newly_included:
        non_sft_blocker_status = "partially_relaxed" if any(fid not in {non_sft.get("selected_family")} for fid in newly_included) else "remains"
    # stay conservative: inclusion of another finite-state prefix family does not resolve the blocker
    if all(fid.startswith("contextual_local.prefix_memory") or fid.startswith("classical.") for fid in newly_included):
        non_sft_blocker_status = "remains"

    impact_decision = "stronger_sft_like_theorem"
    if plausible_next and non_sft_blocker_status != "remains":
        impact_decision = "bridge_toward_frontier"

    report = {
        "schema_version": "1.0",
        "report_id": "theorem_diagnostics_v2",
        "based_on_bowen_class": "docs/internal/bowen_class_v2.json",
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
        "families": families,
        "summary": {
            "newly_included_families": newly_included,
            "still_excluded_families": still_excluded,
            "plausible_next_families": plausible_next,
            "blocked_frontier_families": blocked_frontier,
            "non_sft_blocker_status": non_sft_blocker_status,
        },
        "impact_decision": impact_decision,
    }
    return report, families


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    assumptions_path = repo_root / "docs" / "internal" / "theorem_assumptions_v1.json"
    assumptions = load_json(assumptions_path)
    tags = {entry["family_id"]: entry for entry in assumptions["family_assumption_tags"]}

    report_root = repo_root / "results" / "theorem_diagnostics"
    report_root.mkdir(parents=True, exist_ok=True)

    required_configs = [
        repo_root / "configs" / "experiments" / "classical" / "middle_thirds.json",
        repo_root / "configs" / "experiments" / "classical" / "restricted_digits_base5_024.json",
        repo_root / "configs" / "experiments" / "finite_state" / "adjacency_no_consecutive_2_base3.json",
        repo_root / "configs" / "experiments" / "contextual" / "prefix_memory_last_digit_rule.json",
        repo_root / "configs" / "experiments" / "contextual" / "prefix_memory_no_22_base3.json",
        repo_root / "configs" / "experiments" / "contextual" / "domain_gated_two_map_local_ifs.json",
        repo_root / "configs" / "experiments" / "contextual" / "stage_dependent_alternating_removal.json",
        repo_root / "configs" / "experiments" / "contextual" / "feedback_lens_protocol_coupled.json",
        repo_root / "configs" / "experiments" / "contextual" / "feedback_budget_gate_and_packaging.json",
        repo_root / "configs" / "experiments" / "local_ifs" / "nested_three_map_local_ifs.json",
    ]

    family_records = []
    for config_path in required_configs:
        computed = compute_metrics(repo_root, config_path, tags)
        family_records.append(
            {
                **computed,
                "config_path_rel": rel(repo_root, config_path),
                "manifest_path_rel": rel(repo_root, computed["manifest_path"]),
                "csv_path_rel": rel(repo_root, computed["csv_path"]),
                "assumption_values": tags[computed["config"]["family_id"]]["assumption_values"],
            }
        )

    report_v1, families_v1 = build_v1_report(repo_root, assumptions, family_records)
    report_json = report_root / "classification_report.json"
    report_json.write_text(json.dumps(report_v1, indent=2, sort_keys=True), encoding="utf-8")

    report_csv = report_root / "classification_report.csv"
    with report_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "family_id",
                "config_path",
                "run_id",
                "qm_defect",
                "overlap_defect",
                "memory_growth_proxy",
                "upper_lower_pressure_gap",
                "depth_sensitivity",
                "primary_classification",
                "stretch_classification",
                "classification_note",
            ],
        )
        writer.writeheader()
        for entry in families_v1:
            writer.writerow(
                {
                    "family_id": entry["family_id"],
                    "config_path": entry["config_path"],
                    "run_id": entry["run_ids"][0],
                    "qm_defect": entry["metrics"]["concatenation_quasimultiplicativity_defect"]["value"],
                    "overlap_defect": entry["metrics"]["overlap_defect"]["value"],
                    "memory_growth_proxy": entry["metrics"]["memory_growth_proxy"]["value"],
                    "upper_lower_pressure_gap": entry["metrics"]["upper_lower_pressure_gap"]["value"],
                    "depth_sensitivity": entry["metrics"]["depth_sensitivity"]["last_step_drift"],
                    "primary_classification": entry["primary_classification"],
                    "stretch_classification": entry["stretch_classification"],
                    "classification_note": entry["classification_note"],
                }
            )

    report_v2, families_v2 = build_v2_report(repo_root, family_records)
    report_v2_json = report_root / "classification_report_v2.json"
    report_v2_json.write_text(json.dumps(report_v2, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_v2_csv = report_root / "classification_report_v2.csv"
    with report_v2_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "family_id",
                "primary_v1_status",
                "bowen_v2_status",
                "changed_since_v1",
                "classification_note",
            ],
        )
        writer.writeheader()
        for entry in families_v2:
            writer.writerow({k: entry.get(k) for k in writer.fieldnames})

    notes_path = report_root / "classification_notes.md"
    notes_path.write_text(
        "# Classification Notes\n\n"
        "Metrics are computed from the T15 assumption pack plus local-pressure outputs.\n"
        "- quasi-multiplicativity defect uses a split-depth upper partition sum defect at a root proxy\n"
        "- overlap defect uses deepest upper/lower root gap when available\n"
        "- memory growth uses config-derived or observed controller-state proxies\n"
        "- depth sensitivity uses last-step drift from the depth series\n",
        encoding="utf-8",
    )
    print(f"wrote {rel(repo_root, report_json)} with {len(families_v1)} families")
    print(f"wrote {rel(repo_root, report_v2_json)} with {len(families_v2)} families")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
