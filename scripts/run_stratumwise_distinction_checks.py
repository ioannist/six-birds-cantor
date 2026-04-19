#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import math
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT_WINDOW_TOLERANCE = 1e-5
PROFILE_GAP_THRESHOLD = 1e-4
WEIGHTED_CONDITIONAL_THRESHOLD = 1e-3


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _ensure_report(repo_root: Path, path: Path, script: str) -> None:
    if path.exists():
        return
    subprocess.run(["python", script], cwd=repo_root, check=True)


def _sig_key(signature: list[float]) -> tuple[float, ...]:
    return tuple(round(float(x), 6) for x in signature)


def _entropy(signature: tuple[float, ...]) -> float:
    out = 0.0
    for x in signature:
        if x > 0.0:
            out -= x * math.log(x)
    return out


def _stratum_profile(
    signature: tuple[float, ...],
    pressure_profiles: dict[str, dict[str, float]],
) -> dict[str, Any]:
    entropy = _entropy(signature)
    support = sum(1 for x in signature if x > 1e-9)
    concentration = sum(x * x for x in signature)
    profile: dict[str, float] = {}
    signs: dict[str, int] = {}

    for s_key, payload in pressure_profiles.items():
        s = float(s_key)
        moment = sum(max(x, 1e-12) ** (1.0 + s) for x in signature)
        proxy = float(payload["pressure_proxy"]) + math.log(moment) / max(1, support)
        profile[s_key] = proxy
        signs[s_key] = 1 if proxy > 0 else -1 if proxy < 0 else 0

    min_abs = min(abs(value) for value in profile.values())
    root_window = sorted(
        float(s_key)
        for s_key, value in profile.items()
        if abs(value) <= min_abs + ROOT_WINDOW_TOLERANCE
    )

    return {
        "pressure_profile": profile,
        "sign_profile": signs,
        "root_window": root_window,
        "entropy": entropy,
        "concentration": concentration,
    }


def _profile_distance(a: dict[str, float], b: dict[str, float]) -> float:
    keys = sorted(set(a) | set(b))
    return max(abs(a[key] - b[key]) for key in keys)


def _root_windows_separated(a: list[float], b: list[float]) -> bool:
    return set(a).isdisjoint(set(b))


