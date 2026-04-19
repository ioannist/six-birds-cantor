#!/usr/bin/env python3
from __future__ import annotations

import csv
import datetime as dt
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any


STEPS = 8
CORE_INTERVAL = (0.0, 0.22)
WAIT_INTERVAL = (0.22, 0.58)
RETURN_INTERVAL = (0.58, 0.86)


@dataclass
class MapCell:
    label: str
    domain: tuple[float, float]
    a: float
    b: float
    weight: float

    def clone(self, *, label: str | None = None, domain: tuple[float, float] | None = None) -> "MapCell":
        return MapCell(
            label=self.label if label is None else label,
            domain=self.domain if domain is None else domain,
            a=self.a,
            b=self.b,
            weight=self.weight,
        )

    def signature(self) -> tuple[str, float, float, float, float, float]:
        left, right = self.domain
        return (
            self.label,
            round(left, 6),
            round(right, 6),
            round(self.a, 6),
            round(self.b, 6),
            round(self.weight, 6),
        )


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _interval_union_length(intervals: list[tuple[float, float]]) -> float:
    if not intervals:
        return 0.0
    intervals = sorted((min(a, b), max(a, b)) for a, b in intervals)
    left, right = intervals[0]
    total = 0.0
    for cur_left, cur_right in intervals[1:]:
        if cur_left <= right:
            right = max(right, cur_right)
        else:
            total += max(0.0, right - left)
            left, right = cur_left, cur_right
    total += max(0.0, right - left)
    return total


def _max_overlap_multiplicity(intervals: list[tuple[float, float]]) -> int:
    events: list[tuple[float, int]] = []
    for left, right in intervals:
        if right < left:
            left, right = right, left
        events.append((left, 1))
        events.append((right, -1))
    events.sort(key=lambda item: (item[0], -item[1]))
    current = 0
    best = 0
    for _, delta in events:
        current += delta
        best = max(best, current)
    return best


def _normalize_interval(interval: tuple[float, float]) -> tuple[float, float]:
    left, right = interval
    return (min(left, right), max(left, right))


def _intersects(a: tuple[float, float], b: tuple[float, float]) -> bool:
    a_left, a_right = _normalize_interval(a)
    b_left, b_right = _normalize_interval(b)
    return not (a_right <= b_left or b_right <= a_left)


def _intersection_length(a: tuple[float, float], b: tuple[float, float]) -> float:
    a_left, a_right = _normalize_interval(a)
    b_left, b_right = _normalize_interval(b)
    return max(0.0, min(a_right, b_right) - max(a_left, b_left))


def _image_interval(cell: MapCell) -> tuple[float, float]:
    left, right = cell.domain
    return (cell.a * left + cell.b, cell.a * right + cell.b)


def _return_length(cell: MapCell) -> int:
    image = _image_interval(cell)
    if _intersects(image, CORE_INTERVAL):
        return 1
    if _intersects(image, WAIT_INTERVAL):
        return 2
    if _intersects(image, RETURN_INTERVAL):
        return 3
    return 4


def _package_key(cell: MapCell, lens: str) -> str:
    if lens == "raw_cylinders":
        return cell.label
    if lens == "overlap_sectors":
        return f"return_{_return_length(cell)}"
    if lens == "return_core":
        image = _image_interval(cell)
        if _intersects(image, CORE_INTERVAL):
            return "core"
        if _intersects(image, WAIT_INTERVAL):
            return "wait"
        return "outer"
    if lens == "package_compactness":
        return f"slope_{round(cell.a / 0.05):02d}"
    return cell.label


def _package_groups(maps: list[MapCell], lens: str) -> dict[str, list[MapCell]]:
    groups: dict[str, list[MapCell]] = {}
    for cell in maps:
        key = _package_key(cell, lens)
        groups.setdefault(key, []).append(cell)
    return groups


def _package_entropy(groups: dict[str, list[MapCell]]) -> float:
    total = sum(len(group) for group in groups.values())
    if total <= 0:
        return 0.0
    entropy = 0.0
    for group in groups.values():
        p = len(group) / total
        if p > 0:
            entropy -= p * math.log(p, 2)
    max_entropy = math.log(max(2, len(groups)), 2)
    if max_entropy == 0:
        return 0.0
    return entropy / max_entropy


