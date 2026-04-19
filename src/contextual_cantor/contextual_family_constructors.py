from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .local_ifs import LocalIFS, iterate_set


def build_prefix_memory_last_digit_rule(depth: int = 8) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "experiment_id": "prefix-memory-last-digit-rule",
        "family_id": "contextual_local.prefix_memory_last_digit_rule",
        "engine": "finite_state_symbolic",
        "description": "Digit choices depend on the previous digit in base 3.",
        "lens_mode": "prefix_sectors",
        "packaging_mode": "merge_touching",
        "parameters": {
            "constructor": "prefix_memory_last_digit_rule",
            "base": 3,
            "start_digits": [0, 1, 2],
            "transition_digits": {
                "0": [0, 2],
                "1": [0],
                "2": [1, 2]
            },
            "snapshot_depth": depth
        },
        "run_controls": {"seed": 0, "save_outputs": True},
        "output_root": "results/contextual_family_samples/prefix_memory_last_digit_rule"
    }


def build_prefix_memory_no_22_base3(depth: int = 8) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "experiment_id": "prefix-memory-no-22-base3",
        "family_id": "contextual_local.prefix_memory_no_22_base3",
        "engine": "finite_state_symbolic",
        "description": "Forbid adjacent '22' in base-3 digit strings.",
        "lens_mode": "prefix_sectors",
        "packaging_mode": "merge_touching",
        "parameters": {
            "constructor": "prefix_memory_no_22_base3",
            "base": 3,
            "start_digits": [0, 2],
            "transition_digits": {
                "0": [0, 2],
                "2": [0]
            },
            "snapshot_depth": depth
        },
        "run_controls": {"seed": 0, "save_outputs": True},
        "output_root": "results/contextual_family_samples/prefix_memory_no_22_base3"
    }


def build_domain_gated_two_map_local_ifs(iterations: int = 8) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "experiment_id": "domain-gated-two-map-local-ifs",
        "family_id": "contextual_local.domain_gated_two_map_local_ifs",
        "engine": "local_ifs",
        "description": "Two contractive maps with disjoint gating domains.",
        "lens_mode": "coalesced_intervals",
        "packaging_mode": "merge_touching",
        "parameters": {
            "constructor": "domain_gated_two_map_local_ifs",
            "maps": [
                {"a": 0.5, "b": 0.0, "domain": [0.0, 0.5], "label": "left"},
                {"a": 0.5, "b": 0.5, "domain": [0.5, 1.0], "label": "right"}
            ],
            "iterations": iterations
        },
        "run_controls": {"seed": 0, "save_outputs": True},
        "output_root": "results/contextual_family_samples/domain_gated_two_map_local_ifs"
    }


def build_stage_dependent_alternating_removal(depth: int = 8) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "experiment_id": "stage-dependent-alternating-removal",
        "family_id": "contextual_local.stage_dependent_alternating_removal",
        "engine": "nonautonomous_symbolic",
        "description": "Alternating stage rules in base 3 for contextual removal.",
        "lens_mode": "coalesced_intervals",
        "packaging_mode": "merge_touching",
        "parameters": {
            "constructor": "stage_dependent_alternating_removal",
            "base": 3,
            "stage_digit_sets": [
                [0, 2],
                [0, 1]
            ],
            "snapshot_depth": depth
        },
        "run_controls": {"seed": 0, "save_outputs": True},
        "output_root": "results/contextual_family_samples/stage_dependent_alternating_removal"
    }


def write_experiment_config(config: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(config, indent=2, sort_keys=True), encoding="utf-8")


def _intervals_from_digit_words(base: int, words: list[list[int]]) -> list[tuple[float, float]]:
    intervals: list[tuple[float, float]] = []
    if not words:
        return intervals
    depth = len(words[0])
    scale = float(base) ** depth
    width = 1.0 / scale
    for word in words:
        offset = 0.0
        for i, digit in enumerate(word, start=1):
            offset += float(digit) / (float(base) ** i)
        intervals.append((offset, offset + width))
    return sorted(intervals)


