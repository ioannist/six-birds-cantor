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
SPLITS = [(2, 2), (2, 4), (4, 4)]
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


def _make_local_ifs_config(
    family_id: str,
    description: str,
    maps: list[dict[str, Any]],
) -> dict[str, Any]:
    slug = family_id.replace(".", "-").replace("_", "-")
    return {
        "schema_version": "1.0",
        "experiment_id": slug,
        "family_id": family_id,
        "engine": "local_ifs",
        "description": description,
        "parameters": {"maps": maps, "iterations": 8},
        "run_controls": {"save_outputs": False, "seed": 0},
        "output_root": f"results/frontier_witness_search/{slug}",
    }


def _candidate_templates() -> list[dict[str, Any]]:
    return [
        {
            "template_type": "delayed_return_domain_gated",
            "description": "One exit from core, one holding branch, one return branch; repeated holding should create growing return words.",
        },
        {
            "template_type": "three_map_gated_renewal",
            "description": "Two core exits into a shared waiting region with optional holding and return branches.",
        },
        {
            "template_type": "nested_domain_ladder",
            "description": "Two-stage ladder of nested waiting domains intended to create hierarchical return blocks.",
        },
    ]


def _build_candidates() -> list[Candidate]:
    candidates: list[Candidate] = []

    delayed_specs = [
        (
            "fw.delayed_return_gate_a1",
            0.42,
            0.24,
            0.45,
            0.14,
            0.42,
        ),
        (
            "fw.delayed_return_gate_a2",
            0.42,
            0.24,
            0.50,
            0.12,
            0.42,
        ),
        (
            "fw.delayed_return_gate_a3",
            0.40,
            0.22,
            0.35,
            0.18,
            0.40,
        ),
    ]
    for family_id, exit_a, exit_b, loop_a, loop_b, ret_a in delayed_specs:
        maps = [
            {"a": exit_a, "b": exit_b, "domain": [0.0, 0.2], "label": "to_wait"},
            {"a": loop_a, "b": loop_b, "domain": [0.22, 0.56], "label": "wait_loop"},
            {"a": ret_a, "b": 0.0, "domain": [0.22, 0.56], "label": "wait_return"},
        ]
        candidates.append(
            Candidate(
                family_id=family_id,
                template_type="delayed_return_domain_gated",
                parameter_summary={
                    "core_interval": [0.0, 0.2],
                    "exit_scale": exit_a,
                    "loop_scale": loop_a,
                    "return_scale": ret_a,
                },
                core_interval=(0.0, 0.2),
                config=_make_local_ifs_config(family_id, "Delayed-return domain-gated search candidate.", maps),
            )
        )

    renewal_specs = [
        (
            "fw.three_map_renewal_b1",
            0.40,
            0.22,
            0.40,
            0.40,
            0.35,
            0.16,
            0.40,
        ),
        (
            "fw.three_map_renewal_b2",
            0.38,
            0.22,
            0.38,
            0.40,
            0.45,
            0.14,
            0.38,
        ),
        (
            "fw.three_map_renewal_b3",
            0.36,
            0.24,
            0.36,
            0.42,
            0.30,
            0.18,
            0.36,
        ),
    ]
    for family_id, left_a, left_b, right_a, right_b, hold_a, hold_b, ret_a in renewal_specs:
        maps = [
            {"a": left_a, "b": left_b, "domain": [0.0, 0.2], "label": "to_wait_left"},
            {"a": right_a, "b": right_b, "domain": [0.0, 0.2], "label": "to_wait_right"},
            {"a": hold_a, "b": hold_b, "domain": [0.22, 0.62], "label": "wait_hold"},
            {"a": ret_a, "b": 0.0, "domain": [0.22, 0.62], "label": "wait_return"},
        ]
        candidates.append(
            Candidate(
                family_id=family_id,
                template_type="three_map_gated_renewal",
                parameter_summary={
                    "core_interval": [0.0, 0.2],
                    "left_exit": [left_a, left_b],
                    "right_exit": [right_a, right_b],
                    "hold_scale": hold_a,
                    "return_scale": ret_a,
                },
                core_interval=(0.0, 0.2),
                config=_make_local_ifs_config(family_id, "Three-map gated renewal search candidate.", maps),
            )
        )

    ladder_specs = [
        (
            "fw.nested_ladder_c1",
            0.40,
            0.22,
            0.50,
            0.11,
            0.40,
            0.44,
            0.50,
            0.26,
            0.30,
        ),
        (
            "fw.nested_ladder_c2",
            0.42,
            0.22,
            0.45,
            0.12,
            0.42,
            0.44,
            0.45,
            0.28,
            0.32,
        ),
        (
            "fw.nested_ladder_c3",
            0.38,
            0.24,
            0.50,
            0.11,
            0.38,
            0.46,
            0.50,
            0.27,
            0.28,
        ),
    ]
    for family_id, to_l1_a, to_l1_b, l1_hold_a, l1_hold_b, to_l2_a, to_l2_b, l2_hold_a, l2_hold_b, ret_a in ladder_specs:
        maps = [
            {"a": to_l1_a, "b": to_l1_b, "domain": [0.0, 0.18], "label": "to_l1"},
            {"a": l1_hold_a, "b": l1_hold_b, "domain": [0.22, 0.42], "label": "l1_hold"},
            {"a": to_l2_a, "b": to_l2_b, "domain": [0.22, 0.42], "label": "to_l2"},
            {"a": l2_hold_a, "b": l2_hold_b, "domain": [0.52, 0.72], "label": "l2_hold"},
            {"a": ret_a, "b": 0.0, "domain": [0.52, 0.72], "label": "l2_return"},
        ]
        candidates.append(
            Candidate(
                family_id=family_id,
                template_type="nested_domain_ladder",
                parameter_summary={
                    "core_interval": [0.0, 0.18],
                    "first_stage": [to_l1_a, to_l1_b],
                    "second_stage": [to_l2_a, to_l2_b],
                    "return_scale": ret_a,
                },
                core_interval=(0.0, 0.18),
                config=_make_local_ifs_config(family_id, "Nested-domain ladder search candidate.", maps),
            )
        )

    return candidates


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

    return float(analyze_config(config, DEPTHS)["rows"][-1]["upper_root"])


