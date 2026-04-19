#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def run(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate contextual-family configs and snapshots.")
    parser.parse_args(argv)

    script_path = Path(__file__).resolve()
    repo_root = script_path.parent.parent
    src_path = repo_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

    from contextual_cantor.contextual_family_constructors import (
        build_domain_gated_two_map_local_ifs,
        build_prefix_memory_last_digit_rule,
        build_prefix_memory_no_22_base3,
        build_stage_dependent_alternating_removal,
        sample_stage_snapshot,
        write_experiment_config,
    )

    configs_dir = repo_root / "configs" / "experiments" / "contextual"
    snapshots_dir = repo_root / "results" / "contextual_family_samples"
    configs_dir.mkdir(parents=True, exist_ok=True)
    snapshots_dir.mkdir(parents=True, exist_ok=True)

    generated = [
        ("prefix_memory_last_digit_rule.json", build_prefix_memory_last_digit_rule()),
        ("prefix_memory_no_22_base3.json", build_prefix_memory_no_22_base3()),
        ("domain_gated_two_map_local_ifs.json", build_domain_gated_two_map_local_ifs()),
        ("stage_dependent_alternating_removal.json", build_stage_dependent_alternating_removal()),
    ]

    for filename, cfg in generated:
        config_path = configs_dir / filename
        write_experiment_config(cfg, config_path)
        png_path, metrics = sample_stage_snapshot(cfg, snapshots_dir)
        sidecar = snapshots_dir / f"{cfg['experiment_id']}_snapshot.json"
        sidecar.write_text(
            json.dumps(
                {
                    "family_id": cfg["family_id"],
                    "config_path": config_path.relative_to(repo_root).as_posix(),
                    "snapshot_png": png_path.relative_to(repo_root).as_posix(),
                    "metrics": metrics,
                },
                indent=2,
                sort_keys=True,
            ),
            encoding="utf-8",
        )
        print(
            f"generated family={cfg['family_id']} "
            f"config={config_path.relative_to(repo_root).as_posix()} "
            f"snapshot={png_path.relative_to(repo_root).as_posix()}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(run())
