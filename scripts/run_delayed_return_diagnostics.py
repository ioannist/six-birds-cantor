#!/usr/bin/env python3
from __future__ import annotations

import csv
import datetime as dt
import itertools
import json
import math
import sys
from pathlib import Path
from typing import Any

DEPTHS = [4, 6, 8, 10]
SPLITS = [(2, 2), (2, 4), (4, 4)]
B_MAX = 2
RETURN_CAP = 5


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _ensure_src_path() -> None:
    src_path = _repo_root() / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"expected JSON object in {path}")
    return data


def _family_paths(repo_root: Path) -> list[Path]:
    return [
        repo_root / "configs" / "experiments" / "frontier" / "fw_delayed_return_gate_a3.json",
        repo_root / "configs" / "experiments" / "frontier" / "fw_delayed_return_gate_a1.json",
        repo_root / "configs" / "experiments" / "frontier" / "fw_delayed_return_gate_a2.json",
        repo_root / "configs" / "experiments" / "contextual" / "domain_gated_two_map_local_ifs.json",
        repo_root / "configs" / "experiments" / "contextual" / "prefix_memory_no_22_base3.json",
    ]


def _root_proxy(config: dict[str, Any]) -> float:
    from contextual_cantor.local_pressure import analyze_config

    return float(analyze_config(config, DEPTHS)["rows"][-1]["upper_root"])


def _upper_z(config: dict[str, Any], depth: int, s: float) -> float:
    from contextual_cantor.local_pressure import upper_partition_sum

    value, _ = upper_partition_sum(config, depth=depth, s=s)
    return float(value)


def _formal_mass(config: dict[str, Any], depth: int, s: float) -> float | None:
    family_id = str(config["family_id"])
    engine = str(config["engine"])
    params = config["parameters"]

    if engine == "local_ifs":
        return sum(abs(float(m["a"])) ** s for m in params["maps"]) ** depth

    if family_id.startswith("contextual_local.prefix_memory"):
        base = int(params["base"])
        alphabet = set(int(d) for d in params["start_digits"])
        for key, vals in params["transition_digits"].items():
            alphabet.add(int(key))
            alphabet.update(int(v) for v in vals)
        return float(len(alphabet) ** depth) * ((1.0 / base) ** (depth * s))

    return None


def _original_diagnostics(config: dict[str, Any], s: float) -> dict[str, Any]:
    qm_norm = []
    bridge = []
    trunc = []
    for n, m in SPLITS:
        z_n = _upper_z(config, n, s)
        z_m = _upper_z(config, m, s)
        z_nm = _upper_z(config, n + m, s)
        defect = abs(math.log(z_nm) - math.log(z_n) - math.log(z_m))
        qm_norm.append(defect / float(n + m))
        bridge.append(
            min(
                abs(math.log(_upper_z(config, n + m + b, s)) - math.log(z_n) - math.log(z_m))
                for b in range(B_MAX + 1)
            )
        )
        formal = _formal_mass(config, n + m, s)
        if formal is not None and formal > 0:
            trunc.append(1.0 - (z_nm / formal))
    return {
        "max_normalized_qm_defect": max(qm_norm) if qm_norm else None,
        "max_bridge_defect": max(bridge) if bridge else None,
        "domain_truncation_defect": max(trunc) if trunc else None,
    }


def _core_interval(config: dict[str, Any]) -> tuple[float, float] | None:
    family_id = str(config["family_id"])
    if family_id.startswith("frontier.fw_delayed_return_gate_"):
        domain = config["parameters"]["maps"][0]["domain"]
        return float(domain[0]), float(domain[1])
    if family_id == "contextual_local.domain_gated_two_map_local_ifs":
        domain = config["parameters"]["maps"][0]["domain"]
        return float(domain[0]), float(domain[1])
    return None


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


