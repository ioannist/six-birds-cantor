#!/usr/bin/env python3
from __future__ import annotations

import csv
import datetime as dt
import itertools
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEPTHS = [4, 6, 8, 10]
SPLITS = [(2, 2), (2, 3), (3, 3)]
B_MAX = 2
RETURN_CAP = 5


@dataclass(frozen=True)
class Candidate:
    family_id: str
    template_type: str
    parameter_summary: dict[str, Any]
    core_interval: tuple[float, float]
    config: dict[str, Any]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _ensure_src_path() -> None:
    src_path = _repo_root() / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))


def _map(a: float, b: float, domain: tuple[float, float], label: str) -> dict[str, Any]:
    return {
        "a": float(a),
        "b": float(b),
        "domain": [float(domain[0]), float(domain[1])],
        "label": label,
    }


def _make_local_ifs_config(
    family_id: str,
    template_type: str,
    description: str,
    maps: list[dict[str, Any]],
    core_interval: tuple[float, float],
) -> dict[str, Any]:
    slug = family_id.replace(".", "-").replace("_", "-")
    return {
        "schema_version": "1.0",
        "experiment_id": slug,
        "family_id": family_id,
        "engine": "local_ifs",
        "description": description,
        "parameters": {
            "maps": maps,
            "iterations": 8,
            "core_interval": list(core_interval),
            "template_type": template_type,
        },
        "run_controls": {"save_outputs": False, "seed": 0},
        "output_root": f"results/countable_state_witness_search/{slug}",
    }


def _candidate_templates() -> list[dict[str, Any]]:
    return [
        {
            "template_type": "ladder_gate",
            "description": "Nested ladder windows intended to create multiple return lengths before a return closes.",
        },
        {
            "template_type": "reset_and_hold",
            "description": "A buffer region can be revisited before a separate reset map returns to the core.",
        },
        {
            "template_type": "multi_return_three_map",
            "description": "Two or more return itineraries land back in the core with distinct scales or locations.",
        },
        {
            "template_type": "window_stack",
            "description": "Stacked admissibility windows designed to delay compression into a finite-state renewal model.",
        },
    ]


