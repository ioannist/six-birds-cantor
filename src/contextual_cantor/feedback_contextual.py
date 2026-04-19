from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .local_ifs import Interval, IntervalUnion


LENS_MODES = {"raw_cylinders", "coalesced_intervals", "prefix_sectors"}
PACKAGING_MODES = {"identity", "merge_touching", "budget_capped_merge"}


@dataclass(frozen=True)
class StageTraceRow:
    stage: int
    protocol_state_before: str
    protocol_state_after: str
    lens_mode_before: str
    lens_mode_after: str
    packaging_mode_before: str
    packaging_mode_after: str
    observed_metric_name: str
    observed_metric_value: float
    decision_rule: str
    triggered_cells: str
    gating_state_before: str
    gating_state_after: str
    gating_rule: str
    lens_metric_threshold: float
    p2_from_p4_fired: int
    p2_from_p6_fired: int
    p5_from_p4_fired: int
    p5_from_p6_fired: int
    raw_interval_count: int
    packaged_interval_count: int
    total_length_before_packaging: float
    total_length_after_packaging: float


def _digit_step(intervals: list[Interval], base: int, digits: list[int]) -> list[Interval]:
    out: list[Interval] = []
    for iv in intervals:
        for d in digits:
            out.append(Interval((iv.left + d) / base, (iv.right + d) / base))
    return out


def _merge_to_cap(merged: list[Interval], cap: int) -> list[Interval]:
    if cap <= 0:
        return []
    current = list(merged)
    while len(current) > cap:
        min_gap = float("inf")
        idx = 0
        for i in range(len(current) - 1):
            gap = current[i + 1].left - current[i].right
            if gap < min_gap:
                min_gap = gap
                idx = i
        combined = Interval(current[idx].left, current[idx + 1].right)
        current = current[:idx] + [combined] + current[idx + 2 :]
    return current


def apply_packaging_mode(intervals: list[Interval], packaging_mode: str, config: dict[str, Any]) -> list[Interval]:
    if packaging_mode not in PACKAGING_MODES:
        raise ValueError(f"unsupported packaging_mode: {packaging_mode}")
    if packaging_mode == "identity":
        # Keep the raw stage pieces exactly as generated.
        return list(intervals)
    merged = IntervalUnion(intervals).intervals
    if packaging_mode == "merge_touching":
        return merged
    cap = int(config.get("budget_interval_cap", 2))
    return _merge_to_cap(merged, cap)


def compute_lens_observation(
    lens_mode: str,
    raw_intervals: list[Interval],
    packaged_intervals: list[Interval],
    config: dict[str, Any],
) -> tuple[str, float]:
    if lens_mode not in LENS_MODES:
        raise ValueError(f"unsupported lens_mode: {lens_mode}")
    if lens_mode == "raw_cylinders":
        return "raw_interval_count", float(len(raw_intervals))
    if lens_mode == "coalesced_intervals":
        return "coalesced_interval_count", float(len(IntervalUnion(packaged_intervals).intervals))

    sectors = int(config.get("prefix_sector_count", 4))
    if sectors <= 0:
        sectors = 4
    occupied = 0
    sector_width = 1.0 / sectors
    union = IntervalUnion(packaged_intervals)
    for k in range(sectors):
        sector = Interval(k * sector_width, (k + 1) * sector_width)
        if not union.intersection_interval(sector).is_empty():
            occupied += 1
    return "occupied_prefix_sectors", float(occupied)


def update_protocol_state(
    protocol_state: str,
    observed_metric_name: str,
    observed_metric_value: float,
    config: dict[str, Any],
) -> tuple[str, str]:
    family_kind = str(config.get("family_kind", ""))
    if family_kind == "lens_protocol_coupled":
        to_strict = float(config.get("strict_threshold", 2.0))
        to_loose = float(config.get("loose_threshold", 1.0))
        if protocol_state == "loose" and observed_metric_value >= to_strict:
            return "strict", "lens_threshold_to_strict"
        if protocol_state == "strict" and observed_metric_value <= to_loose:
            return "loose", "lens_threshold_to_loose"
        return protocol_state, "no_change"
    return protocol_state, "no_change"