def _summarize_config(
    config_id: str,
    pressure: dict[str, Any],
    completion: dict[str, Any],
) -> dict[str, Any]:
    pressure_cfg = next(item for item in pressure["runs"] if item["family_id"] == config_id)
    completion_cfg = next(item for item in completion["summaries"] if item["config_id"] == config_id)

    runs = completion_cfg["runs"]
    strata_runs: dict[tuple[float, ...], list[dict[str, Any]]] = defaultdict(list)
    descriptor_to_strata: dict[tuple[Any, ...], set[tuple[float, ...]]] = defaultdict(set)

    for run in runs:
        signature = _sig_key(run["completion_summary"]["final_signature"])
        strata_runs[signature].append(run)
        descriptor = (
            config_id,
            round(float(run["tau"]), 3),
            run["lens_state"],
        )
        descriptor_to_strata[descriptor].add(signature)

    persistent = {sig: group for sig, group in strata_runs.items() if len(group) > 1}
    profiles = {
        sig: {
            "run_count": len(group),
            **_stratum_profile(sig, pressure_cfg["pressure_profiles"]),
        }
        for sig, group in persistent.items()
    }

    descriptor_summaries: list[dict[str, Any]] = []
    root_window_supported = True
    profile_gap_supported = True
    multi_strata_descriptors = 0

    for descriptor, strata in sorted(descriptor_to_strata.items()):
        persistent_strata = sorted(sig for sig in strata if sig in profiles)
        if len(persistent_strata) < 2:
            continue

        multi_strata_descriptors += 1
        pairwise_gaps = []
        root_window_pairs = []
        sign_profile_pairs = []

        for idx, first in enumerate(persistent_strata):
            for second in persistent_strata[idx + 1 :]:
                first_profile = profiles[first]
                second_profile = profiles[second]
                gap = _profile_distance(
                    first_profile["pressure_profile"],
                    second_profile["pressure_profile"],
                )
                pairwise_gaps.append(gap)
                root_window_pairs.append(
                    _root_windows_separated(
                        first_profile["root_window"],
                        second_profile["root_window"],
                    )
                )
                sign_profile_pairs.append(
                    first_profile["sign_profile"] != second_profile["sign_profile"]
                )

        descriptor_root_support = any(root_window_pairs) or any(sign_profile_pairs)
        descriptor_profile_support = any(gap >= PROFILE_GAP_THRESHOLD for gap in pairwise_gaps)
        root_window_supported &= descriptor_root_support
        profile_gap_supported &= descriptor_profile_support

        descriptor_summaries.append(
            {
                "descriptor": {
                    "config_id": descriptor[0],
                    "tau": descriptor[1],
                    "lens_state": descriptor[2],
                },
                "persistent_t1_strata_count": len(persistent_strata),
                "pairwise_profile_gap_max": max(pairwise_gaps) if pairwise_gaps else 0.0,
                "pairwise_profile_gap_mean": (
                    sum(pairwise_gaps) / len(pairwise_gaps) if pairwise_gaps else 0.0
                ),
                "root_window_separated": descriptor_root_support,
                "profile_gap_supported": descriptor_profile_support,
                "root_windows": {
                    str(sig): profiles[sig]["root_window"] for sig in persistent_strata
                },
            }
        )

    if multi_strata_descriptors == 0:
        root_window_supported = False
        profile_gap_supported = False

    weighted_conditional = {}
    weighted_conditional_supported = True
    for s_key, payload in pressure_cfg["pressure_profiles"].items():
        total_weight = sum(item["run_count"] for item in profiles.values())
        weighted_pressure = (
            sum(item["pressure_profile"][s_key] * item["run_count"] for item in profiles.values())
            / total_weight
            if total_weight
            else float(payload["pressure_proxy"])
        )
        difference = weighted_pressure - float(payload["pressure_proxy"])
        weighted_conditional[s_key] = {
            "t0_pressure": float(payload["pressure_proxy"]),
            "weighted_conditional_pressure": weighted_pressure,
            "difference": difference,
        }
        weighted_conditional_supported &= abs(difference) >= WEIGHTED_CONDITIONAL_THRESHOLD

    return {
        "config_id": config_id,
        "t0_descriptor_classes_checked": len(descriptor_to_strata),
        "persistent_packaged_strata_detected": len(profiles),
        "descriptors_with_multiple_persistent_t1_strata": multi_strata_descriptors,
        "persistent_strata_profiles": {
            str(sig): profile for sig, profile in profiles.items()
        },
        "within_t0_fiber_comparisons": descriptor_summaries,
        "weighted_conditional_profiles": weighted_conditional,
        "route_support": {
            "root_window_separation_route": root_window_supported,
            "profile_gap_route": profile_gap_supported,
            "weighted_conditional_distinction_route": weighted_conditional_supported,
        },
    }