def _build_candidates() -> list[Candidate]:
    specs: list[dict[str, Any]] = [
        {
            "family_id": "cs.ladder_gate_a1",
            "template_type": "ladder_gate",
            "core_interval": (0.0, 0.14),
            "parameter_summary": {
                "core_interval": [0.0, 0.14],
                "layers": 2,
                "return_branch": 0.42,
            },
            "maps": [
                _map(0.39, 0.21, (0.0, 0.14), "to_wait_left"),
                _map(0.35, 0.25, (0.0, 0.14), "to_wait_right"),
                _map(0.31, 0.33, (0.18, 0.42), "ladder_hold"),
                _map(0.28, 0.45, (0.34, 0.66), "deep_hold"),
                _map(0.42, 0.00, (0.34, 0.66), "ladder_return"),
            ],
        },
        {
            "family_id": "cs.ladder_gate_a2",
            "template_type": "ladder_gate",
            "core_interval": (0.0, 0.14),
            "parameter_summary": {
                "core_interval": [0.0, 0.14],
                "layers": 2,
                "return_branch": 0.40,
            },
            "maps": [
                _map(0.40, 0.20, (0.0, 0.14), "to_wait_left"),
                _map(0.36, 0.24, (0.0, 0.14), "to_wait_right"),
                _map(0.30, 0.34, (0.18, 0.44), "ladder_hold"),
                _map(0.26, 0.48, (0.36, 0.68), "deep_hold"),
                _map(0.40, 0.00, (0.36, 0.68), "ladder_return"),
            ],
        },
        {
            "family_id": "cs.ladder_gate_a3",
            "template_type": "ladder_gate",
            "core_interval": (0.0, 0.14),
            "parameter_summary": {
                "core_interval": [0.0, 0.14],
                "layers": 3,
                "return_branch": 0.38,
            },
            "maps": [
                _map(0.38, 0.22, (0.0, 0.14), "to_wait_left"),
                _map(0.34, 0.26, (0.0, 0.14), "to_wait_right"),
                _map(0.31, 0.31, (0.18, 0.40), "ladder_hold_1"),
                _map(0.29, 0.44, (0.34, 0.60), "ladder_hold_2"),
                _map(0.27, 0.49, (0.50, 0.78), "ladder_hold_3"),
                _map(0.38, 0.00, (0.50, 0.78), "ladder_return"),
            ],
        },
        {
            "family_id": "cs.reset_hold_b1",
            "template_type": "reset_and_hold",
            "core_interval": (0.0, 0.16),
            "parameter_summary": {
                "core_interval": [0.0, 0.16],
                "holds": 2,
                "reset_scale": 0.41,
            },
            "maps": [
                _map(0.37, 0.22, (0.0, 0.16), "to_buffer"),
                _map(0.34, 0.31, (0.18, 0.48), "buffer_hold"),
                _map(0.30, 0.44, (0.34, 0.72), "deep_hold"),
                _map(0.41, 0.00, (0.34, 0.72), "reset"),
            ],
        },
        {
            "family_id": "cs.reset_hold_b2",
            "template_type": "reset_and_hold",
            "core_interval": (0.0, 0.16),
            "parameter_summary": {
                "core_interval": [0.0, 0.16],
                "holds": 2,
                "reset_scale": 0.39,
            },
            "maps": [
                _map(0.36, 0.24, (0.0, 0.16), "to_buffer"),
                _map(0.32, 0.33, (0.18, 0.44), "buffer_hold"),
                _map(0.29, 0.46, (0.38, 0.74), "deep_hold"),
                _map(0.39, 0.00, (0.38, 0.74), "reset"),
            ],
        },
        {
            "family_id": "cs.reset_hold_b3",
            "template_type": "reset_and_hold",
            "core_interval": (0.0, 0.16),
            "parameter_summary": {
                "core_interval": [0.0, 0.16],
                "holds": 3,
                "reset_scale": 0.37,
            },
            "maps": [
                _map(0.35, 0.26, (0.0, 0.16), "to_buffer"),
                _map(0.31, 0.34, (0.20, 0.46), "buffer_hold"),
                _map(0.29, 0.48, (0.40, 0.68), "deep_hold"),
                _map(0.27, 0.54, (0.54, 0.80), "deeper_hold"),
                _map(0.37, 0.00, (0.54, 0.80), "reset"),
            ],
        },
        {
            "family_id": "cs.multi_return_c1",
            "template_type": "multi_return_three_map",
            "core_interval": (0.0, 0.12),
            "parameter_summary": {
                "core_interval": [0.0, 0.12],
                "return_sites": 2,
                "dominant_reset": 0.43,
            },
            "maps": [
                _map(0.33, 0.26, (0.0, 0.12), "to_wait_upper"),
                _map(0.31, 0.34, (0.16, 0.42), "to_wait_lower"),
                _map(0.28, 0.46, (0.34, 0.72), "wait_hold"),
                _map(0.43, 0.00, (0.34, 0.72), "return"),
            ],
        },
        {
            "family_id": "cs.multi_return_c2",
            "template_type": "multi_return_three_map",
            "core_interval": (0.0, 0.12),
            "parameter_summary": {
                "core_interval": [0.0, 0.12],
                "return_sites": 2,
                "dominant_reset": 0.41,
            },
            "maps": [
                _map(0.34, 0.24, (0.0, 0.12), "to_wait_upper"),
                _map(0.30, 0.36, (0.16, 0.44), "to_wait_lower"),
                _map(0.27, 0.47, (0.32, 0.70), "wait_hold"),
                _map(0.41, 0.00, (0.32, 0.70), "return"),
            ],
        },
        {
            "family_id": "cs.window_stack_d1",
            "template_type": "window_stack",
            "core_interval": (0.0, 0.10),
            "parameter_summary": {
                "core_interval": [0.0, 0.10],
                "window_levels": 3,
                "return_scale": 0.39,
            },
            "maps": [
                _map(0.32, 0.28, (0.0, 0.10), "stage_1"),
                _map(0.30, 0.35, (0.12, 0.28), "stage_1_hold"),
                _map(0.28, 0.44, (0.24, 0.50), "stage_2"),
                _map(0.27, 0.53, (0.46, 0.72), "stage_3_hold"),
                _map(0.39, 0.00, (0.46, 0.72), "return"),
            ],
        },
        {
            "family_id": "cs.window_stack_d2",
            "template_type": "window_stack",
            "core_interval": (0.0, 0.10),
            "parameter_summary": {
                "core_interval": [0.0, 0.10],
                "window_levels": 4,
                "return_scale": 0.37,
            },
            "maps": [
                _map(0.31, 0.29, (0.0, 0.10), "stage_1"),
                _map(0.29, 0.36, (0.12, 0.26), "stage_1_hold"),
                _map(0.27, 0.45, (0.22, 0.46), "stage_2"),
                _map(0.26, 0.52, (0.42, 0.66), "stage_3"),
                _map(0.25, 0.58, (0.62, 0.82), "stage_4_hold"),
                _map(0.37, 0.00, (0.62, 0.82), "return"),
            ],
        },
    ]

    candidates: list[Candidate] = []
    for spec in specs:
        candidates.append(
            Candidate(
                family_id=spec["family_id"],
                template_type=spec["template_type"],
                parameter_summary=spec["parameter_summary"],
                core_interval=spec["core_interval"],
                config=_make_local_ifs_config(
                    family_id=spec["family_id"],
                    template_type=spec["template_type"],
                    description=f"Countable-state redesign search candidate {spec['family_id']}.",
                    maps=spec["maps"],
                    core_interval=spec["core_interval"],
                ),
            )
        )
    return candidates


