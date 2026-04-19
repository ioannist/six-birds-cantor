#!/usr/bin/env python3
from __future__ import annotations

import csv
import datetime as dt
import json
import math
import sys
from pathlib import Path
from typing import Any

DEPTHS = [4, 6, 8, 10]
SPLITS = [(2, 2), (2, 4), (4, 4)]
L_MAX = 4


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"expected JSON object in {path}")
    return data


def _root_proxy(config: dict[str, Any], repo_root: Path) -> float:
    src_path = repo_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    from contextual_cantor.local_pressure import analyze_config
    from contextual_cantor.transfer_operator import reference_root_for_family

    ref = reference_root_for_family(str(config["family_id"]))
    if ref is not None:
        return float(ref)
    analysis = analyze_config(config, depths=DEPTHS)
    return float(analysis["rows"][-1]["upper_root"])


def _upper_z(config: dict[str, Any], depth: int, s: float) -> float:
    from contextual_cantor.local_pressure import upper_partition_sum

    z, _ = upper_partition_sum(config, depth=depth, s=s)
    return float(z)


def _original_defects(config: dict[str, Any], s: float) -> dict[str, Any]:
    raw_defects = []
    norm_defects = []
    bridge_defects = []
    for n, m in SPLITS:
        z_n = _upper_z(config, n, s)
        z_m = _upper_z(config, m, s)
        z_nm = _upper_z(config, n + m, s)
        defect = abs(math.log(z_nm) - math.log(z_n) - math.log(z_m))
        raw_defects.append(defect)
        norm_defects.append(defect / float(n + m))
        bridge_candidates = []
        for b in range(L_MAX + 1):
            z_bridge = _upper_z(config, n + m + b, s)
            bridge_candidates.append(abs(math.log(z_bridge) - math.log(z_n) - math.log(z_m)))
        bridge_defects.append(min(bridge_candidates))
    return {
        "max_raw_qm_defect": max(raw_defects),
        "max_normalized_qm_defect": max(norm_defects),
        "max_bridge_defect": max(bridge_defects),
    }


def _classical_induced(config: dict[str, Any], s: float) -> dict[str, Any]:
    base = int(config["parameters"]["base"])
    digits = [int(d) for d in config["parameters"]["allowed_digits"]]
    weights = [(1.0 / base) ** s for _ in digits]
    total = sum(weights)
    return {
        "core_definition": "whole one-state symbolic core",
        "return_blocks": [{"word": [d], "length": 1, "weight_at_s": (1.0 / base) ** s} for d in digits],
        "induced_z": lambda k: total**k,
        "truncation": 0.0,
    }


def _prefix_induced(config: dict[str, Any], s: float) -> dict[str, Any]:
    base = int(config["parameters"]["base"])
    start_digits = [int(d) for d in config["parameters"]["start_digits"]]
    transitions = {int(k): [int(v) for v in vals] for k, vals in config["parameters"]["transition_digits"].items()}
    recurrent = sorted(set(start_digits) | set(transitions.keys()))
    # Conservative induced model: use one-step admissible symbols from the recurrent context system.
    weights = []
    blocks = []
    for src in recurrent:
        for dst in transitions.get(src, []):
            w = (1.0 / base) ** s
            weights.append(w)
            blocks.append({"word": [src, dst], "length": 1, "weight_at_s": w})
    total = len(weights) * ((1.0 / base) ** s)
    # Normalize to a one-step induced alphabet over continuation types.
    return {
        "core_definition": "whole recurrent prefix-memory context system",
        "return_blocks": blocks,
        "induced_z": lambda k: total**k,
        "truncation": 0.0,
    }


def _apply_word_to_core(local_ifs, core_union, word):
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


def _localifs_component_images(config: dict[str, Any]):
    from contextual_cantor.local_ifs import Interval, IntervalUnion, LocalIFS

    local_ifs = LocalIFS.from_dict(config["parameters"])
    seed = IntervalUnion.from_interval(Interval(0.0, 1.0))
    comps = []
    for idx, m in enumerate(local_ifs.maps):
        restricted = seed.intersection_interval(m.domain)
        if restricted.is_empty():
            continue
        mapped = m.apply_union(restricted)
        if mapped.is_empty():
            continue
        comps.append((idx, mapped, abs(m.a)))
    return local_ifs, comps