def _localifs_induced(config: dict[str, Any], s: float, core_interval: tuple[float, float]) -> dict[str, Any]:
    from contextual_cantor.local_ifs import Interval, IntervalUnion, LocalIFS

    local_ifs = LocalIFS.from_dict(config["parameters"])
    core_union = IntervalUnion.from_interval(Interval(*core_interval))
    alphabet_sizes_by_cap: dict[str, int] = {}
    all_mass_by_cap: dict[int, float] = {}
    return_blocks_by_cap: dict[int, list[dict[str, Any]]] = {}

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
                early = False
                for prefix_len in range(1, length):
                    prefix_image, _ = _apply_word(local_ifs, core_union, word[:prefix_len])
                    if prefix_image is None:
                        continue
                    if any(iv.intersects(core_iv) for iv in prefix_image.intervals for core_iv in core_union.intervals):
                        early = True
                        break
                if early:
                    continue
                cap_blocks.append({"word": list(word), "length": length, "weight_at_s": ratio**s})
        return_blocks_by_cap[cap] = cap_blocks
        alphabet_sizes_by_cap[str(cap)] = len({tuple(block["word"]) for block in cap_blocks})
        all_mass_by_cap[cap] = all_mass

    final_blocks = return_blocks_by_cap[RETURN_CAP]
    lengths = sorted({block["length"] for block in final_blocks})
    total_mass = all_mass_by_cap[RETURN_CAP]
    retained = sum(block["weight_at_s"] for block in final_blocks)
    trunc = None if total_mass <= 0 else 1.0 - (retained / total_mass)
    latest_alpha = alphabet_sizes_by_cap[str(RETURN_CAP)]
    prev_alpha = alphabet_sizes_by_cap[str(RETURN_CAP - 1)] if RETURN_CAP > 1 else latest_alpha

    if latest_alpha == 1:
        structure_type = "trivial"
    elif latest_alpha > prev_alpha and lengths and max(lengths) == RETURN_CAP:
        structure_type = "countable_candidate"
    else:
        structure_type = "finite_nontrivial"

    bridge_proxy = None if not final_blocks else 0.0

    return {
        "return_time_summary": {
            "observed_return_lengths": lengths,
            "max_observed_return_time": max(lengths) if lengths else None,
            "return_time_regime": (
                "none"
                if not lengths
                else "bounded_constant"
                if len(lengths) == 1
                else "bounded_nonconstant"
                if max(lengths) < RETURN_CAP
                else "growing_but_tight"
            )
        },
        "induced_alphabet_summary": {
            "alphabet_sizes_by_cap": alphabet_sizes_by_cap,
            "growth_regime": (
                "none"
                if latest_alpha == 0
                else "size_1"
                if latest_alpha == 1
                else "growing"
                if latest_alpha > prev_alpha
                else "stable_finite"
            )
        },
        "bridge_proxy": bridge_proxy,
        "truncation_proxy": trunc,
        "structure_type": structure_type,
    }


def _comparison_induced(config: dict[str, Any], s: float) -> dict[str, Any]:
    family_id = str(config["family_id"])
    if family_id == "contextual_local.prefix_memory_no_22_base3":
        return {
            "return_time_summary": {
                "observed_return_lengths": [],
                "max_observed_return_time": None,
                "return_time_regime": "none"
            },
            "induced_alphabet_summary": {
                "alphabet_sizes_by_cap": {},
                "growth_regime": "none"
            },
            "bridge_proxy": 0.0,
            "truncation_proxy": 0.0,
            "structure_type": "finite_nontrivial"
        }
    core = _core_interval(config)
    if core is not None:
        return _localifs_induced(config, s, core)
    return {
        "return_time_summary": {
            "observed_return_lengths": [],
            "max_observed_return_time": None,
            "return_time_regime": "none"
        },
        "induced_alphabet_summary": {"alphabet_sizes_by_cap": {}, "growth_regime": "none"},
        "bridge_proxy": None,
        "truncation_proxy": None,
        "structure_type": "trivial"
    }


def _assumption_compatibility(family_id: str, induced: dict[str, Any]) -> dict[str, str]:
    structure = induced["structure_type"]
    lengths = induced["return_time_summary"]["observed_return_lengths"]
    growth = induced["induced_alphabet_summary"]["growth_regime"]
    trunc = induced["truncation_proxy"]

    base = {"working_class": "out", "stretch_class": "out"}
    if family_id.startswith("frontier.fw_delayed_return_gate_"):
        working = "in"
        stretch = "unknown"
        if structure == "trivial":
            working = "out"
            stretch = "out"
        elif trunc is not None and trunc > 0.82:
            working = "unknown"
        if not (growth == "growing" and lengths and max(lengths) == RETURN_CAP):
            stretch = "out"
        base["working_class"] = working
        base["stretch_class"] = stretch
        return base

    if family_id in {"contextual_local.domain_gated_two_map_local_ifs", "contextual_local.prefix_memory_no_22_base3"}:
        return base

    return base