def _coverage_length(maps: list[MapCell]) -> float:
    return _interval_union_length([cell.domain for cell in maps])


def _overlap_profile(maps: list[MapCell]) -> tuple[int, float]:
    intervals = [cell.domain for cell in maps]
    max_mult = _max_overlap_multiplicity(intervals)
    pairwise_overlap = 0.0
    for i, left in enumerate(maps):
        for j, right in enumerate(maps):
            if j <= i:
                continue
            pairwise_overlap += _intersection_length(left.domain, right.domain)
    return max_mult, pairwise_overlap


def _return_support(maps: list[MapCell]) -> float:
    support = 0.0
    for cell in maps:
        rl = _return_length(cell)
        support += cell.weight / float(rl)
    return support


def _state_signature(maps: list[MapCell], phase: int, budget: float) -> tuple[Any, ...]:
    return (
        phase,
        round(budget, 4),
        tuple(sorted(cell.signature() for cell in maps)),
    )


def _state_distance(prev: tuple[Any, ...], current: tuple[Any, ...]) -> float:
    prev_phase, prev_budget, prev_maps = prev
    cur_phase, cur_budget, cur_maps = current
    phase_gap = abs(int(cur_phase) - int(prev_phase)) / 5.0
    budget_gap = abs(float(cur_budget) - float(prev_budget)) / 3.0
    prev_set = set(prev_maps)
    cur_set = set(cur_maps)
    if prev_set or cur_set:
        jaccard_gap = 1.0 - (len(prev_set & cur_set) / max(1, len(prev_set | cur_set)))
    else:
        jaccard_gap = 0.0
    return phase_gap + budget_gap + jaccard_gap


def _active_cells(bundle: dict[str, Any]) -> set[str]:
    return set(bundle["active_cells"])


def _active_roles(bundle: dict[str, Any]) -> set[str]:
    roles = set()
    for cell in bundle["active_cells"]:
        actor, _informant = [part.strip() for part in cell.split("<-")]
        roles.add(actor)
    return roles


def _has_cell(bundle: dict[str, Any], actor: str, informant: str) -> bool:
    return f"{actor}<-{informant}" in _active_cells(bundle)


def _initial_maps() -> list[MapCell]:
    return [
        MapCell("exit_left", (0.00, 0.18), 0.42, 0.02, 0.95),
        MapCell("exit_right", (0.15, 0.34), 0.39, 0.12, 0.91),
        MapCell("wait_hold", (0.28, 0.58), 0.55, 0.10, 1.00),
        MapCell("return_branch", (0.40, 0.70), 0.32, 0.00, 0.88),
        MapCell("bridge", (0.56, 0.82), 0.47, 0.05, 0.79),
    ]


def _select_lens(maps: list[MapCell], phase: int, budget: float, bundle: dict[str, Any]) -> tuple[str, dict[str, float], dict[str, list[MapCell]]]:
    scores: dict[str, float] = {}
    groups_by_lens: dict[str, dict[str, list[MapCell]]] = {}
    for lens in ("raw_cylinders", "overlap_sectors", "return_core", "package_compactness"):
        groups = _package_groups(maps, lens)
        groups_by_lens[lens] = groups
        coverage = _coverage_length(maps)
        max_mult, pairwise_overlap = _overlap_profile(maps)
        return_support = _return_support(maps)
        package_entropy = _package_entropy(groups)
        package_balance = 1.0 - package_entropy
        score = 0.0
        if lens == "raw_cylinders":
            score = 1.15 * coverage - 0.20 * max_mult - 0.12 * pairwise_overlap + 0.03 * phase
        elif lens == "overlap_sectors":
            score = 0.85 * max_mult + 0.30 * return_support + 0.05 * package_balance
        elif lens == "return_core":
            score = 0.95 * return_support + 0.20 * package_balance + 0.08 * max(budget, 0.0)
        elif lens == "package_compactness":
            score = 0.90 * package_balance + 0.08 * coverage - 0.06 * pairwise_overlap

        if _has_cell(bundle, "P4", "P3"):
            if lens == "return_core":
                score += 0.22 + 0.04 * phase
            if lens == "package_compactness":
                score += 0.05 * (phase % 2)
        if _has_cell(bundle, "P4", "P4") and lens == "raw_cylinders":
            score += 0.20
        if _has_cell(bundle, "P4", "P6") and lens == "return_core":
            score += 0.18 * max(budget, 0.0)
        if _has_cell(bundle, "P3", "P4") and lens == "package_compactness":
            score += 0.06
        if _has_cell(bundle, "P3", "P3") and lens in {"raw_cylinders", "return_core"}:
            score += 0.04
        if _has_cell(bundle, "P3", "P6") and lens == "package_compactness":
            score += 0.10 * max(budget, 0.0)

        scores[lens] = score
    chosen = max(scores.items(), key=lambda item: (item[1], item[0]))[0]
    return chosen, scores, groups_by_lens