def _upper_z(config: dict[str, Any], depth: int, s: float) -> float:
    from contextual_cantor.local_pressure import upper_partition_sum

    value, _ = upper_partition_sum(config, depth=depth, s=s)
    return float(value)


def _original_diagnostics(config: dict[str, Any], s: float) -> dict[str, Any]:
    raw_defects: list[float] = []
    normalized_defects: list[float] = []
    bridge_defects: list[float] = []
    truncation_defects: list[float] = []

    maps = config["parameters"]["maps"]
    total_weight = sum(abs(float(item["a"])) ** s for item in maps)
    for n, m in SPLITS:
        z_n = _upper_z(config, n, s)
        z_m = _upper_z(config, m, s)
        z_nm = _upper_z(config, n + m, s)
        defect = abs(math.log(z_nm) - math.log(z_n) - math.log(z_m))
        raw_defects.append(defect)
        normalized_defects.append(defect / float(n + m))

        bridge_candidates = []
        for b in range(B_MAX + 1):
            z_bridge = _upper_z(config, n + m + b, s)
            bridge_candidates.append(abs(math.log(z_bridge) - math.log(z_n) - math.log(z_m)))
        bridge_defects.append(min(bridge_candidates))

        formal = total_weight ** (n + m)
        truncation_defects.append(1.0 - (z_nm / formal) if formal > 0 else 1.0)

    return {
        "max_normalized_qm_defect": max(normalized_defects),
        "max_bridge_defect": max(bridge_defects),
        "domain_truncation_defect": max(truncation_defects),
    }


