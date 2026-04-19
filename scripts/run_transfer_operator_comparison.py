#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import time
from pathlib import Path
from typing import Any


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def run() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    src_path = repo_root / "src"
    import sys

    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

    from contextual_cantor.certified_bracketing import certify_config_root
    from contextual_cantor.local_pressure import analyze_config, default_depths_from_config
    from contextual_cantor.transfer_operator import reference_root_for_family, solve_transfer_root

    config_paths = [
        repo_root / "configs" / "experiments" / "classical" / "middle_thirds.json",
        repo_root / "configs" / "experiments" / "finite_state" / "adjacency_no_consecutive_2_base3.json",
        repo_root / "configs" / "experiments" / "classical" / "restricted_digits_base5_024.json",
    ]

    out_dir = repo_root / "results" / "transfer_operator"
    out_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    for cfg_path in config_paths:
        cfg = _load_json(cfg_path)
        if not isinstance(cfg, dict):
            raise ValueError(f"config must be object: {cfg_path}")
        family_id = str(cfg["family_id"])
        status = "ok"
        notes = ""

        t0 = time.perf_counter()
        transfer_root = None
        try:
            transfer_root = solve_transfer_root(cfg, s_min=0.0, s_max=2.0, tol=1e-13, max_iter=300)
        except Exception as exc:  # pragma: no cover - surfaced in status
            status = "transfer_error"
            notes = f"transfer root failed: {exc}"
        runtime_transfer_ms = (time.perf_counter() - t0) * 1000.0

        t1 = time.perf_counter()
        partition_root = None
        try:
            depths = default_depths_from_config(cfg)
            analysis = analyze_config(cfg, depths=depths, s_min=0.0, s_max=2.0, tol=1e-10)
            partition_root = analysis["rows"][-1]["upper_root"]
        except Exception as exc:  # pragma: no cover
            status = "partition_error" if status == "ok" else status
            notes = f"{notes}; partition failed: {exc}".strip("; ")
        runtime_partition_ms = (time.perf_counter() - t1) * 1000.0

        certified_lower = None
        certified_upper = None
        within_certified_interval = None
        try:
            cert = certify_config_root(cfg, precision_dps=80, max_steps=80)
            certified_lower = cert["certified_lower"]
            certified_upper = cert["certified_upper"]
            if transfer_root is not None:
                within_certified_interval = bool(certified_lower <= transfer_root <= certified_upper)
        except Exception:
            certified_lower = None
            certified_upper = None
            within_certified_interval = None

        reference_root = reference_root_for_family(family_id)
        abs_error_transfer = None
        if transfer_root is not None and reference_root is not None:
            abs_error_transfer = abs(float(transfer_root) - float(reference_root))
        abs_error_partition = None
        if partition_root is not None and reference_root is not None:
            abs_error_partition = abs(float(partition_root) - float(reference_root))

        rows.append(
            {
                "family_id": family_id,
                "transfer_root": transfer_root,
                "partition_root": partition_root,
                "certified_lower": certified_lower,
                "certified_upper": certified_upper,
                "reference_root": reference_root,
                "abs_error_transfer": abs_error_transfer,
                "abs_error_partition": abs_error_partition,
                "runtime_ms_transfer": runtime_transfer_ms,
                "runtime_ms_partition": runtime_partition_ms,
                "within_certified_interval": within_certified_interval,
                "status": status,
                "notes": notes,
            }
        )

    csv_path = out_dir / "baseline_comparison.csv"
    json_path = out_dir / "baseline_comparison.json"
    fieldnames = [
        "family_id",
        "transfer_root",
        "partition_root",
        "certified_lower",
        "certified_upper",
        "reference_root",
        "abs_error_transfer",
        "abs_error_partition",
        "runtime_ms_transfer",
        "runtime_ms_partition",
        "within_certified_interval",
        "status",
        "notes",
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    json_path.write_text(json.dumps({"rows": rows}, indent=2, sort_keys=True), encoding="utf-8")
    print(f"wrote {csv_path.relative_to(repo_root)} and {json_path.relative_to(repo_root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