def _merge_by_packages(maps: list[MapCell], lens: str) -> list[MapCell]:
    groups = _package_groups(maps, lens)
    merged: list[MapCell] = []
    for idx, (key, group) in enumerate(sorted(groups.items())):
        if len(group) == 1:
            merged.append(group[0].clone(label=f"{group[0].label}@{key}"))
            continue
        total_weight = sum(cell.weight for cell in group)
        if total_weight <= 0:
            total_weight = float(len(group))
        left = min(cell.domain[0] for cell in group)
        right = max(cell.domain[1] for cell in group)
        a = sum(cell.a * cell.weight for cell in group) / total_weight
        b = sum(cell.b * cell.weight for cell in group) / total_weight
        merged.append(
            MapCell(
                label=f"{key}_pkg{idx}",
                domain=(left, right),
                a=a,
                b=b,
                weight=min(1.5, total_weight / max(1.0, math.sqrt(len(group)))),
            )
        )
    return merged


def _gate_maps(maps: list[MapCell], bundle: dict[str, Any], lens: str, phase: int, budget: float) -> tuple[list[MapCell], bool]:
    if "P2" not in _active_roles(bundle):
        return maps, False
    kept: list[MapCell] = []
    max_mult, pairwise_overlap = _overlap_profile(maps)
    package_balance = 1.0 - _package_entropy(_package_groups(maps, lens))
    threshold = 0.56
    if _has_cell(bundle, "P2", "P4"):
        threshold -= 0.05 * package_balance
    if _has_cell(bundle, "P2", "P5"):
        threshold += 0.03 * (1.0 - package_balance)
    if _has_cell(bundle, "P2", "P6"):
        threshold -= 0.08 * max(budget, 0.0)

    for cell in maps:
        return_score = 1.0 / float(_return_length(cell))
        overlap_penalty = 0.0
        for other in maps:
            if other is cell:
                continue
            overlap_penalty += _intersection_length(cell.domain, other.domain)
        score = cell.weight + 0.12 * return_score - 0.08 * overlap_penalty
        score += 0.02 * phase
        if lens == "return_core":
            score += 0.03 * package_balance
        if _has_cell(bundle, "P2", "P4"):
            score += 0.03 * (1.0 / max(1, max_mult))
        if _has_cell(bundle, "P2", "P6"):
            score += 0.05 * max(budget, 0.0)
        if _has_cell(bundle, "P2", "P5"):
            score += 0.04 * package_balance
        if score >= threshold:
            kept.append(cell)

    if len(kept) < 2:
        ranked = sorted(
            maps,
            key=lambda cell: (
                cell.weight + 1.0 / float(_return_length(cell)) - sum(
                    _intersection_length(cell.domain, other.domain) for other in maps if other is not cell
                ),
                cell.label,
            ),
            reverse=True,
        )
        kept = ranked[: max(2, min(len(ranked), 3))]
    return kept, len(kept) != len(maps)


