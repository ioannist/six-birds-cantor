#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


def canonical_json_sha256(data: Any) -> str:
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _family_slug(family_id: str) -> str:
    return family_id.split(".")[-1].replace("_", "-")


def run(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run certified contextual/local prototype on equal-ratio digit-transition families.")
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--precision-dps", type=int, default=90)
    parser.add_argument("--perron-steps", type=int, default=40)
    args = parser.parse_args(argv)

    script_path = Path(__file__).resolve()
    repo_root = script_path.parent.parent
    src_path = repo_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

    from contextual_cantor.contextual_certification import certify_markov_equal_ratio_dimension

    config_path = args.config if args.config.is_absolute() else (Path.cwd() / args.config)
    config_path = config_path.resolve()
    config = json.loads(config_path.read_text(encoding="utf-8"))

    family_id = str(config["family_id"])
    out_dir = repo_root / "results" / "certified_contextual" / _family_slug(family_id)
    out_dir.mkdir(parents=True, exist_ok=True)

    payload = certify_markov_equal_ratio_dimension(
        config,
        perron_steps=int(args.perron_steps),
        precision_dps=int(args.precision_dps),
    )

    interval_path = out_dir / "certified_interval.json"
    interval_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    config_rel = config_path.relative_to(repo_root).as_posix()
    interval_rel = interval_path.relative_to(repo_root).as_posix()
    run_id = f"{_family_slug(family_id)}-certified-contextual-dps{args.precision_dps}-steps{args.perron_steps}"

    manifest = {
        "schema_version": "1.0",
        "run_id": run_id,
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
            {"path": interval_rel, "kind": "certified_interval_json"},
        ],
        "summary_metrics": {
            "certified_lower": payload["certified_lower"],
            "certified_upper": payload["certified_upper"],
            "certified_width": payload["certified_width"],
            "reference_root": payload["reference_root"],
            "contains_reference_root": payload["contains_reference_root"],
            "rho_lower": payload["rho_lower"],
            "rho_upper": payload["rho_upper"],
            "precision_dps": payload["precision_dps"],
            "perron_steps": payload["perron_steps"],
            "method_backend": payload["method_backend"],
        },
        "command": f"python {script_path.relative_to(repo_root).as_posix()} --config {config_rel} --precision-dps {args.precision_dps} --perron-steps {args.perron_steps}",
        "exit_status": 0,
        "warnings": [],
        "notes": "Prototype supports only digit-transition Markov, equal ratio (1/base), affine-map families.",
        "environment": {"python": sys.version.split()[0]},
    }

    manifest_path = out_dir / "result_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")

    print(
        f"family={family_id} interval=[{payload['certified_lower']:.16f},{payload['certified_upper']:.16f}] "
        f"width={payload['certified_width']:.3e} steps={payload['perron_steps']} dps={payload['precision_dps']} "
        f"contains_ref={payload['contains_reference_root']} manifest={manifest_path}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