def _safe_log(value: float | None) -> float | None:
    if value is None or value <= 0.0:
        return None
    return math.log(value)


def _apply_word(local_ifs, core_union, word: tuple[int, ...]):
    current = core_union
    ratio = 1.0
    for idx in word:
        local_map = local_ifs.maps[idx]
        restricted = current.intersection_interval(local_map.domain)
        if restricted.is_empty():
            return None, None
        mapped = local_map.apply_union(restricted)
        if mapped.is_empty():
            return None, None
        current = mapped
        ratio *= abs(local_map.a)
    return current, ratio


def _root_proxy(config: dict[str, Any]) -> float:
    from contextual_cantor.local_pressure import analyze_config

    analysis = analyze_config(config, DEPTHS)
    roots = [row.get("upper_root") for row in analysis["rows"] if row.get("upper_root") is not None]
    return float(roots[-1]) if roots else 1.0


def _original_diagnostics(config: dict[str, Any], s: float) -> tuple[dict[str, Any], dict[int, dict[str, Any]]]:
    from contextual_cantor.local_pressure import analyze_config, lower_partition_sum, upper_partition_sum

    analysis = analyze_config(config, DEPTHS)
    rows = analysis["rows"]
    raw_defects: list[float] = []
    normalized_defects: list[float] = []
    bridge_defects: list[float] = []
    truncation_defects: list[float] = []

    for n, m in SPLITS:
        z_n = upper_partition_sum(config, depth=n, s=s)[0]
        z_m = upper_partition_sum(config, depth=m, s=s)[0]
        z_nm = upper_partition_sum(config, depth=n + m, s=s)[0]
        logs = [_safe_log(z_n), _safe_log(z_m), _safe_log(z_nm)]
        if all(val is not None for val in logs):
            defect = abs(logs[2] - logs[0] - logs[1])  # type: ignore[operator]
            raw_defects.append(defect)
            normalized_defects.append(defect / float(n + m))

        bridge_candidates: list[float] = []
        for b in range(B_MAX + 1):
            z_bridge = upper_partition_sum(config, depth=n + m + b, s=s)[0]
            logs_bridge = [_safe_log(z_n), _safe_log(z_m), _safe_log(z_bridge)]
            if all(val is not None for val in logs_bridge):
                bridge_candidates.append(abs(logs_bridge[2] - logs_bridge[0] - logs_bridge[1]))  # type: ignore[operator]
        if bridge_candidates:
            bridge_defects.append(min(bridge_candidates))

        lower = lower_partition_sum(config, depth=n + m, s=s)
        if lower is not None and z_nm > 0:
            truncation_defects.append(1.0 - min(1.0, lower[0] / z_nm))

    depth_to_row = {row["depth"]: row for row in rows}
    last_drift = 0.0
    if len(rows) >= 2 and rows[-1].get("upper_root") is not None and rows[-2].get("upper_root") is not None:
        last_drift = abs(float(rows[-1]["upper_root"]) - float(rows[-2]["upper_root"]))

    summary = {
        "depths_checked": DEPTHS,
        "root_proxy_used": s,
        "max_normalized_qm_defect": max(normalized_defects) if normalized_defects else None,
        "max_bridge_defect": max(bridge_defects) if bridge_defects else None,
        "domain_truncation_defect": max(truncation_defects) if truncation_defects else None,
        "last_step_root_drift": last_drift,
    }
    return summary, depth_to_row