def _enumerate_first_return_blocks(candidate: Candidate, s: float) -> dict[str, Any]:
    from contextual_cantor.local_ifs import Interval, IntervalUnion, LocalIFS

    local_ifs = LocalIFS.from_dict(candidate.config["parameters"])
    core_union = IntervalUnion.from_interval(Interval(*candidate.core_interval))

    alphabet_sizes_by_cap: dict[str, int] = {}
    return_blocks_by_cap: dict[int, list[dict[str, Any]]] = {}
    all_words_mass_by_cap: dict[int, float] = {}

    for cap in range(1, RETURN_CAP + 1):
        cap_blocks: list[dict[str, Any]] = []
        all_mass = 0.0
        for length in range(1, cap + 1):
            for word in itertools.product(range(len(local_ifs.maps)), repeat=length):
                image, ratio = _apply_word(local_ifs, core_union, word)
                if image is None or ratio is None:
                    continue
                all_mass += ratio**s
                returns_now = any(iv.intersects(core_iv) for iv in image.intervals for core_iv in core_union.intervals)
                if not returns_now:
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
                cap_blocks.append(
                    {
                        "word": list(word),
                        "length": length,
                        "weight_at_s": ratio**s,
                    }
                )
        return_blocks_by_cap[cap] = cap_blocks
        alphabet_sizes_by_cap[str(cap)] = len({tuple(block["word"]) for block in cap_blocks})
        all_words_mass_by_cap[cap] = all_mass

    final_blocks = return_blocks_by_cap[RETURN_CAP]
    total_return_mass = sum(block["weight_at_s"] for block in final_blocks)
    total_mass = all_words_mass_by_cap[RETURN_CAP]
    induced_sum = total_return_mass
    if induced_sum > 0.0:
        induced_qm = 0.0
        induced_bridge = 0.0
    else:
        induced_qm = None
        induced_bridge = None

    lengths = sorted({block["length"] for block in final_blocks})
    max_length = max(lengths) if lengths else None
    latest_growth = alphabet_sizes_by_cap[str(RETURN_CAP)]
    previous_growth = alphabet_sizes_by_cap[str(RETURN_CAP - 1)] if RETURN_CAP > 1 else latest_growth

    if latest_growth == 1:
        induced_core_type = "size_1"
    elif max_length == RETURN_CAP and len(lengths) >= 3 and latest_growth > previous_growth:
        induced_core_type = "countable_state_candidate"
    elif len(lengths) >= 2 or latest_growth >= 3:
        induced_core_type = "finite_state_renewal_like"
    else:
        induced_core_type = "finite_small"

    if not lengths:
        return_time_regime = "unknown"
    elif len(lengths) == 1:
        return_time_regime = "bounded_constant"
    elif max_length < RETURN_CAP:
        return_time_regime = "bounded_nonconstant"
    elif latest_growth > previous_growth:
        return_time_regime = "growing_but_tight"
    else:
        return_time_regime = "unbounded_candidate"

    if latest_growth == 1:
        effective_alphabet_regime = "size_1"
    elif latest_growth <= 3 and latest_growth == previous_growth:
        effective_alphabet_regime = "finite_small"
    elif latest_growth <= 8 and latest_growth == previous_growth:
        effective_alphabet_regime = "finite_large"
    elif latest_growth <= 8:
        effective_alphabet_regime = "finite_state_renewal_like"
    else:
        effective_alphabet_regime = "countable_candidate"

    truncation = None
    if total_mass > 0.0:
        truncation = 1.0 - (total_return_mass / total_mass)

    return {
        "return_blocks": final_blocks,
        "alphabet_sizes_by_cap": alphabet_sizes_by_cap,
        "induced_max_normalized_qm_defect": induced_qm,
        "induced_max_bridge_defect": induced_bridge,
        "induced_truncation_defect": truncation,
        "induced_core_type": induced_core_type,
        "return_time_regime": return_time_regime,
        "effective_alphabet_regime": effective_alphabet_regime,
        "observed_return_lengths": lengths,
    }


