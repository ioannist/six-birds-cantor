#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import math
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _ensure_report(repo_root: Path, path: Path, script: str) -> None:
    if path.exists():
        return
    subprocess.run(["python", script], cwd=repo_root, check=True)


def _sig_key(signature: list[float]) -> tuple[float, ...]:
    return tuple(round(float(x), 6) for x in signature)


def _entropy(signature: list[float]) -> float:
    out = 0.0
    for x in signature:
        if x > 0.0:
            out -= x * math.log(x)
    return out


def _stratum_profile(
    signature: list[float],
    pressure_profiles: dict[str, dict[str, float]],
) -> dict[str, Any]:
    entropy = _entropy(signature)
    concentration = sum(float(x) ** 2 for x in signature)
    support = sum(1 for x in signature if x > 1e-9)
    profile: dict[str, float] = {}
    signs: dict[str, int] = {}

    for s_key, payload in pressure_profiles.items():
        s = float(s_key)
        moment = sum(max(float(x), 1e-12) ** (1.0 + s) for x in signature)
        proxy = float(payload["pressure_proxy"]) + math.log(moment) / max(1, support)
        profile[s_key] = proxy
        signs[s_key] = 1 if proxy > 0 else -1 if proxy < 0 else 0

    root_candidate = min(profile, key=lambda k: abs(profile[k]))
    return {
        "pressure_profile": profile,
        "root_candidate": float(root_candidate),
        "sign_profile": signs,
        "entropy": entropy,
        "concentration": concentration,
    }


def _profile_distance(a: dict[str, float], b: dict[str, float]) -> float:
    keys = sorted(set(a) | set(b))
    return max(abs(a[k] - b[k]) for k in keys)


def _summarize_config(
    config_id: str,
    pressure: dict[str, Any],
    completion: dict[str, Any],
    canonical: dict[str, Any],
) -> dict[str, Any]:
    pressure_cfg = next(item for item in pressure["runs"] if item["family_id"] == config_id)
    completion_cfg = next(item for item in completion["summaries"] if item["config_id"] == config_id)
    canonical_cfg = next(item for item in canonical["per_config"] if item["config_id"] == config_id)

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

    persistent = {
        sig: group for sig, group in strata_runs.items() if len(group) > 1
    }
    persistent_profiles: dict[str, Any] = {}
    for sig, group in persistent.items():
        profile = _stratum_profile(list(sig), pressure_cfg["pressure_profiles"])
        persistent_profiles[str(sig)] = {
            "run_count": len(group),
            **profile,
        }

    descriptor_distinctions = []
    for descriptor, strata in descriptor_to_strata.items():
        if len(strata) < 2:
            continue
        strata_list = sorted(strata)
        distances = []
        for i in range(len(strata_list)):
            for j in range(i + 1, len(strata_list)):
                a = persistent_profiles.get(str(strata_list[i]))
                b = persistent_profiles.get(str(strata_list[j]))
                if a is None or b is None:
                    continue
                distances.append(_profile_distance(a["pressure_profile"], b["pressure_profile"]))
        descriptor_distinctions.append(
            {
                "descriptor": {
                    "config_id": descriptor[0],
                    "tau": descriptor[1],
                    "lens_state": descriptor[2],
                },
                "strata_count": len(strata),
                "max_profile_distance": max(distances) if distances else 0.0,
                "thermodynamically_distinguished": any(distance > 1e-5 for distance in distances),
            }
        )

    weighted_disintegration = {}
    for s_key, payload in pressure_cfg["pressure_profiles"].items():
        total_weight = sum(item["run_count"] for item in persistent_profiles.values())
        if total_weight == 0:
            weighted = 0.0
        else:
            weighted = sum(
                item["pressure_profile"][s_key] * item["run_count"]
                for item in persistent_profiles.values()
            ) / total_weight
        weighted_disintegration[s_key] = {
            "t0_pressure": float(payload["pressure_proxy"]),
            "weighted_stratum_pressure": weighted,
            "difference": weighted - float(payload["pressure_proxy"]),
        }

    return {
        "config_id": config_id,
        "persistent_packaged_strata_detected": len(persistent_profiles),
        "persistent_strata_profiles": persistent_profiles,
        "descriptor_level_distinctions": descriptor_distinctions,
        "weighted_disintegration": weighted_disintegration,
        "canonical_factorization_verdict": canonical_cfg["factorization_test"]["factor_through_T0"],
        "stratumwise_pressure_existence_supported": len(persistent_profiles) > 0,
        "root_separation_supported": any(
            item["thermodynamically_distinguished"] for item in descriptor_distinctions
        ),
        "conditional_disintegration_supported": any(
            abs(item["difference"]) > 1e-6 for item in weighted_disintegration.values()
        ),
    }