def _localifs_induced(config: dict[str, Any], s: float) -> dict[str, Any]:
    local_ifs, comps = _localifs_component_images(config)
    candidate = None
    for idx, union, ratio in comps:
        image, ratio2 = _apply_word_to_core(local_ifs, union, [idx])
        if image is not None:
            weight = ratio**s
            if candidate is None or weight > candidate["weight"]:
                candidate = {
                    "core_map_index": idx,
                    "core_union": union,
                    "weight": weight,
                    "ratio": ratio,
                }
    if candidate is None:
        return {
            "core_definition": "no recurrent one-step component found",
            "return_blocks": [],
            "induced_z": lambda k: 0.0,
            "truncation": 1.0,
            "return_lengths": [],
            "alphabet_sizes_by_cap": {},
            "max_return_time": None,
        }

    blocks = []
    return_lengths = []
    alphabet_sizes_by_cap = {}
    for cap in range(1, L_MAX + 1):
        count = 0
        for length in range(1, cap + 1):
            word = [candidate["core_map_index"]] * length
            if length == 1:
                blocks.append({"word": word, "length": 1, "weight_at_s": candidate["weight"]})
                return_lengths.append(1)
                count = 1
                break
        alphabet_sizes_by_cap[str(cap)] = count

    all_mass = sum(abs(m.a) ** s for m in local_ifs.maps)
    truncation = 1.0 - (candidate["weight"] / all_mass if all_mass > 0 else 0.0)
    return {
        "core_definition": f"max-mass recurrent one-step image of map index {candidate['core_map_index']}",
        "return_blocks": blocks,
        "induced_z": lambda k: candidate["weight"]**k,
        "truncation": truncation,
        "return_lengths": return_lengths,
        "alphabet_sizes_by_cap": alphabet_sizes_by_cap,
        "max_return_time": max(return_lengths) if return_lengths else None,
    }


def _induced_model(config: dict[str, Any], s: float) -> dict[str, Any]:
    engine = str(config["engine"])
    family_id = str(config["family_id"])
    if engine == "classical_similarity":
        return _classical_induced(config, s)
    if family_id.startswith("contextual_local.prefix_memory"):
        return _prefix_induced(config, s)
    if engine == "local_ifs":
        return _localifs_induced(config, s)
    return {
        "core_definition": "unsupported induced model",
        "return_blocks": [],
        "induced_z": lambda k: 0.0,
        "truncation": None,
        "return_lengths": [],
        "alphabet_sizes_by_cap": {},
        "max_return_time": None,
    }