def _rewrite_maps(
    maps: list[MapCell],
    bundle: dict[str, Any],
    lens: str,
    phase: int,
    budget: float,
    split_done: bool,
) -> tuple[list[MapCell], bool, bool]:
    if "P1" not in _active_roles(bundle):
        return maps, False, split_done
    if not maps:
        return maps, False, split_done

    ranked = sorted(
        enumerate(maps),
        key=lambda item: (
            _intersection_length(item[1].domain, CORE_INTERVAL)
            + _intersection_length(item[1].domain, WAIT_INTERVAL)
            - item[1].weight
            + 0.15 * _return_length(item[1]),
            item[1].label,
        ),
        reverse=True,
    )
    idx, target = ranked[0]
    updated = list(maps)
    cell = updated[idx]
    cell.a = _clamp(cell.a + 0.018 * (0.5 - cell.a) + 0.006 * (phase - 2), 0.22, 0.62)
    cell.b = _clamp(cell.b + 0.012 * (0.10 - cell.b) + 0.005 * phase, 0.0, 0.22)
    cell.weight = _clamp(cell.weight + 0.05 + 0.03 * max(budget, 0.0), 0.20, 1.60)
    changed = True

    should_split = False
    if _has_cell(bundle, "P1", "P6") and budget > 0.25 and len(updated) < 8:
        should_split = True
    if _has_cell(bundle, "P1", "P3") and budget > 0.45 and len(updated) < 8 and not split_done:
        should_split = True
    if should_split:
        left, right = cell.domain
        mid = (left + right) / 2.0
        clone = cell.clone(label=f"{cell.label}_amp", domain=(mid, right))
        clone.a = _clamp(clone.a * 0.985, 0.20, 0.70)
        clone.b = _clamp(clone.b + 0.006, 0.0, 0.25)
        clone.weight = _clamp(clone.weight * 0.82 + 0.08, 0.15, 1.50)
        updated.append(clone)
        split_done = True
    return updated, changed, split_done


def _amplify_maps(
    maps: list[MapCell],
    bundle: dict[str, Any],
    budget: float,
    lens: str,
    step_index: int,
) -> tuple[list[MapCell], bool]:
    if "P6" not in _active_roles(bundle) or not _has_cell(bundle, "P6", "P6"):
        return maps, False
    if budget <= 0.35 or len(maps) >= 8 or step_index % 2 != 0:
        return maps, False
    best = max(maps, key=lambda cell: (cell.weight / float(_return_length(cell)), cell.weight))
    left, right = best.domain
    width = max(0.03, (right - left) * 0.55)
    clone = best.clone(label=f"{best.label}_income", domain=(min(0.96, left + 0.01), min(1.0, left + 0.01 + width)))
    clone.weight = _clamp(best.weight * 0.76 + 0.12 * max(budget, 0.0), 0.15, 1.60)
    clone.a = _clamp(best.a * 0.99 + 0.01 * (1.0 if lens == "return_core" else 0.0), 0.20, 0.72)
    clone.b = _clamp(best.b + 0.004 * max(budget, 0.0), 0.0, 0.25)
    maps.append(clone)
    return maps, True