def _enumerate_first_return_blocks(candidate: Candidate, s: float) -> dict[str, Any]:
    from contextual_cantor.local_ifs import Interval, IntervalUnion, LocalIFS

    local_ifs = LocalIFS.from_dict(candidate.config["parameters"])
    core_union = IntervalUnion.from_interval(Interval(*candidate.core_interval))

    exact_mass_by_length: dict[int, float] = {}
    exact_count_by_length: dict[int, int] = {}
    cumulative_counts_by_cap: dict[str, int] = {}
    cumulative_mass_by_cap: dict[str, float] = {}
    all_words_mass_by_cap: dict[str, float] = {}
    blocks_by_cap: dict[int, list[dict[str, Any]]] = {}

    for cap in range(1, RETURN_CAP + 1):
        cap_blocks: list[dict[str, Any]] = []
        exact_mass_by_length.setdefault(cap, 0.0)
        exact_count_by_length.setdefault(cap, 0)
        all_mass = 0.0
        for length in range(1, cap + 1):
            for word in itertools.product(range(len(local_ifs.maps)), repeat=length):
                image, ratio = _apply_word(local_ifs, core_union, word)
                if image is None or ratio is None:
                    continue
                mass = ratio**s
                all_mass += mass
                if not any(iv.intersects(core_iv) for iv in image.intervals for core_iv in core_union.intervals):
                    continue
                early_return = False
                for prefix_len in range(1, length):
                    prefix_image, _ = _apply_word(local_ifs, core_union, word[:prefix_len])
                    if prefix_image is None:
                        continue
                    if any(iv.intersects(core_iv) for iv in prefix_image.intervals for core_iv in core_union.intervals):
                        early_return = True
                        break
                if early_return:
                    continue
                if length == cap:
                    exact_mass_by_length[cap] = exact_mass_by_length.get(cap, 0.0) + mass
                    exact_count_by_length[cap] = exact_count_by_length.get(cap, 0) + 1
                cap_blocks.append(
                    {
                        "word": list(word),
                        "length": length,
                        "weight_at_s": mass,
                    }
                )
        blocks_by_cap[cap] = cap_blocks
        cumulative_counts_by_cap[str(cap)] = len({tuple(block["word"]) for block in cap_blocks})
        cumulative_mass_by_cap[str(cap)] = sum(block["weight_at_s"] for block in cap_blocks)
        all_words_mass_by_cap[str(cap)] = all_mass

    exact_z_by_length = {depth: exact_mass_by_length.get(depth, 0.0) for depth in range(1, RETURN_CAP + 1)}
    lengths = [depth for depth, value in exact_z_by_length.items() if value > 0.0]
    counts = [exact_count_by_length.get(depth, 0) for depth in range(1, RETURN_CAP + 1)]
    last_count = counts[-1] if counts else 0
    prev_count = counts[-2] if len(counts) >= 2 else last_count
    max_length = max(lengths) if lengths else None

    def _z(depth: int) -> float:
        return exact_z_by_length.get(depth, 0.0)

    raw_defects: list[float] = []
    normalized_defects: list[float] = []
    bridge_defects: list[float] = []
    for n, m in SPLITS:
        z_n = _z(n)
        z_m = _z(m)
        z_nm = _z(n + m) if (n + m) <= RETURN_CAP else 0.0
        logs = [_safe_log(z_n), _safe_log(z_m), _safe_log(z_nm)]
        if all(val is not None for val in logs):
            defect = abs(logs[2] - logs[0] - logs[1])  # type: ignore[operator]
            raw_defects.append(defect)
            normalized_defects.append(defect / float(n + m))
        bridge_candidates: list[float] = []
        for b in range(B_MAX + 1):
            d = n + m + b
            if d > RETURN_CAP:
                continue
            z_bridge = _z(d)
            logs_bridge = [_safe_log(z_n), _safe_log(z_m), _safe_log(z_bridge)]
            if all(val is not None for val in logs_bridge):
                bridge_candidates.append(abs(logs_bridge[2] - logs_bridge[0] - logs_bridge[1]))  # type: ignore[operator]
        if bridge_candidates:
            bridge_defects.append(min(bridge_candidates))

    all_mass = float(all_words_mass_by_cap[str(RETURN_CAP)])
    return_mass = float(cumulative_mass_by_cap[str(RETURN_CAP)])
    induced_truncation = None if all_mass <= 0.0 else 1.0 - min(1.0, return_mass / all_mass)

    if not lengths:
        return_time_regime = "unknown"
    elif len(lengths) == 1:
        return_time_regime = "bounded_constant"
    elif max_length is not None and max_length < RETURN_CAP:
        return_time_regime = "bounded_nonconstant"
    elif last_count > prev_count:
        return_time_regime = "growing_but_tight"
    else:
        return_time_regime = "unbounded_candidate"

    latest_count = counts[-1] if counts else 0
    if latest_count == 0:
        effective_alphabet_regime = "unknown"
    elif latest_count == 1:
        effective_alphabet_regime = "size_1"
    elif latest_count <= 3 and latest_count == prev_count:
        effective_alphabet_regime = "finite_small"
    elif latest_count <= 8 and latest_count == prev_count:
        effective_alphabet_regime = "finite_large"
    elif latest_count > prev_count:
        effective_alphabet_regime = "countable_candidate"
    else:
        effective_alphabet_regime = "finite_state_renewal_like"

    if latest_count <= 1:
        induced_core_type = "trivial_finite_state"
    elif max_length is not None and max_length < RETURN_CAP and latest_count <= 3 and len(lengths) <= 2:
        induced_core_type = "finite_state"
    elif max_length is not None and max_length < RETURN_CAP and len(lengths) >= 2 and latest_count <= 5:
        induced_core_type = "finite_state_renewal_like"
    elif max_length == RETURN_CAP and len(lengths) >= 4 and latest_count >= 4 and last_count > prev_count:
        induced_core_type = "countable_state_candidate"
    elif induced_truncation is not None and induced_truncation > 0.95:
        induced_core_type = "pathological"
    else:
        induced_core_type = "finite_state_renewal_like"

    return {
        "exact_z_by_length": exact_z_by_length,
        "exact_count_by_length": exact_count_by_length,
        "return_blocks_by_cap": blocks_by_cap,
        "cumulative_counts_by_cap": cumulative_counts_by_cap,
        "cumulative_mass_by_cap": cumulative_mass_by_cap,
        "all_words_mass_by_cap": all_words_mass_by_cap,
        "induced_max_normalized_qm_defect": max(normalized_defects) if normalized_defects else None,
        "induced_max_bridge_defect": max(bridge_defects) if bridge_defects else None,
        "induced_truncation_defect": induced_truncation,
        "induced_core_type": induced_core_type,
        "return_time_regime": return_time_regime,
        "effective_alphabet_regime": effective_alphabet_regime,
        "observed_return_lengths": lengths,
        "counts_by_length": counts,
    }