def _generate_prefix_words(
    start_digits: list[int],
    transition_digits: dict[str, list[int]],
    depth: int,
) -> list[list[int]]:
    words = [[d] for d in start_digits]
    if depth <= 1:
        return words
    for _ in range(1, depth):
        nxt: list[list[int]] = []
        for w in words:
            allowed = transition_digits[str(w[-1])]
            for d in allowed:
                nxt.append(w + [d])
        words = nxt
    return words


def _generate_stage_alternating_words(stage_digit_sets: list[list[int]], depth: int) -> list[list[int]]:
    words = [[]]
    for stage in range(depth):
        digits = stage_digit_sets[stage % len(stage_digit_sets)]
        nxt: list[list[int]] = []
        for w in words:
            for d in digits:
                nxt.append(w + [d])
        words = nxt
    return words


def _plot_intervals(intervals: list[tuple[float, float]], png_path: Path, title: str) -> None:
    fig, ax = plt.subplots(figsize=(10, 1.8))
    y = 0.5
    for left, right in intervals:
        ax.plot([left, right], [y, y], color="#2a9d8f", linewidth=3, solid_capstyle="butt")
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.0)
    ax.set_yticks([])
    ax.set_xlabel("x")
    ax.set_title(title)
    fig.tight_layout()
    png_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(png_path, dpi=150)
    plt.close(fig)


def sample_stage_snapshot(config: dict[str, Any], out_dir: Path) -> tuple[Path, dict[str, Any]]:
    family_id = str(config["family_id"])
    params = config["parameters"]
    metrics: dict[str, Any] = {}

    if family_id == "contextual_local.prefix_memory_last_digit_rule":
        base = int(params["base"])
        depth = int(params["snapshot_depth"])
        words = _generate_prefix_words(
            start_digits=[int(x) for x in params["start_digits"]],
            transition_digits={k: [int(v) for v in vals] for k, vals in params["transition_digits"].items()},
            depth=depth,
        )
        intervals = _intervals_from_digit_words(base, words)
        metrics = {"depth": depth, "word_count": len(words), "interval_count": len(intervals)}
    elif family_id == "contextual_local.prefix_memory_no_22_base3":
        base = int(params["base"])
        depth = int(params["snapshot_depth"])
        words = _generate_prefix_words(
            start_digits=[int(x) for x in params["start_digits"]],
            transition_digits={k: [int(v) for v in vals] for k, vals in params["transition_digits"].items()},
            depth=depth,
        )
        intervals = _intervals_from_digit_words(base, words)
        metrics = {"depth": depth, "word_count": len(words), "interval_count": len(intervals)}
    elif family_id == "contextual_local.domain_gated_two_map_local_ifs":
        iterations = int(params["iterations"])
        local_ifs = LocalIFS.from_dict(params)
        seq = iterate_set(local_ifs, steps=iterations)
        final_union = seq[-1]
        intervals = [(iv.left, iv.right) for iv in final_union.intervals]
        metrics = {
            "iterations": iterations,
            "final_interval_count": len(final_union.intervals),
            "final_total_length": final_union.total_length,
        }
    elif family_id == "contextual_local.stage_dependent_alternating_removal":
        base = int(params["base"])
        depth = int(params["snapshot_depth"])
        stage_digit_sets = [[int(x) for x in stage] for stage in params["stage_digit_sets"]]
        words = _generate_stage_alternating_words(stage_digit_sets, depth)
        intervals = _intervals_from_digit_words(base, words)
        metrics = {"depth": depth, "word_count": len(words), "interval_count": len(intervals)}
    else:
        raise ValueError(f"unsupported family for snapshot: {family_id}")

    png_path = out_dir / f"{config['experiment_id']}_snapshot.png"
    _plot_intervals(intervals, png_path, f"{family_id}")
    metrics["png_path"] = png_path.as_posix()
    return png_path, metrics