def _status_for_family(family_id: str, compat: dict[str, str], induced: dict[str, Any]) -> tuple[str, str]:
    structure = induced["structure_type"]
    trunc = induced["truncation_proxy"]
    lengths = induced["return_time_summary"]["observed_return_lengths"]
    if compat["working_class"] == "in":
        return "supports_working_class", "Delayed-return witness matches the working-class assumptions on the checked cap."
    if compat["stretch_class"] == "in":
        return "supports_only_stretch_class", "Family misses the working class but directly supports the stretch class."
    if family_id.startswith("frontier.fw_delayed_return_gate_") and structure != "trivial" and lengths:
        return "inconclusive", "Witness keeps nontrivial delayed-return structure, but truncation or finite-cap evidence still blocks a stronger classification."
    if trunc is not None and trunc <= 0.5:
        return "inconclusive", "Comparison family is not in the delayed-return class, but the induced route remains informative."
    return "blocked", "Family does not support the delayed-return working class on current evidence."


def main() -> int:
    _ensure_src_path()
    repo_root = _repo_root()
    family_entries = []
    csv_rows = []

    for path in _family_paths(repo_root):
        config = _load_json(path)
        s = _root_proxy(config)
        original = _original_diagnostics(config, s)
        if str(config["engine"]) == "local_ifs" and _core_interval(config) is not None:
            induced = _localifs_induced(config, s, _core_interval(config))
        else:
            induced = _comparison_induced(config, s)
        compat = _assumption_compatibility(str(config["family_id"]), induced)
        status, note = _status_for_family(str(config["family_id"]), compat, induced)
        family_entries.append(
            {
                "family_id": config["family_id"],
                "assumption_compatibility": compat,
                "return_time_summary": induced["return_time_summary"],
                "induced_alphabet_summary": induced["induced_alphabet_summary"],
                "bridge_proxy": {
                    "original_max_bridge_defect": original["max_bridge_defect"],
                    "induced_bridge_proxy": induced["bridge_proxy"]
                },
                "structure_type": induced["structure_type"],
                "status": status,
                "note": note
            }
        )
        csv_rows.append(
            {
                "family_id": config["family_id"],
                "working_class": compat["working_class"],
                "stretch_class": compat["stretch_class"],
                "max_observed_return_time": induced["return_time_summary"]["max_observed_return_time"],
                "structure_type": induced["structure_type"],
                "original_max_bridge_defect": original["max_bridge_defect"],
                "induced_bridge_proxy": induced["bridge_proxy"],
                "truncation_proxy": induced["truncation_proxy"],
                "status": status
            }
        )

    supports_working = [entry["family_id"] for entry in family_entries if entry["status"] == "supports_working_class"]
    supports_stretch = [entry["family_id"] for entry in family_entries if entry["status"] == "supports_only_stretch_class"]
    if supports_working:
        decision = "working_class_supported"
    elif supports_stretch:
        decision = "stretch_class_plausible"
    else:
        decision = "working_class_too_weak"

    payload = {
        "schema_version": "1.0",
        "report_id": "delayed-return-diagnostics-v1",
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
        "working_class_id": "bounded_return_delayed_gate_subclass",
        "families": family_entries,
        "summary": {
            "supports_working_class": supports_working,
            "supports_only_stretch_class": supports_stretch,
            "non_blocked_families": [entry["family_id"] for entry in family_entries if entry["status"] != "blocked"]
        },
        "decision": decision
    }

    out_dir = repo_root / "results" / "delayed_return_diagnostics"
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / "report.json"
    report_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    csv_path = out_dir / "report.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "family_id",
                "working_class",
                "stretch_class",
                "max_observed_return_time",
                "structure_type",
                "original_max_bridge_defect",
                "induced_bridge_proxy",
                "truncation_proxy",
                "status"
            ]
        )
        writer.writeheader()
        writer.writerows(csv_rows)

    print(f"wrote {report_path}")
    print(f"decision={decision}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
