from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from .feedback_contextual import run_feedback_family
from .finite_state_symbolic import admissible_word_count, partition_sum
from .local_ifs import Interval, IntervalUnion, LocalIFS, iterate_set


def _intervals_from_words(base: int, words: list[list[int]]) -> IntervalUnion:
    if not words:
        return IntervalUnion()
    depth = len(words[0])
    scale = float(base) ** depth
    width = 1.0 / scale
    intervals: list[Interval] = []
    for word in words:
        offset = 0.0
        for i, digit in enumerate(word, start=1):
            offset += float(digit) / (float(base) ** i)
        intervals.append(Interval(offset, offset + width))
    return IntervalUnion(intervals)


def _generate_classical_words(allowed_digits: list[int], depth: int) -> list[list[int]]:
    words = [[]]
    for _ in range(depth):
        nxt: list[list[int]] = []
        for word in words:
            for d in allowed_digits:
                nxt.append(word + [d])
        words = nxt
    return words


def _generate_prefix_words(start_digits: list[int], transitions: dict[str, list[int]], depth: int) -> list[list[int]]:
    if depth <= 0:
        return [[]]
    words = [[d] for d in start_digits]
    for _ in range(1, depth):
        nxt: list[list[int]] = []
        for word in words:
            for d in transitions[str(word[-1])]:
                nxt.append(word + [d])
        words = nxt
    return words


def _generate_stage_words(stage_digit_sets: list[list[int]], depth: int) -> list[list[int]]:
    words = [[]]
    for stage in range(depth):
        choices = stage_digit_sets[stage % len(stage_digit_sets)]
        nxt: list[list[int]] = []
        for word in words:
            for d in choices:
                nxt.append(word + [d])
        words = nxt
    return words


def _local_ifs_branches_by_depth(local_ifs: LocalIFS, max_depth: int) -> dict[int, list[float]]:
    current: list[tuple[IntervalUnion, float]] = [(IntervalUnion.from_interval(Interval(0.0, 1.0)), 1.0)]
    out: dict[int, list[float]] = {0: [1.0]}
    for depth in range(1, max_depth + 1):
        nxt: list[tuple[IntervalUnion, float]] = []
        for union, ratio_product in current:
            for local_map in local_ifs.maps:
                restricted = union.intersection_interval(local_map.domain)
                if restricted.is_empty():
                    continue
                mapped = local_map.apply_union(restricted)
                if mapped.is_empty():
                    continue
                nxt.append((mapped, ratio_product * abs(local_map.a)))
        current = nxt
        out[depth] = [p for _, p in current]
    return out


def _find_root_bisection(
    func,
    s_min: float,
    s_max: float,
    tol: float = 1e-10,
    max_iter: int = 256,
) -> float | None:
    f_lo = func(s_min)
    f_hi = func(s_max)
    if abs(f_lo) <= tol:
        return s_min
    if abs(f_hi) <= tol:
        return s_max
    if f_lo * f_hi > 0.0:
        return None
    lo, hi = s_min, s_max
    for _ in range(max_iter):
        mid = 0.5 * (lo + hi)
        f_mid = func(mid)
        if abs(f_mid) <= tol or (hi - lo) <= tol:
            return mid
        if f_lo * f_mid <= 0.0:
            hi = mid
        else:
            lo = mid
            f_lo = f_mid
    return 0.5 * (lo + hi)


def _build_feedback_depth_data(config: dict[str, Any], max_depth: int) -> dict[int, dict[str, Any]]:
    if max_depth <= 0:
        return {}
    result = run_feedback_family(config, steps=max_depth)
    trace_rows = result.get("trace_rows", [])
    snapshots = result.get("stage_snapshots", [])
    out: dict[int, dict[str, Any]] = {}
    for idx, row in enumerate(trace_rows, start=1):
        raw_intervals: list[Interval] = []
        packaged_intervals: list[Interval] = []
        if idx - 1 < len(snapshots):
            snap = snapshots[idx - 1]
            raw_intervals = list(snap.get("raw_intervals", []))
            packaged_intervals = list(snap.get("packaged_intervals", []))
        out[idx] = {
            "raw_intervals": raw_intervals,
            "packaged_intervals": packaged_intervals,
            "protocol_state": row.protocol_state_after,
            "gating_state": row.gating_state_after,
            "lens_mode": row.lens_mode_after,
            "packaging_mode": row.packaging_mode_after,
            "triggered_cells": row.triggered_cells,
            "branch_count_raw": row.raw_interval_count,
            "interval_count_packaged": row.packaged_interval_count,
        }
    return out


def _get_feedback_depth_info(
    config: dict[str, Any],
    depth: int,
    context: dict[str, Any] | None,
) -> dict[str, Any] | None:
    family_id = str(config.get("family_id", ""))
    engine = str(config.get("engine", ""))
    if engine != "contextual_feedback" or not family_id.startswith("contextual_local.feedback"):
        return None
    if context and isinstance(context.get("feedback_depth_data"), dict):
        return context["feedback_depth_data"].get(depth)
    return _build_feedback_depth_data(config, depth).get(depth)