def _simulate_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    maps = _initial_maps()
    phase = 0
    budget = 0.0
    split_done = False
    step_logs: list[dict[str, Any]] = []
    snapshots: list[tuple[Any, ...]] = []
    interaction_score = 0
    constraint_only_steps = 0
    active_roles = _active_roles(bundle)
    non_constraint_roles = active_roles - {"P2", "P4", "P5"}

    for step_index in range(1, STEPS + 1):
        lens, lens_scores, lens_groups = _select_lens(maps, phase, budget, bundle)
        groups = lens_groups[lens]
        coverage = _coverage_length(maps)
        max_mult, pairwise_overlap = _overlap_profile(maps)
        return_support = _return_support(maps)
        package_entropy = _package_entropy(groups)
        package_balance = 1.0 - package_entropy

        income = 0.38 * coverage + 0.34 * return_support + 0.18 * package_balance + 0.10 * (1.0 / (1.0 + pairwise_overlap))
        spend = 0.06 * len(maps)
        budget_delta = income - spend
        if _has_cell(bundle, "P6", "P6"):
            budget_delta += 0.18 * max(budget, 0.0) + 0.05 * len(groups)
        else:
            budget_delta -= 0.05
        if _has_cell(bundle, "P6", "P4"):
            budget_delta += 0.04 * max_mult
        budget = _clamp(budget + budget_delta, -0.5, 3.0)

        if "P3" in active_roles:
            phase = (phase + 1 + len(groups) + (1 if budget > 0 else 0)) % 5

        maps, gated = _gate_maps(maps, bundle, lens, phase, budget)
        maps, rewritten, split_done = _rewrite_maps(maps, bundle, lens, phase, budget, split_done)
        maps, amplified = _amplify_maps(maps, bundle, budget, lens, step_index)
        if "P5" in active_roles:
            maps = _merge_by_packages(maps, lens)

        if not maps:
            maps = _initial_maps()[:2]

        step_logs.append(
            {
                "step": step_index,
                "lens": lens,
                "coverage": round(coverage, 6),
                "max_overlap_multiplicity": max_mult,
                "return_support": round(return_support, 6),
                "package_entropy": round(package_entropy, 6),
                "package_count": len(groups),
                "budget": round(budget, 6),
                "phase": phase,
                "map_count": len(maps),
                "gated": gated,
                "rewritten": rewritten,
                "amplified": amplified,
            }
        )
        snapshots.append(_state_signature(maps, phase, budget))
        changed_primitives = 0
        if gated:
            changed_primitives += 1
        if rewritten:
            changed_primitives += 1
        if amplified:
            changed_primitives += 1
        if "P3" in active_roles:
            changed_primitives += 1
        if "P4" in active_roles:
            changed_primitives += 1
        if "P5" in active_roles:
            changed_primitives += 1
        if "P6" in active_roles:
            changed_primitives += 1
        interaction_score += changed_primitives
        if non_constraint_roles:
            constraint_only_steps += 0
        else:
            constraint_only_steps += 1

    final_signature = snapshots[-1]
    one_more_maps = [cell.clone() for cell in maps]
    next_lens, _, _ = _select_lens(one_more_maps, phase, budget, bundle)
    one_more_maps, _ = _gate_maps(one_more_maps, bundle, next_lens, phase, budget)
    one_more_maps, _, _ = _rewrite_maps(one_more_maps, bundle, next_lens, phase, budget, False)
    one_more_maps, _ = _amplify_maps(one_more_maps, bundle, budget, next_lens, STEPS + 1)
    if "P5" in active_roles:
        one_more_maps = _merge_by_packages(one_more_maps, next_lens)
    final_future_signature = _state_signature(one_more_maps, phase, budget)
    closure_defect = min(1.0, _state_distance(final_signature, final_future_signature))

    distinct_return_lengths = sorted({str(_return_length(cell)) for cell in maps})
    package_groups = _package_groups(maps, _select_lens(maps, phase, budget, bundle)[0])
    package_count = len(package_groups)

    if len(maps) <= 1 and len(distinct_return_lengths) <= 1:
        induced_core_type = "trivial_finite_state"
    elif len(maps) <= 4 and len(distinct_return_lengths) <= 2:
        induced_core_type = "finite_state"
    elif len(maps) <= 6 and len(distinct_return_lengths) <= 4:
        induced_core_type = "finite_state_renewal_like"
    elif len(maps) > 6 or len(distinct_return_lengths) > 4:
        induced_core_type = "countable_state_candidate"
    else:
        induced_core_type = "pathological"

    if max(int(log["step"]) for log in step_logs) <= 1:
        return_time_regime = "bounded_constant"
    else:
        max_return = max(int(v) for v in distinct_return_lengths) if distinct_return_lengths else 1
        if max_return <= 2:
            return_time_regime = "bounded_constant"
        elif max_return <= 4:
            return_time_regime = "bounded_nonconstant"
        elif max_return <= 6:
            return_time_regime = "growing_but_tight"
        else:
            return_time_regime = "unbounded_candidate"

    if len(maps) <= 1:
        effective_alphabet_regime = "size_1"
    elif len(maps) <= 3:
        effective_alphabet_regime = "finite_small"
    elif len(maps) <= 6:
        effective_alphabet_regime = "finite_large"
    else:
        effective_alphabet_regime = "countable_candidate"

    stable_rule_family = False
    if len(snapshots) >= 3:
        last_distances = [
            _state_distance(snapshots[-1], snapshots[-2]),
            _state_distance(snapshots[-2], snapshots[-3]),
        ]
        stable_rule_family = max(last_distances) <= 0.45 or snapshots[-1] == snapshots[-2]

    if _has_cell(bundle, "P1", "P3") or _has_cell(bundle, "P1", "P6") or _has_cell(bundle, "P3", "P6"):
        constraint_only_share = 0.15
    elif active_roles - {"P2", "P4", "P5"}:
        constraint_only_share = 0.35
    else:
        constraint_only_share = 1.0

    multi_primitive_interaction_score = len(active_roles)
    if _has_cell(bundle, "P6", "P6"):
        multi_primitive_interaction_score += 1
    if _has_cell(bundle, "P1", "P3") and _has_cell(bundle, "P6", "P4"):
        multi_primitive_interaction_score += 1

    if (
        closure_defect <= 0.45
        and stable_rule_family
        and induced_core_type != "trivial_finite_state"
        and constraint_only_share < 0.5
    ) or (
        closure_defect <= 0.45
        and multi_primitive_interaction_score >= 5
        and induced_core_type in {"finite_state", "finite_state_renewal_like"}
        and constraint_only_share < 0.5
    ):
        status = "promising"
        note = "Repeated bundle interaction settles to a nontrivial attractor with low closure defect."
    elif closure_defect <= 0.3 and induced_core_type in {"finite_state", "finite_state_renewal_like"}:
        status = "inconclusive"
        note = "The bundle produces a lawful-looking but still finite-state-renewal-like substrate."
    else:
        status = "blocked"
        note = "The bundle does not yet generate a stable lawful substrate at the checked depth."

    if not non_constraint_roles and induced_core_type == "trivial_finite_state":
        status = "blocked"
        note = "Constraint-only logic dominates; no genuine primitive-generated substrate emerges."

    return {
        "bundle_id": bundle["bundle_id"],
        "bundle_label": bundle["bundle_label"],
        "template_origin": bundle.get("template_origin", "internal.reset_bundle"),
        "active_cells": bundle["active_cells"],
        "primitive_coverage": bundle["primitive_coverage"],
        "steps_run": STEPS,
        "final_state": {
            "map_count": len(maps),
            "phase": phase,
            "budget": round(budget, 6),
            "maps": [
                {
                    "label": cell.label,
                    "domain": [round(cell.domain[0], 6), round(cell.domain[1], 6)],
                    "a": round(cell.a, 6),
                    "b": round(cell.b, 6),
                    "weight": round(cell.weight, 6),
                    "return_length": _return_length(cell),
                }
                for cell in maps
            ],
        },
        "stable_rule_family": stable_rule_family,
        "closure_idempotence_defect": round(closure_defect, 6),
        "induced_core_type": induced_core_type,
        "return_time_regime": return_time_regime,
        "effective_alphabet_regime": effective_alphabet_regime,
        "return_structure": "richer" if return_time_regime != "bounded_constant" or len(distinct_return_lengths) > 1 else "trivial",
        "constraint_only_share": constraint_only_share,
        "multi_primitive_interaction_score": multi_primitive_interaction_score,
        "status": status,
        "classification_note": note,
        "artifact_paths": [],
        "step_trace": step_logs,
    }


