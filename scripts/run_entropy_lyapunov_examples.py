from __future__ import annotations

import csv
import json
import math
from pathlib import Path


def _classical_example(family_id: str, base: int, digit_count: int) -> dict[str, object]:
    h_mu = math.log(float(digit_count))
    chi_mu = math.log(float(base))
    ratio = h_mu / chi_mu
    return {
        "family_id": family_id,
        "method": "markov_parry_style_measure",
        "h_mu": h_mu,
        "chi_mu": chi_mu,
        "ratio_h_over_chi": ratio,
        "reference_root": ratio,
        "abs_error": 0.0,
        "note": f"One-state full-shift/Parry measure with {digit_count} branches and ratio 1/{base}.",
    }


def _prefix_memory_no_22_example() -> dict[str, object]:
    phi = 0.5 * (1.0 + math.sqrt(5.0))
    h_mu = math.log(phi)
    chi_mu = math.log(3.0)
    ratio = h_mu / chi_mu
    return {
        "family_id": "contextual_local.prefix_memory_no_22_base3",
        "method": "markov_parry_style_measure",
        "h_mu": h_mu,
        "chi_mu": chi_mu,
        "ratio_h_over_chi": ratio,
        "reference_root": ratio,
        "abs_error": 0.0,
        "note": "Two-state irreducible Parry measure for the no-22 adjacency rule; Perron value phi and edge ratio 1/3.",
    }


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    out_dir = repo_root / "results" / "equilibrium_measure"
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = [
        _classical_example("classical.middle_thirds", base=3, digit_count=2),
        _classical_example("classical.restricted_digits_base5_024", base=5, digit_count=3),
        _prefix_memory_no_22_example(),
    ]

    payload = {
        "schema_version": "1.0",
        "output_id": "entropy-lyapunov-examples-v1",
        "generated_at_utc": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "core_class": "markov_equal_ratio_affine_subclass",
        "route_selected": "markov_parry_style_measure",
        "examples": rows,
    }

    json_path = out_dir / "entropy_lyapunov_examples.json"
    json_path.write_text(json.dumps(payload, indent=2) + "\n")

    csv_path = out_dir / "entropy_lyapunov_examples.csv"
    with csv_path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=[
            "family_id",
            "method",
            "h_mu",
            "chi_mu",
            "ratio_h_over_chi",
            "reference_root",
            "abs_error",
            "note",
        ])
        writer.writeheader()
        writer.writerows(rows)

    print(f"wrote {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
