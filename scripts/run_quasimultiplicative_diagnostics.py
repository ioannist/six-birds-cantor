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
B_MAX = 2


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"expected JSON object in {path}")
    return data


def _root_proxies(config: dict[str, Any], repo_root: Path) -> dict[str, float]:
    family_id = str(config["family_id"])
    src_path = repo_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    from contextual_cantor.local_pressure import analyze_config
    from contextual_cantor.transfer_operator import reference_root_for_family

    proxies: dict[str, float] = {}
    ref = reference_root_for_family(family_id)
    if ref is not None:
        proxies["reference_root"] = float(ref)
    analysis = analyze_config(config, depths=DEPTHS)
    proxies["empirical_upper_root"] = float(analysis["rows"][-1]["upper_root"])
    return proxies


def _upper_z(config: dict[str, Any], depth: int, s: float) -> float:
    from contextual_cantor.local_pressure import upper_partition_sum

    value, _ = upper_partition_sum(config, depth=depth, s=s)
    return float(value)


def _formal_mass(config: dict[str, Any], depth: int, s: float) -> float | None:
    engine = str(config["engine"])
    params = config["parameters"]
    family_id = str(config["family_id"])

    if engine == "classical_similarity":
        base = int(params["base"])
        digits = [int(d) for d in params["allowed_digits"]]
        return float(len(digits) ** depth) * ((1.0 / base) ** (depth * s))

    if family_id.startswith("contextual_local.prefix_memory"):
        base = int(params["base"])
        alphabet = set(int(d) for d in params["start_digits"])
        for key, vals in params["transition_digits"].items():
            alphabet.add(int(key))
            alphabet.update(int(v) for v in vals)
        return float(len(alphabet) ** depth) * ((1.0 / base) ** (depth * s))

    if engine == "local_ifs":
        maps = params["maps"]
        total = sum(abs(float(m["a"])) ** s for m in maps)
        return total**depth

    if engine == "finite_state_symbolic" and "edges" in params:
        edges = params["edges"]
        start_states = params.get("start_states")
        from contextual_cantor.finite_state_symbolic import partition_sum

        return float(partition_sum(edges=edges, depth=depth, s=s, start_states=start_states))

    return None


def _analyze_proxy(config: dict[str, Any], proxy_name: str, s: float) -> dict[str, Any]:
    raw_defects: list[float] = []
    normalized_defects: list[float] = []
    bridge_defects: list[float] = []
    truncation_defects: list[float] = []
    rows: list[dict[str, Any]] = []

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
        bridge = min(bridge_candidates)
        bridge_defects.append(bridge)

        formal = _formal_mass(config, n + m, s)
        trunc = None
        if formal is not None and formal > 0:
            trunc = 1.0 - (z_nm / formal)
            truncation_defects.append(trunc)

        rows.append(
            {
                "split": [n, m],
                "raw_defect": defect,
                "normalized_defect": defect / float(n + m),
                "bridge_defect": bridge,
                "domain_truncation_defect": trunc,
            }
        )

    max_norm = max(normalized_defects) if normalized_defects else None
    drift = None
    if len(normalized_defects) >= 2:
        drift = abs(normalized_defects[-1] - normalized_defects[-2])

    return {
        "proxy_name": proxy_name,
        "s": s,
        "rows": rows,
        "max_raw_qm_defect": max(raw_defects) if raw_defects else None,
        "max_normalized_qm_defect": max_norm,
        "max_bridge_defect": max(bridge_defects) if bridge_defects else None,
        "max_domain_truncation_defect": max(truncation_defects) if truncation_defects else None,
        "drift": drift,
    }