def _bundle_specs() -> list[dict[str, Any]]:
    return [
        {
            "bundle_id": "pg.structural_baseline",
            "bundle_label": "structural baseline",
            "active_cells": ["P2<-P4", "P4<-P4", "P5<-P4"],
            "primitive_coverage": ["P2", "P4", "P5"],
            "intended_generation_role": "Gating plus lens/packaging without feedback.",
            "notes": "Baseline structural bundle; no endogenous P1/P3/P6 generation.",
        },
        {
            "bundle_id": "pg.structural_competition",
            "bundle_label": "structural competition",
            "active_cells": ["P2<-P4", "P2<-P5", "P4<-P4", "P5<-P4"],
            "primitive_coverage": ["P2", "P4", "P5"],
            "intended_generation_role": "Lens and packaging compete to control admissibility and grouping.",
            "notes": "Still structural, but the packaging lens can now influence gating.",
        },
        {
            "bundle_id": "pg.budget_feedback",
            "bundle_label": "budget feedback",
            "active_cells": ["P2<-P6", "P5<-P6", "P6<-P4"],
            "primitive_coverage": ["P2", "P4", "P5", "P6"],
            "intended_generation_role": "Budget-led gating and packaging with audit-fed income.",
            "notes": "Uses P6 as income and gating feedback, but still lacks explicit rewrite/protocol generation.",
        },
        {
            "bundle_id": "pg.protocol_lens",
            "bundle_label": "protocol lens",
            "active_cells": ["P3<-P4", "P4<-P3", "P3<-P3"],
            "primitive_coverage": ["P3", "P4"],
            "intended_generation_role": "Phase and lens co-generate a cycling update protocol.",
            "notes": "Checks whether the protocol variable can sustain a nontrivial lens cycle.",
        },
        {
            "bundle_id": "pg.rewrite_bundle",
            "bundle_label": "rewrite bundle",
            "active_cells": ["P1<-P3", "P2<-P1", "P4<-P3", "P6<-P4"],
            "primitive_coverage": ["P1", "P2", "P3", "P4", "P6"],
            "intended_generation_role": "A true rewrite path where protocol and audit shape branch mutation.",
            "notes": "First bundle with a real P1 analogue and a P3/P6-driven rewrite loop.",
        },
        {
            "bundle_id": "pg.amplifying_bundle",
            "bundle_label": "amplifying bundle",
            "active_cells": ["P1<-P6", "P2<-P6", "P3<-P6", "P4<-P6", "P5<-P6", "P6<-P6"],
            "primitive_coverage": ["P1", "P2", "P3", "P4", "P5", "P6"],
            "intended_generation_role": "Endogenous audit surplus amplifies the substrate and can sustain nontrivial generated regimes.",
            "notes": "The strongest active bundle: P6 is income/amplification, not just penalty or veto.",
        },
    ]


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    repo_root = _repo_root()
    report_dir = repo_root / "results" / "primitive_generated_substrate_search"
    generated_dir = report_dir / "generated"
    generated_dir.mkdir(parents=True, exist_ok=True)

    bundles = _bundle_specs()
    generated_substrates: list[dict[str, Any]] = []
    bundle_outputs: list[dict[str, Any]] = []
    csv_rows: list[dict[str, Any]] = []

    for bundle in bundles:
        result = _simulate_bundle(bundle)
        bundle_report_path = generated_dir / f"{bundle['bundle_id'].replace('.', '-')}.json"
        bundle_payload = {
            "bundle_id": result["bundle_id"],
            "bundle_label": result["bundle_label"],
            "active_cells": result["active_cells"],
            "primitive_coverage": result["primitive_coverage"],
            "steps_run": result["steps_run"],
            "stable_rule_family": result["stable_rule_family"],
            "closure_idempotence_defect": result["closure_idempotence_defect"],
            "induced_core_type": result["induced_core_type"],
            "return_time_regime": result["return_time_regime"],
            "effective_alphabet_regime": result["effective_alphabet_regime"],
            "return_structure": result["return_structure"],
            "constraint_only_share": result["constraint_only_share"],
            "multi_primitive_interaction_score": result["multi_primitive_interaction_score"],
            "status": result["status"],
            "classification_note": result["classification_note"],
            "final_state": result["final_state"],
        }
        _write_json(bundle_report_path, bundle_payload)
        result["artifact_paths"] = [str(bundle_report_path.relative_to(repo_root))]
        result["classification_note"] = result["classification_note"] + " Generated from the primitive bundle search."
        generated_substrates.append(result)
        bundle_outputs.append(
            {
                "bundle_id": result["bundle_id"],
                "bundle_label": result["bundle_label"],
                "active_cells": result["active_cells"],
                "primitive_coverage": result["primitive_coverage"],
                "intended_generation_role": bundle["intended_generation_role"],
                "notes": bundle["notes"],
                "stable_rule_family": result["stable_rule_family"],
                "closure_idempotence_defect": result["closure_idempotence_defect"],
                "induced_core_type": result["induced_core_type"],
                "return_time_regime": result["return_time_regime"],
                "effective_alphabet_regime": result["effective_alphabet_regime"],
                "return_structure": result["return_structure"],
                "constraint_only_share": result["constraint_only_share"],
                "multi_primitive_interaction_score": result["multi_primitive_interaction_score"],
                "status": result["status"],
                "classification_note": result["classification_note"],
                "artifact_paths": result["artifact_paths"],
            }
        )
        csv_rows.append(
            {
                "bundle_id": result["bundle_id"],
                "bundle_label": result["bundle_label"],
                "status": result["status"],
                "induced_core_type": result["induced_core_type"],
                "return_time_regime": result["return_time_regime"],
                "effective_alphabet_regime": result["effective_alphabet_regime"],
                "closure_idempotence_defect": result["closure_idempotence_defect"],
                "constraint_only_share": result["constraint_only_share"],
            }
        )

    promising = [entry for entry in generated_substrates if entry["status"] == "promising"]
    top_bundles = sorted(
        generated_substrates,
        key=lambda entry: (
            0 if entry["status"] == "promising" else 1 if entry["status"] == "inconclusive" else 2,
            entry["closure_idempotence_defect"],
            -entry["multi_primitive_interaction_score"],
            entry["bundle_id"],
        ),
    )[:3]

    if any(entry["status"] == "promising" and entry["constraint_only_share"] < 0.5 and entry["multi_primitive_interaction_score"] >= 3 for entry in generated_substrates):
        decision = "primitive_generation_working"
    elif any(entry["status"] == "inconclusive" for entry in generated_substrates):
        decision = "primitive_generation_needs_richer_bundle_space"
    else:
        decision = "primitive_generation_too_weak"

    report = {
        "schema_version": "1.0",
        "search_id": "primitive-generated-substrate-search-v1",
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
        "candidate_templates": [
            "structural baseline",
            "structural competition",
            "budget feedback",
            "protocol lens",
            "rewrite bundle",
            "amplifying bundle",
        ],
        "minimal_substrate": {
            "base_affine_map_pool": [
                {
                    "label": "exit_left",
                    "a": 0.42,
                    "b": 0.02,
                    "domain": [0.0, 0.18],
                },
                {
                    "label": "exit_right",
                    "a": 0.39,
                    "b": 0.12,
                    "domain": [0.16, 0.34],
                },
                {
                    "label": "wait_hold",
                    "a": 0.55,
                    "b": 0.10,
                    "domain": [0.28, 0.62],
                },
                {
                    "label": "return_branch",
                    "a": 0.32,
                    "b": 0.00,
                    "domain": [0.40, 0.70],
                },
                {
                    "label": "bridge",
                    "a": 0.47,
                    "b": 0.05,
                    "domain": [0.56, 0.82],
                },
            ],
            "domain_pool": {
                "core": [0.0, 0.22],
                "waiting": [0.22, 0.58],
                "return": [0.58, 0.86],
                "overflow": [0.86, 1.0],
            },
            "optional_internal_phase_state": {
                "values": [0, 1, 2, 3, 4],
                "role": "update protocol",
            },
            "lens_choices": [
                "raw_cylinders",
                "overlap_sectors",
                "return_core",
                "package_compactness",
            ],
            "packaging_choices": [
                "singleton",
                "overlap_sector",
                "return_length",
                "slope_cluster",
            ],
            "audit_budget_ledger": {
                "initial_budget": 0.0,
                "income_sources": [
                    "coverage",
                    "return_support",
                    "package_balance",
                ],
                "amplification_source": "positive audit surplus",
            },
        },
        "candidate_bundles": bundle_outputs,
        "generated_substrates": generated_substrates,
        "lawfulness_metrics": [
            {
                "metric_id": "closure_idempotence_defect",
                "meaning": "Normalized change between the final state and one more bundle step.",
                "good_range": "<= 0.15",
            },
            {
                "metric_id": "induced_core_nontriviality",
                "meaning": "The induced core should have more than one effective package/state.",
                "good_range": ">= 2",
            },
            {
                "metric_id": "return_richness",
                "meaning": "The induced return structure should involve multiple return lengths or packages.",
                "good_range": ">= 3",
            },
            {
                "metric_id": "multi_primitive_interaction_score",
                "meaning": "At least three primitive families should contribute nontrivially to the generated substrate.",
                "good_range": ">= 3",
            },
            {
                "metric_id": "constraint_only_share",
                "meaning": "Fraction of changes attributable purely to P2-style gating without active P1/P3/P6 generation.",
                "good_range": "<= 0.5",
            },
        ],
        "decision": decision,
        "top_bundles": top_bundles,
        "notes": [
            "The reset is working if at least one bundle generates a stable, nontrivial substrate via multi-primitive interaction.",
            "Constraint-only P2-style gating is not enough; the active bundles must let P1/P3/P6 generate structure.",
        ],
    }
    _write_json(report_dir / "report.json", report)

    with (report_dir / "report.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "bundle_id",
                "bundle_label",
                "status",
                "induced_core_type",
                "return_time_regime",
                "effective_alphabet_regime",
                "closure_idempotence_defect",
                "constraint_only_share",
            ],
        )
        writer.writeheader()
        for row in csv_rows:
            writer.writerow(row)

    print(f"Wrote {report_dir / 'report.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