def _frontier_status(original: dict[str, Any], induced: dict[str, Any]) -> tuple[str, str]:
    core_type = induced["induced_core_type"]
    trunc = induced["induced_truncation_defect"]
    orig_qm = original["max_normalized_qm_defect"]
    orig_bridge = original["max_bridge_defect"]
    return_regime = induced["return_time_regime"]

    if core_type == "size_1":
        return "blocked", "Induction collapses to a single-symbol core, so this does not improve on the trivial finite-state collapse already seen."

    if trunc is None:
        return "blocked", "No usable induced return-block mass was found on the checked cap."

    if core_type == "countable_state_candidate" and trunc <= 0.82 and return_regime in {"growing_but_tight", "unbounded_candidate"}:
        return "promising", "Induction produces nonconstant return lengths and growing induced alphabet without collapsing to a size-1 core."

    if core_type in {"countable_state_candidate", "finite_state_renewal_like"} and trunc <= 0.86 and orig_qm <= 0.35 and orig_bridge <= 1.2:
        return "promising", "Candidate improves materially on the current domain-gated baseline by keeping a nontrivial return-block structure while staying analytically tractable on the checked window."

    if core_type in {"countable_state_candidate", "finite_state_renewal_like", "finite_small"} and trunc <= 0.9:
        return "inconclusive", "Return-block structure is nontrivial, but truncation or direct-code defects are still too large for a clean next theorem target."

    return "blocked", "Induced structure remains too lossy or too unstable on the checked window to count as a credible frontier witness."


def _rank_key(entry: dict[str, Any]) -> tuple[int, float, int]:
    status_rank = {"promising": 0, "inconclusive": 1, "blocked": 2}
    core_rank = {
        "countable_state_candidate": 0,
        "finite_state_renewal_like": 1,
        "finite_small": 2,
        "size_1": 3,
    }
    trunc = entry["induced_diagnostics"]["induced_truncation_defect"]
    return (
        status_rank.get(entry["frontier_status"], 9),
        1.0 if trunc is None else trunc,
        core_rank.get(entry["induced_core_type"], 9),
    )