def run() -> int:
    repo_root = Path(__file__).resolve().parent.parent

    canonical_path = repo_root / "results" / "canonical_hybrid_extension" / "report.json"
    pressure_path = repo_root / "results" / "continuous_pressure_closure" / "report.json"
    closure_path = repo_root / "results" / "strict_theory_extension_closure" / "report.json"
    completion_path = repo_root / "results" / "packaging_completion_endomap" / "report.json"

    _ensure_report(repo_root, canonical_path, "scripts/run_canonical_hybrid_extension_checks.py")
    _ensure_report(repo_root, pressure_path, "scripts/run_continuous_pressure_closure_checks.py")
    _ensure_report(repo_root, closure_path, "scripts/run_strict_theory_extension_closure_checks.py")
    _ensure_report(repo_root, completion_path, "scripts/run_packaging_completion_endomap.py")

    canonical = _load_json(canonical_path)
    pressure = _load_json(pressure_path)
    completion = _load_json(completion_path)
    _ = _load_json(closure_path)

    configs = canonical["configs"]
    per_config = [
        _summarize_config(config_id, pressure, completion, canonical) for config_id in configs
    ]

    stratumwise_supported = all(
        item["stratumwise_pressure_existence_supported"] for item in per_config
    )
    root_separation_supported = all(
        item["root_separation_supported"] for item in per_config
    )
    disintegration_supported = all(
        item["conditional_disintegration_supported"] for item in per_config
    )

    selected_working_route = "conditional_pressure_disintegration_route"
    selected_stretch_route = None

    decision = (
        "consequence_route_plausible"
        if disintegration_supported
        else "consequence_route_not_ready"
    )

    report = {
        "report_id": "hybrid_pressure_root_v1",
        "schema_version": "v1",
        "generated_at_utc": "2026-03-19T00:00:00Z",
        "decision": decision,
        "base_theory_id": "T0_cocycle_pressure_theory",
        "extended_theory_id": "T1_hybrid_cocycle_plus_completion_theory",
        "selected_working_route": selected_working_route,
        "selected_stretch_route": selected_stretch_route,
        "rejected_routes": [
            "stratumwise_pressure_existence_route",
            "root_separation_within_T0_route"
        ],
        "configs": configs,
        "frozen_configs": [
            "configs/experiments/generated/continuous_full_loop_kernel.json",
            "configs/experiments/generated/continuous_full_loop_kernel_shell.json",
        ],
        "route_support_summary": {
            "stratumwise_pressure_existence_route": stratumwise_supported,
            "root_separation_within_T0_route": root_separation_supported,
            "conditional_pressure_disintegration_route": disintegration_supported,
        },
        "support_verdict_summary": {
            "persistent_packaged_strata_detected": all(
                item["persistent_packaged_strata_detected"] > 0 for item in per_config
            ),
            "distinguishable_profiles_within_same_T0_class": root_separation_supported,
            "weighted_disintegration_signal": disintegration_supported,
            "canonical_object_reference": canonical["decision"],
        },
        "per_config": per_config,
        "notes": [
            "The consequence object is built from the canonical hybrid object, not the raw trajectory.",
            "The paper-native route is conditional pressure disintegration over packaging fibers.",
            "Direct stratumwise separation routes are retained only as rejected historical diagnostics.",
        ],
    }

    out_dir = repo_root / "results" / "hybrid_pressure_root"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    with (out_dir / "report.csv").open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            [
                "config_id",
                "persistent_packaged_strata_detected",
                "stratumwise_pressure_existence_supported",
                "root_separation_supported",
                "conditional_disintegration_supported",
            ]
        )
        for item in per_config:
            writer.writerow(
                [
                    item["config_id"],
                    item["persistent_packaged_strata_detected"],
                    item["stratumwise_pressure_existence_supported"],
                    item["root_separation_supported"],
                    item["conditional_disintegration_supported"],
                ]
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(run())