def update_gating_state_from_lens(
    gating_state: str,
    observed_metric_value: float,
    config: dict[str, Any],
) -> tuple[str, str, float, int]:
    strict_threshold = float(config.get("lens_gating_strict_threshold", 2.0))
    relax_threshold = float(config.get("lens_gating_relax_threshold", 1.0))
    next_state = gating_state
    rule = "no_change"
    if gating_state == "permissive" and observed_metric_value > strict_threshold:
        next_state = "strict"
        rule = "lens_threshold_to_strict"
    elif gating_state == "strict" and observed_metric_value <= relax_threshold:
        next_state = "permissive"
        rule = "lens_threshold_to_loose"
    fired = 1 if next_state != gating_state else 0
    threshold_used = strict_threshold if rule == "lens_threshold_to_strict" else relax_threshold
    return next_state, rule, threshold_used, fired


def update_gating_state_from_budget(
    gating_state: str,
    budget_metric_value: float,
    config: dict[str, Any],
) -> tuple[str, str, float, int]:
    budget_cap = float(config.get("budget_cap_metric", 2.0))
    if budget_metric_value > budget_cap:
        next_state = "strict"
        rule = "budget_cap_exceeded"
    else:
        next_state = "permissive"
        rule = "budget_cap_not_exceeded"
    fired = 1 if next_state != gating_state else 0
    return next_state, rule, budget_cap, fired


def update_lens_mode(current_lens_mode: str, protocol_state: str, config: dict[str, Any]) -> tuple[str, str]:
    family_kind = str(config.get("family_kind", ""))
    if family_kind != "lens_protocol_coupled":
        return current_lens_mode, "no_change"
    mapping = config.get(
        "lens_by_protocol",
        {"loose": "prefix_sectors", "strict": "coalesced_intervals"},
    )
    if not isinstance(mapping, dict):
        return current_lens_mode, "no_change"
    nxt = mapping.get(protocol_state, current_lens_mode)
    if isinstance(nxt, str) and nxt in LENS_MODES and nxt != current_lens_mode:
        return nxt, "protocol_to_lens_switch"
    return current_lens_mode, "no_change"


def update_packaging_mode(current_packaging_mode: str, protocol_state: str, config: dict[str, Any]) -> tuple[str, str]:
    # Backward-compatible shim kept for callers that still expect this symbol.
    return current_packaging_mode, "no_change"


def update_packaging_mode_from_lens(
    current_packaging_mode: str,
    lens_mode: str,
    observed_metric_value: float,
    config: dict[str, Any],
) -> tuple[str, str, int]:
    if str(config.get("family_kind", "")) != "lens_protocol_coupled":
        return current_packaging_mode, "no_change", 0
    mapping = config.get(
        "packaging_by_lens_mode",
        {
            "prefix_sectors": "identity",
            "coalesced_intervals": "merge_touching",
            "raw_cylinders": "identity",
        },
    )
    threshold = float(config.get("lens_packaging_identity_threshold", -1.0))
    nxt = current_packaging_mode
    rule = "no_change"
    if isinstance(mapping, dict):
        candidate = mapping.get(lens_mode)
        if isinstance(candidate, str) and candidate in PACKAGING_MODES:
            nxt = candidate
            rule = "lens_mode_to_packaging"
    if observed_metric_value >= threshold >= 0.0 and nxt != "identity":
        nxt = "identity"
        rule = "lens_metric_to_identity_packaging"
    fired = 1 if nxt != current_packaging_mode else 0
    return nxt, rule, fired


def update_packaging_mode_from_budget(
    current_packaging_mode: str,
    gating_state: str,
    config: dict[str, Any],
) -> tuple[str, str, int]:
    if str(config.get("family_kind", "")) != "budget_gate_and_packaging":
        return current_packaging_mode, "no_change", 0
    mapping = config.get(
        "packaging_by_gating_state",
        {"permissive": "merge_touching", "strict": "budget_capped_merge"},
    )
    nxt = current_packaging_mode
    if isinstance(mapping, dict):
        candidate = mapping.get(gating_state)
        if isinstance(candidate, str) and candidate in PACKAGING_MODES:
            nxt = candidate
    rule = "budget_to_packaging_switch" if nxt != current_packaging_mode else "no_change"
    fired = 1 if nxt != current_packaging_mode else 0
    return nxt, rule, fired


