#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


def canonical_json_sha256(data: Any) -> str:
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _parse_settings(raw: str) -> list[tuple[int, int]]:
    out: list[tuple[int, int]] = []
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        if ":" not in part:
            raise ValueError(f"invalid settings entry '{part}', expected dps:max_steps")
        dps_s, steps_s = part.split(":", 1)
        out.append((int(dps_s), int(steps_s)))
    if not out:
        raise ValueError("at least one settings pair required")
    return out


def run(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run certified bracketing prototype on supported baselines.")
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--precision-dps", type=int, default=80)
    parser.add_argument("--max-steps", type=int, default=80)
    parser.add_argument("--s-min", type=float, default=0.0)
    parser.add_argument("--s-max", type=float, default=2.0)
    parser.add_argument(
        "--settings",
        type=str,
        default="",
        help="Optional comma list dps:max_steps, e.g. 60:40,120:90 (overrides single setting).",
    )
    args = parser.parse_args(argv)

    script_path = Path(__file__).resolve()
    repo_root = script_path.parent.parent
    src_path = repo_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

    from contextual_cantor.certified_bracketing import certify_config_root
    from contextual_cantor.local_pressure import analyze_config, default_depths_from_config

    config_path = args.config if args.config.is_absolute() else (Path.cwd() / args.config)
    config_path = config_path.resolve()
    config = json.loads(config_path.read_text(encoding="utf-8"))
    if not isinstance(config, dict):
        raise ValueError("config JSON must be object")

    experiment_id = str(config["experiment_id"])
    family_id = str(config["family_id"])
    out_dir = repo_root / "results" / "certified_bracketing" / experiment_id
    out_dir.mkdir(parents=True, exist_ok=True)

    settings = (
        _parse_settings(args.settings)
        if args.settings.strip()
        else [(int(args.precision_dps), int(args.max_steps))]
    )

    nonrig_depths = default_depths_from_config(config)
    nonrig = analyze_config(config, depths=nonrig_depths, s_min=args.s_min, s_max=args.s_max)
    nonrig_estimate = nonrig["rows"][-1]["upper_root"]

    rows: list[dict[str, Any]] = []
    for precision_dps, max_steps in settings:
        cert = certify_config_root(
            config,
            precision_dps=precision_dps,
            max_steps=max_steps,
            s_min=args.s_min,
            s_max=args.s_max,
        )
        cert["nonrigorous_estimate"] = nonrig_estimate
        rows.append(cert)

        run_id = f"{experiment_id}-certified-dps{precision_dps}-steps{max_steps}"
        settings_json_path = out_dir / f"{run_id}_certified.json"
        settings_json_path.write_text(json.dumps(cert, indent=2, sort_keys=True), encoding="utf-8")

    summary_csv = out_dir / "certified_settings_summary.csv"
    all_rows: list[dict[str, Any]] = []
    for p in sorted(out_dir.glob(f"{experiment_id}-certified-dps*-steps*_certified.json")):
        data = json.loads(p.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            all_rows.append(data)
    all_rows_sorted = sorted(all_rows, key=lambda r: (int(r["precision_dps"]), int(r["max_steps"])))

    with summary_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "family_id",
                "precision_dps",
                "max_steps",
                "certified_lower",
                "certified_upper",
                "certified_width",
                "nonrigorous_estimate",
                "reference_root",
                "contains_reference_root",
                "certification_method",
                "function_backend",
                "route",
            ],
        )
        writer.writeheader()
        for row in all_rows_sorted:
            writer.writerow({k: row.get(k) for k in writer.fieldnames})

    latest = rows[-1]
    latest_dps = int(latest["precision_dps"])
    latest_steps = int(latest["max_steps"])
    run_id_latest = f"{experiment_id}-certified-dps{latest_dps}-steps{latest_steps}"

    manifest_path = out_dir / "result_manifest.json"
    config_rel = config_path.relative_to(repo_root).as_posix()
    summary_rel = summary_csv.relative_to(repo_root).as_posix()
    latest_json_rel = (out_dir / f"{run_id_latest}_certified.json").relative_to(repo_root).as_posix()

    manifest = {
        "schema_version": "1.0",
        "run_id": run_id_latest,
        "timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
        "status": "success",
        "code_version": "UNSET",
        "config_path": config_rel,
        "config_hash_method": "sha256-json-canonical-v1",
        "config_hash_sha256": canonical_json_sha256(config),
        "family_id": family_id,
        "engine": config["engine"],
        "parameters": config["parameters"],
        "artifacts": [
            {"path": latest_json_rel, "kind": "certified_interval_json"},
            {"path": summary_rel, "kind": "certified_settings_csv"},
        ],
        "summary_metrics": {
            "certified_lower": latest["certified_lower"],
            "certified_upper": latest["certified_upper"],
            "certified_width": latest["certified_width"],
            "nonrigorous_estimate": latest["nonrigorous_estimate"],
            "reference_root": latest["reference_root"],
            "contains_reference_root": latest["contains_reference_root"],
            "certification_method": latest["certification_method"],
            "precision_dps": latest["precision_dps"],
            "max_steps": latest["max_steps"],
        },
        "command": f"python {script_path.relative_to(repo_root).as_posix()} --config {config_rel}",
        "exit_status": 0,
        "warnings": [],
        "notes": (
            "Prototype: finite_state.adjacency_no_consecutive_2_base3 uses baseline-specific "
            "phi*3^{-s}-1 reduction; non-iv fallback uses conservative outward margins."
        ),
        "environment": {"python": sys.version.split()[0]},
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")

    print(
        f"family={family_id} dps={latest_dps} steps={latest_steps} "
        f"interval=[{latest['certified_lower']:.16f},{latest['certified_upper']:.16f}] "
        f"width={latest['certified_width']:.3e} contains_ref={latest['contains_reference_root']} "
        f"nonrig={nonrig_estimate} manifest={manifest_path}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
