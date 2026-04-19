#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def canonical_json_sha256(data: Any) -> str:
    if not isinstance(data, dict):
        raise ValueError("config must be a top-level JSON object")
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def plot_interval_union(intervals: list[tuple[float, float]], out_path: Path, title: str) -> None:
    fig, ax = plt.subplots(figsize=(10, 1.8))
    y = 0.5
    for left, right in intervals:
        ax.plot([left, right], [y, y], color="#2ca02c", linewidth=3, solid_capstyle="butt")
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.0)
    ax.set_yticks([])
    ax.set_xlabel("x")
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def run(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run toy local-IFS config.")
    parser.add_argument("--config", required=True, type=Path, help="Path to local-IFS config JSON.")
    args = parser.parse_args(argv)

    script_path = Path(__file__).resolve()
    repo_root = script_path.parent.parent
    config_path = args.config if args.config.is_absolute() else (Path.cwd() / args.config)
    config_path = config_path.resolve()

    src_path = repo_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    from contextual_cantor.local_ifs import LocalIFS, iterate_set, is_word_admissible

    config = json.loads(config_path.read_text(encoding="utf-8"))
    if not isinstance(config, dict):
        raise ValueError("config must be a JSON object")
    parameters = config.get("parameters", {})
    if not isinstance(parameters, dict):
        raise ValueError("parameters must be an object")

    local_ifs = LocalIFS.from_dict(parameters)
    iterations = int(parameters.get("iterations", 8))
    history = iterate_set(local_ifs=local_ifs, steps=iterations)

    final_union = history[-1]
    prev_union = history[-2] if len(history) >= 2 else history[-1]
    final_count = len(final_union.intervals)
    final_total_length = final_union.total_length
    last_delta = final_total_length - prev_union.total_length

    examples = parameters.get("admissibility_examples", [])
    admissibility_summary = None
    if isinstance(examples, list) and examples:
        example_word = [int(i) for i in examples[0]]
        admissibility_summary = is_word_admissible(local_ifs, example_word)
    else:
        admissibility_summary = is_word_admissible(local_ifs, [0])
        example_word = [0]

    output_root = repo_root / str(config["output_root"])
    output_root.mkdir(parents=True, exist_ok=True)
    run_id = f"{config['experiment_id']}-run-0001"

    png_path = output_root / f"{run_id}_final_union.png"
    plot_interval_union(
        [(iv.left, iv.right) for iv in final_union.intervals],
        png_path,
        f"{config['family_id']} (steps={iterations})",
    )

    config_rel = config_path.relative_to(repo_root).as_posix()
    png_rel = png_path.relative_to(repo_root).as_posix()
    manifest = {
        "schema_version": "1.0",
        "run_id": run_id,
        "timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
        "status": "success",
        "code_version": "UNSET",
        "config_path": config_rel,
        "config_hash_method": "sha256-json-canonical-v1",
        "config_hash_sha256": canonical_json_sha256(config),
        "family_id": config["family_id"],
        "engine": config["engine"],
        "parameters": parameters,
        "artifacts": [{"path": png_rel, "kind": "interval_union_plot"}],
        "summary_metrics": {
            "iteration_count": iterations,
            "final_interval_count": final_count,
            "final_total_length": final_total_length,
            "last_step_total_length_delta": last_delta,
            "admissibility_example_word": example_word,
            "admissibility_example_result": admissibility_summary,
        },
        "command": f"python {script_path.relative_to(repo_root).as_posix()} --config {config_rel}",
        "exit_status": 0,
        "warnings": [],
        "notes": None,
        "environment": {"python": sys.version.split()[0]},
    }

    manifest_path = output_root / "result_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")

    print(
        f"run_id={run_id} family={config['family_id']} "
        f"final_intervals={final_count} final_total_length={final_total_length:.12f} "
        f"manifest={manifest_path}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