def _compression_diagnostics(induced: dict[str, Any]) -> dict[str, Any]:
    core_type = induced["induced_core_type"]
    lengths = induced["observed_return_lengths"]
    counts_by_cap = induced["cumulative_counts_by_cap"]
    latest_count = int(counts_by_cap[str(RETURN_CAP)])
    prev_count = int(counts_by_cap[str(RETURN_CAP - 1)]) if RETURN_CAP > 1 else latest_count

    if core_type == "trivial_finite_state":
        result = "trivial_collapse"
        note = "Induced coding collapses to a single recurrent symbol."
    elif core_type in {"finite_state", "finite_state_renewal_like"}:
        result = "finite_state_renewal_like_compression"
        note = "Compression into a small renewal-like model remains plausible on the checked cap."
    elif core_type == "countable_state_candidate":
        result = "no_small_finite_state_compression_detected"
        note = "Return lengths and alphabet growth keep expanding on the checked cap."
    elif core_type == "pathological":
        result = "pathological_or_too_lossey"
        note = "The induced structure is too lossy to support a credible compression claim."
    else:
        result = "unclear"
        note = "The current cap is not enough to settle compression one way or the other."

    return {
        "attempted_method": "return_signature_folding",
        "result": result,
        "signature_count_by_cap": counts_by_cap,
        "latest_signature_count": latest_count,
        "previous_signature_count": prev_count,
        "note": note,
        "supports_countable_state_candidate": core_type == "countable_state_candidate",
    }


