import json
from pathlib import Path


DELTA_PATH = Path("docs/internal/contribution_delta_map_v1.json")
RISK_PATH = Path("docs/internal/publication_risk_audit_v1.json")


def load_json(path: Path):
    return json.loads(path.read_text())


def test_delta_map_and_risk_audit_exist_and_cover_required_items():
    assert DELTA_PATH.exists()
    assert RISK_PATH.exists()

    delta = load_json(DELTA_PATH)
    risk = load_json(RISK_PATH)

    assert len(delta["contributions"]) >= 10
    contribution_ids = {item["contribution_id"] for item in delta["contributions"]}
    required = {
        "continuous_full_loop_lawfulness_theoremlet",
        "cocycle_pressure_closure_theoremlet",
        "strict_theory_extension_theoremlet",
        "conditional_pressure_disintegration_theoremlet",
    }
    assert required.issubset(contribution_ids)

    assert risk["decision"] in {
        "ready_with_conservative_level3_positioning",
        "ready_but_level3_claim_should_be_softened",
        "not_publication_safe_yet",
    }


def test_required_risks_and_honest_severity_present():
    risk = load_json(RISK_PATH)
    risk_ids = {item["risk_id"] for item in risk["risks"]}
    required = {
        "audited_shell_scope_only",
        "no_broader_class_theorem",
        "no_external_non_sft_breadth",
        "canonical_object_complexity",
        "continuous_kernel_reset_dependence",
        "pica_novelty_overlap",
        "strict_extension_shell_specificity",
        "thermodynamic_consequence_proxy_reading",
    }
    assert required.issubset(risk_ids)

    severities = {item["severity"] for item in risk["risks"]}
    assert "high" in severities or "medium" in severities