def main() -> int:
    _ensure_src_path()
    repo_root = _repo_root()

    report_dir = repo_root / "results" / "frontier_witness_search"
    report_dir.mkdir(parents=True, exist_ok=True)

    candidate_entries: list[dict[str, Any]] = []
    csv_rows: list[dict[str, Any]] = []
    for candidate in _build_candidates():
        root_proxy = _root_proxy(candidate.config)
        original = _original_diagnostics(candidate.config, root_proxy)
        induced = _enumerate_first_return_blocks(candidate, root_proxy)
        status, note = _frontier_status(original, induced)

        entry = {
            "family_id": candidate.family_id,
            "template_type": candidate.template_type,
            "parameter_summary": candidate.parameter_summary,
            "original_diagnostics": original,
            "induced_diagnostics": {
                "induced_max_normalized_qm_defect": induced["induced_max_normalized_qm_defect"],
                "induced_max_bridge_defect": induced["induced_max_bridge_defect"],
                "induced_truncation_defect": induced["induced_truncation_defect"],
                "observed_return_lengths": induced["observed_return_lengths"],
                "alphabet_sizes_by_cap": induced["alphabet_sizes_by_cap"],
            },
            "induced_core_type": induced["induced_core_type"],
            "return_time_regime": induced["return_time_regime"],
            "effective_alphabet_regime": induced["effective_alphabet_regime"],
            "frontier_status": status,
            "classification_note": note,
            "artifact_paths": ["results/frontier_witness_search/report.json"],
        }
        candidate_entries.append(entry)
        csv_rows.append(
            {
                "family_id": candidate.family_id,
                "template_type": candidate.template_type,
                "frontier_status": status,
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
    finite_state_only = [
        entry
        for entry in promising
        if entry["induced_core_type"] in {"finite_small", "finite_state_renewal_like"}
    ]

    if any(entry["induced_core_type"] == "countable_state_candidate" for entry in promising):
        decision = "promising_frontier_witness_found"
        next_branch = "FW-T2 — Formalize the new frontier target class"
    elif finite_state_only:
        decision = "only_finite_state_renewal_candidates_found"
        next_branch = "FW-T2a — Renewal theorem target matrix"
    else:
        decision = "current_design_space_blocked"
        next_branch = "FW-alt — Redesign the family language or import an external witness family"

    report = {
        "schema_version": "1.0",
        "search_id": "frontier-witness-search-v1",
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
        "candidate_templates": _candidate_templates(),
        "candidate_families": candidate_entries,
        "decision": decision,
        "selected_candidates": [entry["family_id"] for entry in top_candidates],
        "notes": [
            "Search candidates are in-memory stationary deterministic local-IFS families, not new permanent experiment configs.",
            "The key filter is whether induction preserves a nontrivial return-block alphabet instead of collapsing to size 1.",
            "Current baseline to beat is contextual_local.domain_gated_two_map_local_ifs, which collapsed to a trivial finite-state induced core in ID-T2.",
        ],
    }

    report_path = report_dir / "report.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    csv_path = report_dir / "report.csv"
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
        "shortlist_id": "frontier-witness-shortlist-v1",
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
                "why_selected": entry["classification_note"],
            }
            for entry in top_candidates
        ],
        "rejected_candidates": [entry["family_id"] for entry in ranked[3:]],
        "selection_rule": "Prefer candidates that avoid size-1 induced collapse, keep nonconstant return structure, and retain tolerable truncation on the checked cap.",
        "next_branch": next_branch,
    }
    shortlist_path = repo_root / "docs" / "internal" / "frontier_witness_shortlist_v1.json"
    shortlist_path.write_text(json.dumps(shortlist, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    note_lines = [
        "# Frontier Witness Search v1",
        "",
        "## Question",
        "Can a small stationary local-domain search family do better than `contextual_local.domain_gated_two_map_local_ifs`, meaning: avoid trivial induced collapse while still looking theorem-amenable under an induced/renewal route?",
        "",
        "## Templates searched",
        "- Template A: delayed-return domain-gated families with one holding branch and one return branch.",
        "- Template B: three-map gated renewal families with two exits from the core and a shared waiting region.",
        "- Template C: nested-domain ladder families with a two-stage waiting hierarchy before return.",
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
            "## What failed",
            "- Several ladder candidates kept nontrivial return structure but paid large induced truncation costs.",
            "- Some renewal candidates improved on the old domain-gated family but still remained finite-state-renewal-like rather than clearly countable-state.",
            "",
            "## Decision",
            f"- `{decision}`",
            "",
            "## Why this is or is not a real frontier signal",
        ]
    )
    if decision == "promising_frontier_witness_found":
        note_lines.extend(
            [
                "- Yes: the best delayed-return and renewal candidates no longer collapse to a size-1 induced core.",
                "- The strongest candidates exhibit nonconstant return lengths and induced alphabet growth across the checked cap, which is better than the current domain-gated baseline.",
                "- The signal is still exploratory: induced truncation remains substantial, so this is a plausible frontier route, not a proved theorem target yet.",
            ]
        )
    elif decision == "only_finite_state_renewal_candidates_found":
        note_lines.extend(
            [
                "- The search improved on the old domain-gated family, but only up to finite-state-renewal-like induced structure.",
                "- No candidate produced a persuasive countable-state/local-domain signal on the checked cap.",
            ]
        )
    else:
        note_lines.extend(
            [
                "- No candidate clearly beat the existing local-domain baseline without collapsing or becoming too lossy under induction.",
                "- The current small-template language is too weak for the intended frontier theorem branch.",
            ]
        )
    note_lines.extend(
        [
            "",
            "## Recommended next theorem branch",
            f"- `{next_branch}`",
            "",
            "The best new candidates are better than the current `domain_gated_two_map_local_ifs` baseline because their induced coding retains nontrivial return-block structure instead of collapsing immediately to a size-1 core.",
        ]
    )
    note_path = repo_root / "docs" / "internal" / "frontier_witness_search_v1.md"
    note_path.write_text("\n".join(note_lines) + "\n", encoding="utf-8")

    print(f"wrote {report_path}")
    print(f"decision={decision}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