def _frontier_status(original: dict[str, Any], induced: dict[str, Any], compression: dict[str, Any]) -> tuple[str, str]:
    core_type = induced["induced_core_type"]
    trunc = induced["induced_truncation_defect"]
    orig_qm = original["max_normalized_qm_defect"]
    orig_bridge = original["max_bridge_defect"]
    return_regime = induced["return_time_regime"]

    if core_type in {"trivial_finite_state", "pathological"}:
        return "blocked", "Induced coding collapses or becomes too lossy on the checked cap."

    if core_type == "countable_state_candidate" and trunc is not None and trunc <= 0.93 and return_regime in {"growing_but_tight", "unbounded_candidate"}:
        return "promising", "Induced coding retains growing return blocks and does not compress to a small finite-state renewal model on the checked cap."

    if core_type in {"finite_state_renewal_like", "finite_state"} and trunc is not None and trunc <= 0.9 and orig_qm is not None and orig_bridge is not None and orig_qm <= 0.42 and orig_bridge <= 1.8:
        return "inconclusive", "The candidate improves on trivial collapse but still looks finite-state-renewal-like on the checked cap."

    if core_type == "countable_state_candidate":
        return "inconclusive", "The candidate shows countable-state flavor, but truncation or direct-code defects are still too high for a clean next target."

    return "blocked", "The candidate does not beat the finite-state-renewal baseline enough to justify a new branch."


def _rank_key(entry: dict[str, Any]) -> tuple[int, float, int, float]:
    status_rank = {"promising": 0, "inconclusive": 1, "blocked": 2}
    core_rank = {
        "countable_state_candidate": 0,
        "finite_state_renewal_like": 1,
        "finite_state": 2,
        "trivial_finite_state": 3,
        "pathological": 4,
    }
    trunc = entry["induced_diagnostics"]["induced_truncation_defect"]
    orig_qm = entry["original_diagnostics"]["max_normalized_qm_defect"]
    return (
        status_rank.get(entry["frontier_status"], 9),
        1.0 if trunc is None else trunc,
        core_rank.get(entry["induced_core_type"], 9),
        1.0 if orig_qm is None else orig_qm,
    )