def upper_partition_sum(
    config: dict[str, Any],
    depth: int,
    s: float,
    context: dict[str, Any] | None = None,
) -> tuple[float, int]:
    engine = str(config["engine"])
    params = config["parameters"]
    family_id = str(config["family_id"])

    feedback_info = _get_feedback_depth_info(config, depth, context)
    if feedback_info is not None:
        raw_intervals = feedback_info["raw_intervals"]
        z = sum((iv.length**s) for iv in raw_intervals)
        return z, int(feedback_info.get("branch_count_raw", len(raw_intervals)))

    if engine == "classical_similarity":
        base = int(params["base"])
        digits = [int(d) for d in params["allowed_digits"]]
        count = len(digits) ** depth
        z = float(count) * ((1.0 / base) ** (depth * s))
        return z, count

    if engine == "finite_state_symbolic" and "edges" in params:
        edges = params["edges"]
        start_states = params.get("start_states")
        z = partition_sum(edges=edges, depth=depth, s=s, start_states=start_states)
        count = admissible_word_count(edges=edges, depth=depth, start_states=start_states)
        return z, count

    if family_id.startswith("contextual_local.prefix_memory"):
        base = int(params["base"])
        start_digits = [int(d) for d in params["start_digits"]]
        transitions = {k: [int(v) for v in vals] for k, vals in params["transition_digits"].items()}
        words = _generate_prefix_words(start_digits, transitions, depth)
        count = len(words)
        z = float(count) * ((1.0 / base) ** (depth * s))
        return z, count

    if engine == "nonautonomous_symbolic" and "stage_digit_sets" in params:
        base = int(params["base"])
        stage_digit_sets = [[int(d) for d in ds] for ds in params["stage_digit_sets"]]
        words = _generate_stage_words(stage_digit_sets, depth)
        count = len(words)
        z = float(count) * ((1.0 / base) ** (depth * s))
        return z, count

    if engine == "local_ifs" and "maps" in params:
        local_ifs = LocalIFS.from_dict(params)
        branch_products = _local_ifs_branches_by_depth(local_ifs, depth).get(depth, [])
        z = sum((r**s) for r in branch_products)
        return z, len(branch_products)

    raise ValueError(f"unsupported config for upper partition sum: engine={engine} family={family_id}")


def lower_partition_sum(
    config: dict[str, Any],
    depth: int,
    s: float,
    context: dict[str, Any] | None = None,
) -> tuple[float, int] | None:
    engine = str(config["engine"])
    params = config["parameters"]
    family_id = str(config["family_id"])

    feedback_info = _get_feedback_depth_info(config, depth, context)
    if feedback_info is not None:
        packaged_intervals = feedback_info["packaged_intervals"]
        z = sum((iv.length**s) for iv in packaged_intervals)
        return z, int(feedback_info.get("interval_count_packaged", len(packaged_intervals)))

    if depth <= 0:
        union = IntervalUnion.from_interval(Interval(0.0, 1.0))
        return sum(iv.length**s for iv in union.intervals), len(union.intervals)

    if engine == "classical_similarity":
        base = int(params["base"])
        digits = [int(d) for d in params["allowed_digits"]]
        words = _generate_classical_words(digits, depth)
        union = _intervals_from_words(base, words)
        return sum(iv.length**s for iv in union.intervals), len(union.intervals)

    if family_id.startswith("contextual_local.prefix_memory"):
        base = int(params["base"])
        start_digits = [int(d) for d in params["start_digits"]]
        transitions = {k: [int(v) for v in vals] for k, vals in params["transition_digits"].items()}
        words = _generate_prefix_words(start_digits, transitions, depth)
        union = _intervals_from_words(base, words)
        return sum(iv.length**s for iv in union.intervals), len(union.intervals)

    if engine == "nonautonomous_symbolic" and "stage_digit_sets" in params:
        base = int(params["base"])
        stage_digit_sets = [[int(d) for d in ds] for ds in params["stage_digit_sets"]]
        words = _generate_stage_words(stage_digit_sets, depth)
        union = _intervals_from_words(base, words)
        return sum(iv.length**s for iv in union.intervals), len(union.intervals)

    if engine == "local_ifs" and "maps" in params:
        local_ifs = LocalIFS.from_dict(params)
        seq = iterate_set(local_ifs, steps=depth)
        union = seq[-1]
        return sum(iv.length**s for iv in union.intervals), len(union.intervals)

    return None


def pressure_curve(
    config: dict[str, Any],
    depth: int,
    s_values: list[float],
    context: dict[str, Any] | None = None,
) -> list[dict[str, float | None]]:
    rows: list[dict[str, float | None]] = []
    for s in s_values:
        upper_z, _ = upper_partition_sum(config, depth=depth, s=s, context=context)
        upper_p = (1.0 / depth) * math.log(upper_z) if depth > 0 and upper_z > 0 else None
        lower = lower_partition_sum(config, depth=depth, s=s, context=context)
        lower_p = None
        if lower is not None and depth > 0 and lower[0] > 0:
            lower_p = (1.0 / depth) * math.log(lower[0])
        rows.append({"s": s, "upper_pressure": upper_p, "lower_pressure": lower_p})
    return rows


