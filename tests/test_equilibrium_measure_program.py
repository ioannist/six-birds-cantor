import json
import math
from pathlib import Path
import subprocess
import sys


def test_equilibrium_measure_program_outputs() -> None:
    note_path = Path("docs/internal/equilibrium_measure_program_v1.md")
    assert note_path.exists()

    subprocess.run([sys.executable, "scripts/run_entropy_lyapunov_examples.py"], check=True)

    output_path = Path("results/equilibrium_measure/entropy_lyapunov_examples.json")
    assert output_path.exists()

    payload = json.loads(output_path.read_text())
    assert payload["route_selected"] in {
        "explicit_cylinder_gibbs_measure",
        "markov_parry_style_measure",
        "thermodynamic_limit_construction",
    }

    examples = payload["examples"]
    assert len(examples) >= 2
    by_family = {row["family_id"]: row for row in examples}

    mt = by_family["classical.middle_thirds"]
    expected_mt = math.log(2.0) / math.log(3.0)
    assert abs(mt["ratio_h_over_chi"] - expected_mt) < 1e-10

    b5 = by_family["classical.restricted_digits_base5_024"]
    expected_b5 = math.log(3.0) / math.log(5.0)
    assert abs(b5["ratio_h_over_chi"] - expected_b5) < 1e-10

    assert "contextual_local.prefix_memory_no_22_base3" in by_family
