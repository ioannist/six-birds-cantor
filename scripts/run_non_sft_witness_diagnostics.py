#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
from typing import Any


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"expected JSON object in {path}")
    return data


def _prefix_transition_diagnostics(config: dict[str, Any]) -> dict[str, Any]:
    params = config["parameters"]
    start_digits = [int(x) for x in params["start_digits"]]
    transitions = {str(k): tuple(int(v) for v in vals) for k, vals in params["transition_digits"].items()}
    reachable = set(str(x) for x in start_digits)
    frontier = list(reachable)
    while frontier:
        state = frontier.pop()
        for nxt in transitions.get(state, ()):
            nxt_s = str(nxt)
            if nxt_s not in reachable:
                reachable.add(nxt_s)
                frontier.append(nxt_s)
    signature_map = {state: list(transitions.get(state, ())) for state in sorted(reachable)}
    return {
        "diagnostic_type": "finite_state_transition_signatures",
        "reachable_state_count": len(reachable),
        "reachable_states": sorted(reachable),
        "continuation_signatures": signature_map,
        "stabilization_note": "Finite continuation-type set is explicit in the config transition table.",
    }


def _family_status(family_id: str, bowen: dict[str, Any]) -> dict[str, str]:
    if family_id in bowen["included_families"]:
        return {"in_class_status": "yes", "bucket": "included"}
    if family_id in bowen["excluded_families"]:
        return {"in_class_status": "no", "bucket": "excluded"}
    if family_id in bowen.get("not_claimed_families", []):
        return {"in_class_status": "unknown", "bucket": "not_claimed"}
    return {"in_class_status": "unknown", "bucket": "unlisted"}


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    bowen = _load_json(repo_root / "docs" / "internal" / "bowen_class_v1.json")

    candidates = [
        ("contextual_local.domain_gated_two_map_local_ifs", repo_root / "configs" / "experiments" / "contextual" / "domain_gated_two_map_local_ifs.json"),
        ("toy.local_ifs.nested_three_map_local_ifs", repo_root / "configs" / "experiments" / "local_ifs" / "nested_three_map_local_ifs.json"),
        ("contextual_local.prefix_memory_no_22_base3", repo_root / "configs" / "experiments" / "contextual" / "prefix_memory_no_22_base3.json"),
        ("contextual_local.prefix_memory_last_digit_rule", repo_root / "configs" / "experiments" / "contextual" / "prefix_memory_last_digit_rule.json"),
    ]

    rows: list[dict[str, Any]] = []
    for family_id, path in candidates:
        config = _load_json(path)
        status = _family_status(family_id, bowen)
        row: dict[str, Any] = {
            "family_id": family_id,
            "config_path": path.relative_to(repo_root).as_posix(),
            "in_class_status": status["in_class_status"],
            "class_bucket": status["bucket"],
            "engine": config["engine"],
        }
        if family_id.startswith("contextual_local.prefix_memory"):
            row["support"] = _prefix_transition_diagnostics(config)
        else:
            row["support"] = {
                "diagnostic_type": "class_membership_only",
                "note": "No finite-state obstruction diagnostic attempted because this family is not currently in the T19 proved class.",
            }
        rows.append(row)

    out_dir = repo_root / "results" / "non_sft_witness"
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "1.0",
        "report_id": "non-sft-witness-diagnostics-v1",
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
        "target_class_id": bowen["proved_class_id"],
        "families": rows,
    }
    out_path = out_dir / "witness_report.json"
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