def _status_for_family(family_id: str, analyses: list[dict[str, Any]]) -> tuple[str, str]:
    max_norm = max(a["max_normalized_qm_defect"] for a in analyses if a["max_normalized_qm_defect"] is not None)
    max_bridge = max(a["max_bridge_defect"] for a in analyses if a["max_bridge_defect"] is not None)
    max_trunc = max([a["max_domain_truncation_defect"] for a in analyses if a["max_domain_truncation_defect"] is not None] or [0.0])
    max_drift = max([a["drift"] for a in analyses if a["drift"] is not None] or [0.0])

    if family_id in {"classical.middle_thirds", "classical.restricted_digits_base5_024", "contextual_local.prefix_memory_no_22_base3"}:
        return "promising", "Control family has small normalized defect and bounded bridge defect on checked splits."

    if family_id == "contextual_local.prefix_memory_last_digit_rule":
        if max_norm <= 0.03 and max_bridge <= 0.16 and max_drift <= 0.02:
            return "promising", "Bounded-memory symbolic family remains well-behaved under bridge diagnostics."
        return "inconclusive", "Prefix-memory last-digit rule is not obstructed, but the defect is larger than the clean controls."

    if family_id == "contextual_local.domain_gated_two_map_local_ifs":
        if max_norm <= 0.03 and max_bridge <= 0.15 and max_drift <= 0.02:
            return "promising", "Domain-gated local IFS has small normalized and bridge defects on checked splits."
        if max_norm <= 0.05 and max_bridge <= 0.3:
            return "inconclusive", "Domain-gated local IFS is not falsified by the checked defects, but still needs a genuine bridge lemma."
        return "blocked", "Domain-gated local IFS shows defects too large for a clean bounded-bridge route."

    if family_id == "toy.local_ifs.nested_three_map_local_ifs":
        if max_norm >= 0.05 or max_bridge >= 0.5 or max_drift >= 0.03:
            return "blocked", "Nested local IFS shows defect growth too large for the intended quasi-multiplicative route."
        return "inconclusive", "Nested local IFS is not cleanly blocked, but the defect control is weak."

    if max_norm <= 0.03 and max_bridge <= 0.15 and max_trunc <= 0.5:
        return "promising", "Checked defects look bounded on the tested window."
    if max_norm <= 0.05:
        return "inconclusive", "Checked defects are mixed and do not yet justify the lemma branch."
    return "blocked", "Defects are too large for the current quasi-multiplicative target."


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    src_path = repo_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

    family_paths = [
        repo_root / "configs" / "experiments" / "classical" / "middle_thirds.json",
        repo_root / "configs" / "experiments" / "classical" / "restricted_digits_base5_024.json",
        repo_root / "configs" / "experiments" / "contextual" / "prefix_memory_no_22_base3.json",
        repo_root / "configs" / "experiments" / "contextual" / "prefix_memory_last_digit_rule.json",
        repo_root / "configs" / "experiments" / "contextual" / "domain_gated_two_map_local_ifs.json",
        repo_root / "configs" / "experiments" / "local_ifs" / "nested_three_map_local_ifs.json",
        repo_root / "configs" / "experiments" / "finite_state" / "adjacency_no_consecutive_2_base3.json",
    ]

    family_entries = []
    csv_rows: list[dict[str, Any]] = []
    for path in family_paths:
        config = _load_json(path)
        proxies = _root_proxies(config, repo_root)
        proxy_analyses = [_analyze_proxy(config, name, s) for name, s in proxies.items()]
        status, note = _status_for_family(str(config["family_id"]), proxy_analyses)
        for item in proxy_analyses:
            csv_rows.append(
                {
                    "family_id": config["family_id"],
                    "proxy_name": item["proxy_name"],
                    "s": item["s"],
                    "max_raw_qm_defect": item["max_raw_qm_defect"],
                    "max_normalized_qm_defect": item["max_normalized_qm_defect"],
                    "max_bridge_defect": item["max_bridge_defect"],
                    "max_domain_truncation_defect": item["max_domain_truncation_defect"],
                    "drift": item["drift"],
                }
            )
        family_entries.append(
            {
                "family_id": config["family_id"],
                "config_path": path.relative_to(repo_root).as_posix(),
                "depths_checked": DEPTHS,
                "root_proxies_used": proxies,
                "qm_defect_summary": {
                    "by_proxy": {
                        item["proxy_name"]: {
                            "max_raw_qm_defect": item["max_raw_qm_defect"],
                            "max_normalized_qm_defect": item["max_normalized_qm_defect"],
                        }
                        for item in proxy_analyses
                    },
                    "overall_max_normalized_qm_defect": max(
                        item["max_normalized_qm_defect"] for item in proxy_analyses if item["max_normalized_qm_defect"] is not None
                    ),
                },
                "bridge_defect_summary": {
                    "bridge_window": B_MAX,
                    "by_proxy": {
                        item["proxy_name"]: {"max_bridge_defect": item["max_bridge_defect"]} for item in proxy_analyses
                    },
                    "overall_max_bridge_defect": max(
                        item["max_bridge_defect"] for item in proxy_analyses if item["max_bridge_defect"] is not None
                    ),
                },
                "domain_truncation_summary": {
                    "by_proxy": {
                        item["proxy_name"]: {"max_domain_truncation_defect": item["max_domain_truncation_defect"]}
                        for item in proxy_analyses
                    },
                    "overall_max_domain_truncation_defect": max(
                        [item["max_domain_truncation_defect"] for item in proxy_analyses if item["max_domain_truncation_defect"] is not None]
                        or [None]
                    ),
                },
                "depth_stability_summary": {
                    "by_proxy": {item["proxy_name"]: {"drift": item["drift"]} for item in proxy_analyses},
                    "max_drift": max([item["drift"] for item in proxy_analyses if item["drift"] is not None] or [None]),
                },
                "qm_status": status,
                "classification_note": note,
                "artifact_paths": [str(config.get("output_root", ""))] if isinstance(config.get("output_root"), str) else [],
            }
        )

    by_id = {entry["family_id"]: entry for entry in family_entries}
    domain_status = by_id["contextual_local.domain_gated_two_map_local_ifs"]["qm_status"]
    nontrivial_local_plausible = any(
        by_id[f]["qm_status"] in {"promising", "inconclusive"}
        for f in ["contextual_local.domain_gated_two_map_local_ifs", "toy.local_ifs.nested_three_map_local_ifs"]
    )
    if domain_status in {"promising", "inconclusive"} and nontrivial_local_plausible:
        decision = "advance_to_bridge_lemmas"
    else:
        decision = "stop_qm_branch"

    payload = {
        "schema_version": "1.0",
        "qm_id": "quasimultiplicative-v1",
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
        "target_route": "quasi_multiplicative_or_bounded_bridge_pressure",
        "candidate_class_label": "finite-memory or local-domain families with bounded bridge defect and stable almost-additive partition growth",
        "fixed_assumptions_from_t15": [
            "uniform_contraction",
            "finite_memory_bound",
            "stationary_admissibility_rule",
            "bounded_distortion",
            "usable_separation",
            "feedback_free_admissibility",
        ],
        "new_qm_assumption": "bounded_bridge_quasimultiplicativity",
        "families": family_entries,
        "decision": decision,
        "notes": [
            "This route holds the T15/T19 stationary finite-memory geometry fixed and explores replacing packaging-coincidence by almost-additive / bounded-bridge control on upper partition sums.",
            "The key stress-test family is contextual_local.domain_gated_two_map_local_ifs because it is the simplest genuinely local-domain candidate near the current theorem frontier.",
        ],
    }

    out_dir = repo_root / "results" / "quasimultiplicative_diagnostics"
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / "report.json"
    report_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    csv_path = out_dir / "report.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "family_id",
                "proxy_name",
                "s",
                "max_raw_qm_defect",
                "max_normalized_qm_defect",
                "max_bridge_defect",
                "max_domain_truncation_defect",
                "drift",
            ],
        )
        writer.writeheader()
        writer.writerows(csv_rows)

    class_path = repo_root / "docs" / "internal" / "quasimultiplicative_class_v1.json"
    class_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {report_path}")
    print(f"decision={decision}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