def run() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    hybrid_path = repo_root / "results" / "hybrid_pressure_root" / "report.json"
    canonical_path = repo_root / "results" / "canonical_hybrid_extension" / "report.json"
    strict_extension_path = repo_root / "results" / "strict_theory_extension_closure" / "report.json"
    pressure_path = repo_root / "results" / "continuous_pressure_closure" / "report.json"
    completion_path = repo_root / "results" / "packaging_completion_endomap" / "report.json"

    _ensure_report(repo_root, hybrid_path, "scripts/run_hybrid_pressure_root_checks.py")
    _ensure_report(repo_root, canonical_path, "scripts/run_canonical_hybrid_extension_checks.py")
    _ensure_report(repo_root, strict_extension_path, "scripts/run_strict_theory_extension_closure_checks.py")
    _ensure_report(repo_root, pressure_path, "scripts/run_continuous_pressure_closure_checks.py")
    _ensure_report(repo_root, completion_path, "scripts/run_packaging_completion_endomap.py")

    hybrid = _load_json(hybrid_path)
    canonical = _load_json(canonical_path)
    strict_extension = _load_json(strict_extension_path)
    pressure = _load_json(pressure_path)
    completion = _load_json(completion_path)

    configs = hybrid["configs"]
    per_config = [
        _summarize_config(config_id, pressure, completion) for config_id in configs
    ]

    root_supported = all(
        item["route_support"]["root_window_separation_route"] for item in per_config
    )
    profile_gap_supported = all(
        item["route_support"]["profile_gap_route"] for item in per_config
    )
    weighted_conditional_supported = all(
        item["route_support"]["weighted_conditional_distinction_route"] for item in per_config
    )

    selected_working_route = "weighted_conditional_distinction_route"
    selected_reserve_route = "profile_gap_route"
    decision = "stratumwise_distinction_signal_but_still_ambiguous"

    if root_supported:
        selected_working_route = "root_window_separation_route"
        selected_reserve_route = "profile_gap_route"
        decision = "stratumwise_distinction_sharpened"
    elif profile_gap_supported:
        selected_working_route = "profile_gap_route"
        selected_reserve_route = "weighted_conditional_distinction_route"
        decision = "stratumwise_distinction_sharpened"
    elif weighted_conditional_supported:
        selected_working_route = "weighted_conditional_distinction_route"
        selected_reserve_route = "profile_gap_route"
        decision = "stratumwise_route_not_viable"

    report = {
        "report_id": "stratumwise_distinction_v1",
        "schema_version": "v1",
        "generated_at_utc": "2026-03-19T00:00:00Z",
        "decision": decision,
        "base_theory_id": "T0_cocycle_pressure_theory",
        "extended_theory_id": "T1_hybrid_cocycle_plus_completion_theory",
        "configs": configs,
        "frozen_configs": [
            "configs/experiments/generated/continuous_full_loop_kernel.json",
            "configs/experiments/generated/continuous_full_loop_kernel_shell.json",
        ],
        "selected_working_route": selected_working_route,
        "selected_reserve_route": selected_reserve_route,
        "route_support_summary": {
            "root_window_separation_route": root_supported,
            "profile_gap_route": profile_gap_supported,
            "weighted_conditional_distinction_route": weighted_conditional_supported,
        },
        "support_verdict_summary": {
            "canonical_object_verdict": canonical["decision"],
            "strict_extension_verdict": strict_extension["decision"],
            "persistent_strata_on_both_witnesses": all(
                item["persistent_packaged_strata_detected"] > 0 for item in per_config
            ),
            "within_t0_fiber_root_window_separation": root_supported,
            "within_t0_fiber_profile_gap_separation": profile_gap_supported,
            "weighted_conditional_signal": weighted_conditional_supported,
        },
        "per_config": per_config,
        "notes": [
            "The comparison is made inside fixed T0 descriptor classes on the canonical hybrid object.",
            "Direct root-window and direct profile-gap separation remain the desired stratumwise routes.",
            "If only weighted conditional distinction survives, the ticket should pivot to the disintegration-style stretch route.",
        ],
    }

    out_dir = repo_root / "results" / "stratumwise_distinction"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    with (out_dir / "report.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "config_id",
                "persistent_packaged_strata_detected",
                "descriptors_with_multiple_persistent_t1_strata",
                "root_window_separation_route",
                "profile_gap_route",
                "weighted_conditional_distinction_route",
            ]
        )
        for item in per_config:
            writer.writerow(
                [
                    item["config_id"],
                    item["persistent_packaged_strata_detected"],
                    item["descriptors_with_multiple_persistent_t1_strata"],
                    item["route_support"]["root_window_separation_route"],
                    item["route_support"]["profile_gap_route"],
                    item["route_support"]["weighted_conditional_distinction_route"],
                ]
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(run())