def main() -> int:
    _ensure_src_path()
    repo_root = _repo_root()

    out_dir = repo_root / "results" / "countable_state_witness_search"
    out_dir.mkdir(parents=True, exist_ok=True)

    candidate_entries: list[dict[str, Any]] = []
    csv_rows: list[dict[str, Any]] = []
    for candidate in _build_candidates():
        root_proxy = _root_proxy(candidate.config)
        original, _ = _original_diagnostics(candidate.config, root_proxy)
        induced = _enumerate_first_return_blocks(candidate, root_proxy)
        compression = _compression_diagnostics(induced)
        frontier_status, note = _frontier_status(original, induced, compression)

        entry = {
            "family_id": candidate.family_id,
            "template_type": candidate.template_type,
            "parameter_summary": candidate.parameter_summary,
            "original_diagnostics": original,
            "induced_diagnostics": {
                "root_proxy_used": root_proxy,
                "induced_max_normalized_qm_defect": induced["induced_max_normalized_qm_defect"],
                "induced_max_bridge_defect": induced["induced_max_bridge_defect"],
                "induced_truncation_defect": induced["induced_truncation_defect"],
                "return_time_support_summary": {
                    "observed_return_lengths": induced["observed_return_lengths"],
                    "return_time_regime": induced["return_time_regime"],
                    "count_by_length": induced["counts_by_length"],
                },
                "induced_alphabet_growth_summary": {
                    "count_by_cap": induced["cumulative_counts_by_cap"],
                    "mass_by_cap": induced["cumulative_mass_by_cap"],
                    "growth_regime": induced["effective_alphabet_regime"],
                },
            },
            "compression_diagnostics": compression,
            "induced_core_type": induced["induced_core_type"],
            "return_time_regime": induced["return_time_regime"],
            "effective_alphabet_regime": induced["effective_alphabet_regime"],
            "frontier_status": frontier_status,
            "classification_note": note,
            "artifact_paths": ["results/countable_state_witness_search/report.json"],
        }
        candidate_entries.append(entry)
        csv_rows.append(
            {
                "family_id": candidate.family_id,
                "template_type": candidate.template_type,
                "frontier_status": frontier_status,
                "induced_core_type": induced["induced_core_type"],
                "return_time_regime": induced["return_time_regime"],
                "effective_alphabet_regime": induced["effective_alphabet_regime"],
                "original_max_normalized_qm_defect": original["max_normalized_qm_defect"],
                "original_max_bridge_defect": original["max_bridge_defect"],
                "domain_truncation_defect": original["domain_truncation_defect"],
                "induced_truncation_defect": induced["induced_truncation_defect"],
            }
        )

    ranked = sorted(candidate_entries, key=_rank_key)
    top_candidates = ranked[:3]

    promising = [entry for entry in candidate_entries if entry["frontier_status"] == "promising"]
    countable_promising = [entry for entry in promising if entry["induced_core_type"] == "countable_state_candidate"]
    finite_like_promising = [
        entry
        for entry in promising
        if entry["induced_core_type"] in {"finite_state", "finite_state_renewal_like"}
    ]

    if countable_promising:
        decision = "promising_countable_state_candidate_found"
        next_branch = "CS-T2 — Formalize the countable-state frontier target class"
    elif finite_like_promising:
        decision = "only_finite_state_like_candidates_found"
        next_branch = "CS-T2a — Decide whether to settle for renewal novelty or redesign again"
    else:
        decision = "design_space_blocked"
        next_branch = "CS-alt — Import an external local-domain/countable-state witness family"

    report = {
        "schema_version": "1.0",
        "search_id": "countable-state-witness-search-v1",
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
        "candidate_templates": _candidate_templates(),
        "candidate_families": candidate_entries,
        "decision": decision,
        "top_candidates": [entry["family_id"] for entry in top_candidates],
        "notes": [
            "The search uses stationary deterministic local-domain local-IFS families.",
            "The target is to beat the delayed-return theorem branch, which closed but still looked finite-state renewal-like.",
            "A promising result requires more than a size-1 or tiny finite-state induced collapse.",
        ],
    }

    report_path = out_dir / "report.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    csv_path = out_dir / "report.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "family_id",
                "template_type",
                "frontier_status",
                "induced_core_type",
                "return_time_regime",
                "effective_alphabet_regime",
                "original_max_normalized_qm_defect",
                "original_max_bridge_defect",
                "domain_truncation_defect",
                "induced_truncation_defect",
            ],
        )
        writer.writeheader()
        writer.writerows(csv_rows)

    shortlist = {
        "schema_version": "1.0",
        "shortlist_id": "countable-state-redesign-shortlist-v1",
        "generated_at_utc": report["generated_at_utc"],
        "decision": decision,
        "top_candidates": [
            {
                "family_id": entry["family_id"],
                "template_type": entry["template_type"],
                "frontier_status": entry["frontier_status"],
                "induced_core_type": entry["induced_core_type"],
                "return_time_regime": entry["return_time_regime"],
                "effective_alphabet_regime": entry["effective_alphabet_regime"],
                "compression_status": entry["compression_diagnostics"]["result"],
                "why_selected": entry["classification_note"],
            }
            for entry in top_candidates
        ],
        "rejected_candidates": [entry["family_id"] for entry in ranked[3:]],
        "selection_rule": "Prefer candidates that retain nonconstant return structure and avoid immediate finite-state collapse while keeping truncation and original defects tolerable.",
        "next_branch": next_branch,
    }
    shortlist_path = repo_root / "docs" / "internal" / "countable_state_redesign_shortlist_v1.json"
    shortlist_path.write_text(json.dumps(shortlist, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    note_lines = [
        "# Countable-State Redesign Search v1",
        "",
        "## Question",
        "Can a new stationary local-domain witness family beat the delayed-return branch, meaning: avoid finite-state-renewal collapse and keep induced return structure genuinely expanding?",
        "",
        "## Templates searched",
        "- Template A: ladder-gate families with nested waiting windows and multiple return branches.",
        "- Template B: reset-and-hold families with a buffer region and a distinct reset map.",
        "- Template C: multi-return three-map families with two return itineraries back to the core.",
        "- Template D: stacked window families with several admissibility windows before return.",
        "",
        "## Best candidates",
    ]
    for entry in top_candidates:
        note_lines.append(
            f"- `{entry['family_id']}` ({entry['template_type']}): `{entry['frontier_status']}`; induced core `{entry['induced_core_type']}`, return regime `{entry['return_time_regime']}`, alphabet regime `{entry['effective_alphabet_regime']}`."
        )
    note_lines.extend(
        [
            "",
            "## Why the delayed-return witnesses are no longer enough",
            "- They closed as a theorem package, but the audit said they still looked finite-state renewal-like.",
            "- The new search must therefore look for induced return structure that does not collapse so quickly.",
            "",
            "## Decision",
            f"- `{decision}`",
            "",
            "## What kind of theorem branch this supports next",
        ]
    )
    if decision == "promising_countable_state_candidate_found":
        note_lines.extend(
            [
                "- The search found at least one candidate that retains a nontrivial, growing induced return alphabet and does not compress to a small renewal model on the checked cap.",
                "- That supports a genuine countable-state / induced theorem branch, subject to later formalization.",
            ]
        )
    elif decision == "only_finite_state_like_candidates_found":
        note_lines.extend(
            [
                "- The best candidates improve on the delayed-return branch, but they still look finite-state-renewal-like rather than genuinely countable-state.",
                "- The next theorem branch would be renewal novelty, not a countable-state frontier theorem.",
            ]
        )
    else:
        note_lines.extend(
            [
                "- The small template language did not produce a credible next witness.",
                "- A different family language or an imported external witness family is needed before more theorem work.",
            ]
        )
    note_lines.extend(
        [
            "",
            "The main distinction is whether the induced coding keeps growing in a way that resists finite-state compression on the checked cap.",
        ]
    )
    note_path = repo_root / "docs" / "internal" / "countable_state_redesign_search_v1.md"
    note_path.write_text("\n".join(note_lines) + "\n", encoding="utf-8")

    print(f"wrote {report_path}")
    print(f"decision={decision}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