def render_stage_snapshot(interval_union: IntervalUnion, out_path: Path, title: str) -> None:
    fig, ax = plt.subplots(figsize=(10, 1.8))
    y = 0.5
    for iv in interval_union.intervals:
        ax.plot([iv.left, iv.right], [y, y], linewidth=3, color="#4c78a8", solid_capstyle="butt")
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.0)
    ax.set_yticks([])
    ax.set_xlabel("x")
    ax.set_title(title)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def render_stage_snapshot_raw(intervals: list[Interval], out_path: Path, title: str) -> None:
    fig, ax = plt.subplots(figsize=(10, 2.2))
    for i, iv in enumerate(intervals):
        y = 0.15 + 0.7 * ((i % 3) / 2.0)
        ax.plot([iv.left, iv.right], [y, y], linewidth=2.5, color="#dd8452", alpha=0.75, solid_capstyle="butt")
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.0)
    ax.set_yticks([])
    ax.set_xlabel("x")
    ax.set_title(title + " (raw identity pieces)")
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def run_feedback_family(config: dict[str, Any], steps: int) -> dict[str, Any]:
    params = config.get("parameters", {})
    if not isinstance(params, dict):
        raise ValueError("config.parameters must be object")
    base = int(params.get("base", 3))
    protocol_digits = params.get("protocol_digits")
    if not isinstance(protocol_digits, dict):
        raise ValueError("parameters.protocol_digits must be an object")

    protocol_state = str(params.get("initial_protocol_state", "loose"))
    gating_state = str(params.get("initial_gating_state", "permissive"))
    lens_mode = str(config.get("lens_mode", params.get("lens_mode", "coalesced_intervals")))
    packaging_mode = str(config.get("packaging_mode", params.get("packaging_mode", "merge_touching")))
    if lens_mode not in LENS_MODES:
        raise ValueError(f"invalid lens_mode: {lens_mode}")
    if packaging_mode not in PACKAGING_MODES:
        raise ValueError(f"invalid packaging_mode: {packaging_mode}")

    working = {
        **params,
        "family_kind": str(params.get("family_kind", "")),
    }

    current_intervals: list[Interval] = [Interval(0.0, 1.0)]
    traces: list[StageTraceRow] = []
    protocol_switches = 0
    lens_switches = 0
    packaging_switches = 0
    protocol_states_visited = {protocol_state}
    gating_states_visited = {gating_state}
    lens_modes_visited = {lens_mode}
    packaging_modes_visited = {packaging_mode}
    cells_fired_any: set[str] = set()
    final_raw_intervals: list[Interval] = [Interval(0.0, 1.0)]
    stage_snapshots: list[dict[str, Any]] = []

    for stage in range(1, steps + 1):
        protocol_before = protocol_state
        gating_before = gating_state
        lens_before = lens_mode
        packaging_before = packaging_mode

        digits_raw = protocol_digits.get(protocol_before)
        if not isinstance(digits_raw, list) or not digits_raw:
            raise ValueError(f"missing protocol digit rule for state '{protocol_before}'")
        digits = [int(d) for d in digits_raw]
        gating_digits_by_state = params.get("gating_digits_by_state")
        if isinstance(gating_digits_by_state, dict) and isinstance(gating_digits_by_state.get(gating_before), list):
            allowed = {int(x) for x in gating_digits_by_state[gating_before]}
            digits = [d for d in digits if d in allowed]
        elif gating_before == "strict":
            strict_digits = params.get("gating_digits_strict", [0])
            if isinstance(strict_digits, list):
                allowed_strict = {int(x) for x in strict_digits}
                digits = [d for d in digits if d in allowed_strict]
        if not digits:
            digits = [int(digits_raw[0])]
        raw_intervals = _digit_step(current_intervals, base=base, digits=digits)
        final_raw_intervals = list(raw_intervals)
        packaged_intervals = apply_packaging_mode(raw_intervals, packaging_before, working)

        total_before = sum(iv.length for iv in raw_intervals)
        total_after = sum(iv.length for iv in packaged_intervals)

        lens_threshold_used = float(params.get("lens_gating_strict_threshold", 2.0))
        p2_from_p4_fired = 0
        p2_from_p6_fired = 0
        p5_from_p4_fired = 0
        p5_from_p6_fired = 0
        gating_after = gating_before
        gating_rule = "no_change"
        if working["family_kind"] == "budget_gate_and_packaging":
            observed_metric_name = "budget_raw_interval_count"
            observed_metric_value = float(len(raw_intervals))
            gating_after, gating_rule, lens_threshold_used, p2_from_p6_fired = update_gating_state_from_budget(
                gating_state=gating_before,
                budget_metric_value=observed_metric_value,
                config=working,
            )
        else:
            observed_metric_name, observed_metric_value = compute_lens_observation(
                lens_mode=lens_before,
                raw_intervals=raw_intervals,
                packaged_intervals=packaged_intervals,
                config=working,
            )
            gating_after, gating_rule, lens_threshold_used, p2_from_p4_fired = update_gating_state_from_lens(
                gating_state=gating_before,
                observed_metric_value=observed_metric_value,
                config=working,
            )

        protocol_after, protocol_rule = update_protocol_state(
            protocol_state=protocol_before,
            observed_metric_name=observed_metric_name,
            observed_metric_value=observed_metric_value,
            config=working,
        )
        lens_after, lens_rule = update_lens_mode(
            current_lens_mode=lens_before,
            protocol_state=protocol_after,
            config=working,
        )
        packaging_after = packaging_before
        packaging_rule = "no_change"
        if working["family_kind"] == "lens_protocol_coupled":
            packaging_after, packaging_rule, p5_from_p4_fired = update_packaging_mode_from_lens(
                current_packaging_mode=packaging_before,
                lens_mode=lens_after,
                observed_metric_value=observed_metric_value,
                config=working,
            )
        elif working["family_kind"] == "budget_gate_and_packaging":
            packaging_after, packaging_rule, p5_from_p6_fired = update_packaging_mode_from_budget(
                current_packaging_mode=packaging_before,
                gating_state=gating_after,
                config=working,
            )

        triggered_cells: list[str] = []
        if protocol_after != protocol_before:
            protocol_switches += 1
            if working["family_kind"] == "lens_protocol_coupled":
                triggered_cells.append("P3<-P4")
        if p2_from_p4_fired:
            triggered_cells.append("P2<-P4")
        if p2_from_p6_fired:
            triggered_cells.append("P2<-P6")
        if lens_after != lens_before:
            lens_switches += 1
            if working["family_kind"] == "lens_protocol_coupled":
                triggered_cells.append("P4<-P3")
        if packaging_after != packaging_before:
            packaging_switches += 1
        if p5_from_p4_fired:
            triggered_cells.append("P5<-P4")
        if p5_from_p6_fired:
            triggered_cells.append("P5<-P6")
        for cell in triggered_cells:
            cells_fired_any.add(cell)

        decision_parts = [r for r in [protocol_rule, lens_rule, packaging_rule] if r != "no_change"]
        decision_rule = ";".join(decision_parts) if decision_parts else "no_change"

        traces.append(
            StageTraceRow(
                stage=stage,
                protocol_state_before=protocol_before,
                protocol_state_after=protocol_after,
                lens_mode_before=lens_before,
                lens_mode_after=lens_after,
                packaging_mode_before=packaging_before,
                packaging_mode_after=packaging_after,
                observed_metric_name=observed_metric_name,
                observed_metric_value=float(observed_metric_value),
                decision_rule=decision_rule,
                triggered_cells=",".join(triggered_cells),
                gating_state_before=gating_before,
                gating_state_after=gating_after,
                gating_rule=gating_rule,
                lens_metric_threshold=lens_threshold_used,
                p2_from_p4_fired=p2_from_p4_fired,
                p2_from_p6_fired=p2_from_p6_fired,
                p5_from_p4_fired=p5_from_p4_fired,
                p5_from_p6_fired=p5_from_p6_fired,
                raw_interval_count=len(raw_intervals),
                packaged_interval_count=len(packaged_intervals),
                total_length_before_packaging=total_before,
                total_length_after_packaging=total_after,
            )
        )
        stage_snapshots.append(
            {
                "stage": stage,
                "raw_intervals": list(raw_intervals),
                "packaged_intervals": list(packaged_intervals),
            }
        )

        protocol_state = protocol_after
        gating_state = gating_after
        lens_mode = lens_after
        packaging_mode = packaging_after
        protocol_states_visited.add(protocol_state)
        gating_states_visited.add(gating_state)
        lens_modes_visited.add(lens_mode)
        packaging_modes_visited.add(packaging_mode)
        current_intervals = packaged_intervals

    final_union = IntervalUnion(current_intervals)
    return {
        "final_union": final_union,
        "final_raw_intervals": final_raw_intervals,
        "trace_rows": traces,
        "switch_counts": {
            "protocol_switches": protocol_switches,
            "lens_switches": lens_switches,
            "packaging_switches": packaging_switches,
        },
        "visited": {
            "protocol_states": sorted(protocol_states_visited),
            "gating_states": sorted(gating_states_visited),
            "lens_modes": sorted(lens_modes_visited),
            "packaging_modes": sorted(packaging_modes_visited),
            "cells_fired": sorted(cells_fired_any),
        },
        "stage_snapshots": stage_snapshots,
    }