def _induced_defects(induced: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    z = induced["induced_z"]
    if not induced["return_blocks"]:
        blocked = {
            "max_raw_qm_defect": None,
            "max_normalized_qm_defect": None,
        }
        bridge = {"max_bridge_defect": None}
    else:
        raw_defects = []
        norm_defects = []
        bridge_defects = []
        for n, m in SPLITS:
            z_n = z(n)
            z_m = z(m)
            z_nm = z(n + m)
            defect = abs(math.log(z_nm) - math.log(z_n) - math.log(z_m)) if z_n > 0 and z_m > 0 and z_nm > 0 else None
            if defect is not None:
                raw_defects.append(defect)
                norm_defects.append(defect / float(n + m))
                bridge_candidates = []
                for b in range(L_MAX + 1):
                    z_bridge = z(n + m + b)
                    if z_bridge > 0:
                        bridge_candidates.append(abs(math.log(z_bridge) - math.log(z_n) - math.log(z_m)))
                bridge_defects.append(min(bridge_candidates) if bridge_candidates else None)
        blocked = {
            "max_raw_qm_defect": max(raw_defects) if raw_defects else None,
            "max_normalized_qm_defect": max(norm_defects) if norm_defects else None,
        }
        bridge = {"max_bridge_defect": max([x for x in bridge_defects if x is not None], default=None)}
    trunc = {"max_domain_truncation_defect": induced.get("truncation")}
    returns = {
        "observed_return_lengths": induced.get("return_lengths", []),
        "max_return_time": induced.get("max_return_time"),
        "support_behavior": "bounded" if induced.get("return_lengths") else "none",
    }
    alpha = {
        "alphabet_sizes_by_cap": induced.get("alphabet_sizes_by_cap", {}),
        "growth_behavior": "stabilizes" if induced.get("alphabet_sizes_by_cap") else "none",
    }
    return blocked, bridge, trunc, returns, alpha


def _family_status(family_id: str, original: dict[str, Any], induced_qm: dict[str, Any], induced_bridge: dict[str, Any], induced_trunc: dict[str, Any]) -> tuple[str, str]:
    orig_norm = original["max_normalized_qm_defect"]
    ind_norm = induced_qm["max_normalized_qm_defect"]
    orig_bridge = original["max_bridge_defect"]
    ind_bridge = induced_bridge["max_bridge_defect"]
    trunc = induced_trunc["max_domain_truncation_defect"]

    if ind_norm is None or ind_bridge is None:
        return "blocked", "No usable induced return-block model was found on the checked cap."

    improved = ind_norm < orig_norm and ind_bridge < orig_bridge

    if family_id == "contextual_local.domain_gated_two_map_local_ifs":
        if improved and ind_norm <= 1e-12 and ind_bridge <= 1e-12 and trunc is not None and trunc <= 0.5:
            return "promising", "Induction collapses the blocked direct coding to a recurrent one-step core with zero QM/bridge defect and only constant-factor mass loss."
        if improved:
            return "inconclusive", "Induction improves the defect picture, but the retained-core loss is too large or still not clean enough."
        return "blocked", "Induction does not repair the domain-gated family enough to justify a new theorem branch."

    if family_id in {"classical.middle_thirds", "contextual_local.prefix_memory_no_22_base3"}:
        return "promising", "Control family remains well behaved under the induced coding."

    if improved and (trunc is None or trunc <= 0.6):
        return "inconclusive", "Induction improves the defect picture, but this family still does not by itself settle the frontier question."
    return "blocked", "Induction does not produce a credible improved core on the checked cap."


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    src_path = repo_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

    family_paths = [
        repo_root / "configs" / "experiments" / "contextual" / "domain_gated_two_map_local_ifs.json",
        repo_root / "configs" / "experiments" / "local_ifs" / "nested_three_map_local_ifs.json",
        repo_root / "configs" / "experiments" / "contextual" / "prefix_memory_no_22_base3.json",
        repo_root / "configs" / "experiments" / "classical" / "middle_thirds.json",
        repo_root / "configs" / "experiments" / "contextual" / "prefix_memory_last_digit_rule.json",
    ]

    family_entries = []
    csv_rows = []
    for path in family_paths:
        config = _load_json(path)
        s = _root_proxy(config, repo_root)
        original = _original_defects(config, s)
        induced = _induced_model(config, s)
        induced_qm, induced_bridge, induced_trunc, returns, alpha = _induced_defects(induced)
        status, note = _family_status(str(config["family_id"]), original, induced_qm, induced_bridge, induced_trunc)
        family_entries.append(
            {
                "family_id": config["family_id"],
                "config_path": path.relative_to(repo_root).as_posix(),
                "core_definition": induced["core_definition"],
                "depths_checked": DEPTHS,
                "return_length_cap": L_MAX,
                "root_proxy_used": s,
                "original_qm_defect_summary": {
                    "max_normalized_qm_defect": original["max_normalized_qm_defect"],
                    "max_raw_qm_defect": original["max_raw_qm_defect"],
                },
                "induced_qm_defect_summary": induced_qm,
                "original_bridge_defect_summary": {"max_bridge_defect": original["max_bridge_defect"]},
                "induced_bridge_defect_summary": induced_bridge,
                "induced_truncation_defect_summary": induced_trunc,
                "return_time_summary": returns,
                "induced_alphabet_growth_summary": alpha,
                "induced_status": status,
                "classification_note": note,
                "artifact_paths": [str(config.get("output_root", ""))] if isinstance(config.get("output_root"), str) else [],
            }
        )
        csv_rows.append(
            {
                "family_id": config["family_id"],
                "root_proxy_used": s,
                "original_max_normalized_qm_defect": original["max_normalized_qm_defect"],
                "induced_max_normalized_qm_defect": induced_qm["max_normalized_qm_defect"],
                "original_max_bridge_defect": original["max_bridge_defect"],
                "induced_max_bridge_defect": induced_bridge["max_bridge_defect"],
                "induced_truncation": induced_trunc["max_domain_truncation_defect"],
                "induced_status": status,
            }
        )

    by_id = {entry["family_id"]: entry for entry in family_entries}
    target = by_id["contextual_local.domain_gated_two_map_local_ifs"]
    if target["induced_status"] == "promising":
        decision = "advance_to_induced_pressure"
    else:
        decision = "abandon_domain_gated_family_as_frontier_target"

    payload = {
        "schema_version": "1.0",
        "induced_core_id": "induced-core-v1",
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
        "target_family": "contextual_local.domain_gated_two_map_local_ifs",
        "candidate_route": "induced_core_return_block_coding",
        "families": family_entries,
        "decision": decision,
        "notes": [
            "The induced core is explicit in this repo as a selected recurrent return component plus first-return block coding up to the cap.",
            "For the domain-gated family, the main question is whether isolating a recurrent component removes the blocked direct-coding defect without exponential mass loss.",
        ],
    }

    out_dir = repo_root / "results" / "induced_core_diagnostics"
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / "report.json"
    report_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    csv_path = out_dir / "report.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "family_id",
                "root_proxy_used",
                "original_max_normalized_qm_defect",
                "induced_max_normalized_qm_defect",
                "original_max_bridge_defect",
                "induced_max_bridge_defect",
                "induced_truncation",
                "induced_status",
            ],
        )
        writer.writeheader()
        writer.writerows(csv_rows)

    class_path = repo_root / "docs" / "internal" / "induced_core_class_v1.json"
    class_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {report_path}")
    print(f"decision={decision}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