def root_bracket_by_depth(
    config: dict[str, Any],
    depth: int,
    s_min: float = 0.0,
    s_max: float = 2.0,
    tol: float = 1e-10,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    upper_root = _find_root_bisection(
        lambda s: upper_partition_sum(config, depth=depth, s=s, context=context)[0] - 1.0,
        s_min=s_min,
        s_max=s_max,
        tol=tol,
    )
    lower_root: float | None = None
    if lower_partition_sum(config, depth=depth, s=s_min, context=context) is not None:
        lower_root = _find_root_bisection(
            lambda s: lower_partition_sum(config, depth=depth, s=s, context=context)[0] - 1.0,  # type: ignore[index]
            s_min=s_min,
            s_max=s_max,
            tol=tol,
        )

    upper_pressure_at_root = None
    if upper_root is not None and depth > 0:
        z_u, _ = upper_partition_sum(config, depth=depth, s=upper_root, context=context)
        if z_u > 0:
            upper_pressure_at_root = math.log(z_u) / depth

    lower_pressure_at_root = None
    if lower_root is not None and depth > 0:
        lower = lower_partition_sum(config, depth=depth, s=lower_root, context=context)
        if lower is not None and lower[0] > 0:
            lower_pressure_at_root = math.log(lower[0]) / depth

    branch_count_raw = upper_partition_sum(config, depth=depth, s=0.0, context=context)[1]
    lower0 = lower_partition_sum(config, depth=depth, s=0.0, context=context)
    interval_count_packaged = None if lower0 is None else lower0[1]
    width = None
    if upper_root is not None and lower_root is not None:
        width = upper_root - lower_root

    feedback_info = _get_feedback_depth_info(config, depth, context)
    protocol_state = None
    gating_state = None
    lens_mode = None
    packaging_mode = None
    triggered_cells = ""
    if feedback_info is not None:
        protocol_state = feedback_info.get("protocol_state")
        gating_state = feedback_info.get("gating_state")
        lens_mode = feedback_info.get("lens_mode")
        packaging_mode = feedback_info.get("packaging_mode")
        triggered_cells = str(feedback_info.get("triggered_cells", ""))

    return {
        "depth": depth,
        "upper_root": upper_root,
        "lower_root": lower_root,
        "interval_root_width": width,
        "upper_pressure_at_upper_root": upper_pressure_at_root,
        "lower_pressure_at_lower_root": lower_pressure_at_root,
        "branch_count_raw": branch_count_raw,
        "interval_count_packaged": interval_count_packaged,
        "branch_count": branch_count_raw,
        "interval_count": interval_count_packaged,
        "protocol_state": protocol_state,
        "gating_state": gating_state,
        "lens_mode": lens_mode,
        "packaging_mode": packaging_mode,
        "triggered_cells": triggered_cells,
    }


def _build_analysis_context(config: dict[str, Any], max_depth: int) -> dict[str, Any]:
    context: dict[str, Any] = {}
    engine = str(config.get("engine", ""))
    family_id = str(config.get("family_id", ""))
    if engine == "contextual_feedback" and family_id.startswith("contextual_local.feedback"):
        context["feedback_depth_data"] = _build_feedback_depth_data(config, max_depth)
    return context


def analyze_config(
    config: dict[str, Any],
    depths: list[int],
    s_min: float = 0.0,
    s_max: float = 2.0,
    tol: float = 1e-10,
) -> dict[str, Any]:
    unique_depths = sorted(set(int(d) for d in depths if int(d) > 0))
    if not unique_depths:
        raise ValueError("depths must contain positive integers")
    context = _build_analysis_context(config, max(unique_depths))
    rows = [
        root_bracket_by_depth(config=config, depth=d, s_min=s_min, s_max=s_max, tol=tol, context=context)
        for d in unique_depths
    ]
    return {
        "family_id": config["family_id"],
        "engine": config["engine"],
        "depths": unique_depths,
        "rows": rows,
    }


def default_depths_from_config(config: dict[str, Any]) -> list[int]:
    params = config.get("parameters", {})
    if isinstance(params, dict):
        if isinstance(params.get("depth_list"), list):
            vals = [int(v) for v in params["depth_list"] if int(v) > 0]
            if vals:
                return vals
        if "snapshot_depth" in params:
            d = int(params["snapshot_depth"])
            return [max(2, d - 4), max(2, d - 2), d]
        if "max_depth" in params:
            d = int(params["max_depth"])
            return [max(2, d - 4), max(2, d - 2), d]
        if "iterations" in params:
            d = int(params["iterations"])
            return [max(2, d - 4), max(2, d - 2), d]
        if "steps" in params:
            d = int(params["steps"])
            if str(config.get("engine", "")) == "contextual_feedback":
                return sorted({1, 2, max(3, d - 2), d})
            return [max(2, d - 4), max(2, d - 2), d]
    return [2, 4, 6, 8, 10]


def load_config(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("config JSON must be an object")
    return data
