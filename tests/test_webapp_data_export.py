"""Tests for the webapp data export pipeline."""

import json
import subprocess
import sys
import tempfile
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EXPORT_SCRIPT = REPO_ROOT / "scripts" / "export_webapp_data.py"
OUTPUT_DIR = REPO_ROOT / "apps" / "cantor-web" / "public" / "data" / "v1"

REQUIRED_FILES = [
    "index.json",
    "theorem-package.json",
    "claim-ledger.json",
    "traceability.json",
    "figure-manifest.json",
    "witnesses.json",
    "continuous/continuous_full_loop_kernel.json",
    "continuous/continuous_full_loop_kernel_shell.json",
    "t0/continuous_full_loop_kernel_t0.json",
    "t0/continuous_full_loop_kernel_shell_t0.json",
    "t1/continuous_full_loop_kernel_t1.json",
    "t1/continuous_full_loop_kernel_shell_t1.json",
    "extension/continuous_full_loop_kernel_extension.json",
    "extension/continuous_full_loop_kernel_shell_extension.json",
    "disintegration/continuous_full_loop_kernel_disintegration.json",
    "disintegration/continuous_full_loop_kernel_shell_disintegration.json",
    "knockouts/continuous_full_loop_kernel_knockouts.json",
    "knockouts/continuous_full_loop_kernel_shell_knockouts.json",
    "policy/annotation_policy.json",
]


def _run_export():
    """Run the export script and return the process result."""
    result = subprocess.run(
        [sys.executable, str(EXPORT_SCRIPT)],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    return result


def _load(name: str) -> dict:
    with open(OUTPUT_DIR / name) as f:
        return json.load(f)


class TestExportScriptRuns:
    def test_export_exits_zero(self):
        result = _run_export()
        assert result.returncode == 0, f"Export failed:\n{result.stderr}"

    def test_all_required_files_produced(self):
        _run_export()
        for fname in REQUIRED_FILES:
            path = OUTPUT_DIR / fname
            assert path.exists(), f"Missing exported file: {fname}"
            assert path.stat().st_size > 0, f"Empty exported file: {fname}"

    def test_placeholder_removed(self):
        _run_export()
        assert not (OUTPUT_DIR / "placeholder.json").exists()


class TestIndexJson:
    def test_schema_version(self):
        _run_export()
        data = _load("index.json")
        assert data["schema_version"] == "v1"

    def test_datasets_listed(self):
        _run_export()
        data = _load("index.json")
        names = {d["name"] for d in data["datasets"]}
        expected = {
            "theorem-package", "claim-ledger", "traceability", "figure-manifest", "witnesses",
            "continuous/continuous_full_loop_kernel", "continuous/continuous_full_loop_kernel_shell",
            "t0/continuous_full_loop_kernel_t0", "t0/continuous_full_loop_kernel_shell_t0",
            "t1/continuous_full_loop_kernel_t1", "t1/continuous_full_loop_kernel_shell_t1",
            "extension/continuous_full_loop_kernel_extension", "extension/continuous_full_loop_kernel_shell_extension",
            "disintegration/continuous_full_loop_kernel_disintegration", "disintegration/continuous_full_loop_kernel_shell_disintegration",
            "knockouts/continuous_full_loop_kernel_knockouts", "knockouts/continuous_full_loop_kernel_shell_knockouts",
            "policy/annotation_policy",
        }
        assert names == expected

    def test_generated_timestamp_present(self):
        _run_export()
        data = _load("index.json")
        assert "generated_at_utc" in data


class TestTheoremPackageJson:
    def test_top_level_keys(self):
        _run_export()
        data = _load("theorem-package.json")
        for key in ["package_id", "paper_core_positioning", "canonical_object_id",
                     "core_class_id", "included_theoremlets", "nonclaims",
                     "reserve_routes", "canonical_hybrid_object", "claim_posture"]:
            assert key in data, f"Missing key: {key}"

    def test_theoremlets_have_ids(self):
        _run_export()
        data = _load("theorem-package.json")
        for t in data["included_theoremlets"]:
            assert "theoremlet_id" in t
            assert "status" in t


class TestClaimLedgerJson:
    def test_top_level_keys(self):
        _run_export()
        data = _load("claim-ledger.json")
        assert "claims" in data
        assert "claim_counts" in data

    def test_claims_have_required_fields(self):
        _run_export()
        data = _load("claim-ledger.json")
        for c in data["claims"]:
            for key in ["claim_id", "claim_status", "allowed_final_paper_use",
                        "object_scope", "class_scope"]:
                assert key in c, f"Claim missing key: {key}"


class TestTraceabilityJson:
    def test_theoremlets_present(self):
        _run_export()
        data = _load("traceability.json")
        assert len(data["theoremlets"]) > 0

    def test_theoremlet_fields(self):
        _run_export()
        data = _load("traceability.json")
        for t in data["theoremlets"]:
            for key in ["theoremlet_id", "assumptions_used", "dependency_paths",
                        "evidence_paths", "allowed_claim_ids"]:
                assert key in t, f"Theoremlet missing key: {key}"

    def test_scope_firewall_present(self):
        _run_export()
        data = _load("traceability.json")
        assert "scope_firewall" in data


class TestFigureManifestJson:
    def test_figures_present(self):
        _run_export()
        data = _load("figure-manifest.json")
        assert len(data["figures"]) > 0

    def test_figure_fields(self):
        _run_export()
        data = _load("figure-manifest.json")
        for fig in data["figures"]:
            for key in ["figure_id", "title_short", "role", "supports_theoremlets",
                        "allowed_claim_ids", "source_artifacts"]:
                assert key in fig, f"Figure missing key: {key}"


class TestWitnessesJson:
    def test_witnesses_present(self):
        _run_export()
        data = _load("witnesses.json")
        assert len(data["witnesses"]) > 0

    def test_witness_fields(self):
        _run_export()
        data = _load("witnesses.json")
        for w in data["witnesses"]:
            assert "theoremlet_id" in w
            assert "witness_families" in w


class TestIdConsistency:
    """Cross-file ID consistency checks."""

    def test_theoremlet_ids_match_across_files(self):
        _run_export()
        pkg = _load("theorem-package.json")
        ledger = _load("claim-ledger.json")
        trace = _load("traceability.json")

        pkg_ids = {t["theoremlet_id"] for t in pkg["included_theoremlets"]}
        trace_ids = {t["theoremlet_id"] for t in trace["theoremlets"]}
        # All package theoremlet IDs should appear in traceability
        assert pkg_ids <= trace_ids

        # All closed theoremlet claim IDs should appear in the ledger
        ledger_ids = {c["claim_id"] for c in ledger["claims"]}
        for tid in pkg_ids:
            assert tid in ledger_ids, f"Theoremlet {tid} not in claim ledger"

    def test_figure_ids_match(self):
        _run_export()
        manifest = _load("figure-manifest.json")
        trace = _load("traceability.json")

        manifest_ids = {f["figure_id"] for f in manifest["figures"]}
        # All figure IDs referenced in traceability claim_bindings should exist in manifest
        for binding in trace["claim_bindings"]:
            for fid in binding["figure_ids"]:
                assert fid in manifest_ids, f"Figure {fid} in traceability but not in manifest"


class TestContinuousTrajectory:
    """Tests for continuous substrate trajectory exports."""

    def test_both_witnesses_exported(self):
        _run_export()
        for name in ["continuous_full_loop_kernel", "continuous_full_loop_kernel_shell"]:
            path = OUTPUT_DIR / "continuous" / f"{name}.json"
            assert path.exists(), f"Missing continuous export: {name}"

    def test_top_level_keys(self):
        _run_export()
        data = _load("continuous/continuous_full_loop_kernel.json")
        for key in ["schema_version", "witness_id", "config", "total_steps",
                     "kernel_snapshot_interval", "kernel_snapshots", "timeline"]:
            assert key in data, f"Missing key: {key}"

    def test_timeline_has_steps(self):
        _run_export()
        data = _load("continuous/continuous_full_loop_kernel.json")
        assert len(data["timeline"]) == data["total_steps"]

    def test_timeline_step_fields(self):
        _run_export()
        data = _load("continuous/continuous_full_loop_kernel.json")
        step = data["timeline"][0]
        for key in ["step", "variation", "tau", "budget", "lens", "packaging",
                     "action_weights", "primitive_activity"]:
            assert key in step, f"Timeline step missing key: {key}"

    def test_kernel_snapshots_present(self):
        _run_export()
        data = _load("continuous/continuous_full_loop_kernel.json")
        assert len(data["kernel_snapshots"]) > 0

    def test_kernel_snapshot_dimensions(self):
        _run_export()
        data = _load("continuous/continuous_full_loop_kernel.json")
        dim = data["config"]["kernel_dim"]
        snap = data["kernel_snapshots"][0]
        assert len(snap["kernel"]) == dim
        assert len(snap["kernel"][0]) == dim

    def test_index_lists_continuous_datasets(self):
        _run_export()
        index = _load("index.json")
        names = {d["name"] for d in index["datasets"]}
        assert "continuous/continuous_full_loop_kernel" in names
        assert "continuous/continuous_full_loop_kernel_shell" in names

    def test_shell_witness_has_different_config(self):
        _run_export()
        base = _load("continuous/continuous_full_loop_kernel.json")
        shell = _load("continuous/continuous_full_loop_kernel_shell.json")
        assert base["config"]["seed"] != shell["config"]["seed"]
        assert base["config"]["kernel_dim"] != shell["config"]["kernel_dim"]


class TestT0View:
    """Tests for T0 cocycle object view exports."""

    def test_both_witnesses_exported(self):
        _run_export()
        for name in ["continuous_full_loop_kernel_t0", "continuous_full_loop_kernel_shell_t0"]:
            path = OUTPUT_DIR / "t0" / f"{name}.json"
            assert path.exists(), f"Missing T0 export: {name}"

    def test_top_level_keys(self):
        _run_export()
        data = _load("t0/continuous_full_loop_kernel_t0.json")
        for key in ["schema_version", "witness_id", "theory_id", "core_class_id",
                     "shell_stable", "t0_object_map", "theoremlets", "claim_bindings",
                     "pressure_object", "t1_comparison"]:
            assert key in data, f"Missing key: {key}"

    def test_theory_id_is_t0(self):
        _run_export()
        data = _load("t0/continuous_full_loop_kernel_t0.json")
        assert data["theory_id"] == "T0_cocycle_pressure_theory"

    def test_shell_stable_flag(self):
        _run_export()
        data = _load("t0/continuous_full_loop_kernel_t0.json")
        assert data["shell_stable"] is True

    def test_only_t0_theoremlets(self):
        _run_export()
        data = _load("t0/continuous_full_loop_kernel_t0.json")
        ids = {t["theoremlet_id"] for t in data["theoremlets"]}
        assert "continuous_full_loop_lawfulness_theoremlet" in ids
        assert "cocycle_pressure_closure_theoremlet" in ids
        # T1-specific theoremlets must not appear
        assert "strict_theory_extension_theoremlet" not in ids
        assert "conditional_pressure_disintegration_theoremlet" not in ids

    def test_pressure_object_present(self):
        _run_export()
        data = _load("t0/continuous_full_loop_kernel_t0.json")
        assert data["pressure_object"] is not None
        assert "fekete_gap_proxy" in data["pressure_object"]

    def test_t1_comparison_scoped(self):
        _run_export()
        data = _load("t0/continuous_full_loop_kernel_t0.json")
        assert data["t1_comparison"]["_scope"] == "comparison_only"

    def test_index_lists_t0_datasets(self):
        _run_export()
        index = _load("index.json")
        names = {d["name"] for d in index["datasets"]}
        assert "t0/continuous_full_loop_kernel_t0" in names
        assert "t0/continuous_full_loop_kernel_shell_t0" in names


class TestT1View:
    """Tests for T1 completion/fixed-point view exports."""

    def test_both_witnesses_exported(self):
        _run_export()
        for name in ["continuous_full_loop_kernel_t1", "continuous_full_loop_kernel_shell_t1"]:
            path = OUTPUT_DIR / "t1" / f"{name}.json"
            assert path.exists(), f"Missing T1 export: {name}"

    def test_top_level_keys(self):
        _run_export()
        data = _load("t1/continuous_full_loop_kernel_t1.json")
        for key in ["schema_version", "witness_id", "theory_id", "extended_object_map",
                     "completion_config", "fixed_point_strata", "saturation",
                     "run_summaries", "p4_from_p5_events", "packaging_identity_changes",
                     "t0_comparison"]:
            assert key in data, f"Missing key: {key}"

    def test_theory_id_is_t1(self):
        _run_export()
        data = _load("t1/continuous_full_loop_kernel_t1.json")
        assert data["theory_id"] == "T1_hybrid_cocycle_plus_completion_theory"

    def test_fixed_point_strata_present(self):
        _run_export()
        data = _load("t1/continuous_full_loop_kernel_t1.json")
        assert data["fixed_point_strata"]["distinct_count"] > 0

    def test_saturation_has_panels(self):
        _run_export()
        data = _load("t1/continuous_full_loop_kernel_t1.json")
        assert data["saturation"]["total_panels"] > 0

    def test_run_summaries_present(self):
        _run_export()
        data = _load("t1/continuous_full_loop_kernel_t1.json")
        assert len(data["run_summaries"]) > 0
        run = data["run_summaries"][0]
        for key in ["tau", "lens_state", "status", "iterations", "residual", "macro_admissible"]:
            assert key in run, f"Run summary missing key: {key}"

    def test_p4_from_p5_events_present(self):
        _run_export()
        data = _load("t1/continuous_full_loop_kernel_t1.json")
        assert len(data["p4_from_p5_events"]) > 0

    def test_packaging_identity_changes_present(self):
        _run_export()
        data = _load("t1/continuous_full_loop_kernel_t1.json")
        assert len(data["packaging_identity_changes"]) > 0

    def test_t0_comparison_scoped(self):
        _run_export()
        data = _load("t1/continuous_full_loop_kernel_t1.json")
        assert data["t0_comparison"]["_scope"] == "comparison_only"

    def test_index_lists_t1_datasets(self):
        _run_export()
        index = _load("index.json")
        names = {d["name"] for d in index["datasets"]}
        assert "t1/continuous_full_loop_kernel_t1" in names
        assert "t1/continuous_full_loop_kernel_shell_t1" in names


class TestExtensionView:
    """Tests for extension certificate exports."""

    def test_both_witnesses_exported(self):
        _run_export()
        for name in ["continuous_full_loop_kernel_extension", "continuous_full_loop_kernel_shell_extension"]:
            path = OUTPUT_DIR / "extension" / f"{name}.json"
            assert path.exists(), f"Missing extension export: {name}"

    def test_top_level_keys(self):
        _run_export()
        data = _load("extension/continuous_full_loop_kernel_extension.json")
        for key in ["schema_version", "witness_id", "base_theory_id", "extended_theory_id",
                     "factorization_test", "verdicts", "saturation_summary",
                     "forcing_summary", "macro_admissibility_summary", "scope", "theoremlet"]:
            assert key in data, f"Missing key: {key}"

    def test_scope_is_audited_shell(self):
        _run_export()
        data = _load("extension/continuous_full_loop_kernel_extension.json")
        assert data["scope"] == "audited_shell_only"

    def test_factorization_failed(self):
        _run_export()
        data = _load("extension/continuous_full_loop_kernel_extension.json")
        assert data["factorization_test"]["factor_through_T0"] is False
        assert data["factorization_test"]["non_factorization_rate"] > 0

    def test_verdicts_present(self):
        _run_export()
        data = _load("extension/continuous_full_loop_kernel_extension.json")
        for key in ["factorization", "object_identity", "saturation", "forcing", "macro_admissibility"]:
            assert key in data["verdicts"]

    def test_theoremlet_is_strict_extension(self):
        _run_export()
        data = _load("extension/continuous_full_loop_kernel_extension.json")
        assert data["theoremlet"]["theoremlet_id"] == "strict_theory_extension_theoremlet"

    def test_index_lists_extension_datasets(self):
        _run_export()
        index = _load("index.json")
        names = {d["name"] for d in index["datasets"]}
        assert "extension/continuous_full_loop_kernel_extension" in names
        assert "extension/continuous_full_loop_kernel_shell_extension" in names


class TestDisintegrationView:
    """Tests for conditional disintegration exports."""

    def test_both_witnesses_exported(self):
        _run_export()
        for name in ["continuous_full_loop_kernel_disintegration", "continuous_full_loop_kernel_shell_disintegration"]:
            path = OUTPUT_DIR / "disintegration" / f"{name}.json"
            assert path.exists(), f"Missing disintegration export: {name}"

    def test_top_level_keys(self):
        _run_export()
        data = _load("disintegration/continuous_full_loop_kernel_disintegration.json")
        for key in ["schema_version", "witness_id", "selected_consequence_object",
                     "decision", "scope", "t0_pressure", "descriptor_summaries",
                     "config_summary", "shell_stability", "rejected_routes", "theoremlet"]:
            assert key in data, f"Missing key: {key}"

    def test_scope_is_audited_shell(self):
        _run_export()
        data = _load("disintegration/continuous_full_loop_kernel_disintegration.json")
        assert data["scope"] == "audited_shell_only"

    def test_consequence_object(self):
        _run_export()
        data = _load("disintegration/continuous_full_loop_kernel_disintegration.json")
        assert data["selected_consequence_object"] == "weighted_package_conditioned_pressure_gap"

    def test_descriptors_present(self):
        _run_export()
        data = _load("disintegration/continuous_full_loop_kernel_disintegration.json")
        assert len(data["descriptor_summaries"]) > 0
        ds = data["descriptor_summaries"][0]
        assert "gap_bounded_away_from_zero" in ds
        assert "pressure_gap" in ds

    def test_rejected_routes_present(self):
        _run_export()
        data = _load("disintegration/continuous_full_loop_kernel_disintegration.json")
        assert data["rejected_routes"]["direct_stratumwise_separation"]["status"] == "rejected"
        assert data["rejected_routes"]["exact_kl_closure_deficit"]["status"] == "support_only"

    def test_theoremlet_is_disintegration(self):
        _run_export()
        data = _load("disintegration/continuous_full_loop_kernel_disintegration.json")
        assert data["theoremlet"]["theoremlet_id"] == "conditional_pressure_disintegration_theoremlet"

    def test_index_lists_disintegration_datasets(self):
        _run_export()
        index = _load("index.json")
        names = {d["name"] for d in index["datasets"]}
        assert "disintegration/continuous_full_loop_kernel_disintegration" in names
        assert "disintegration/continuous_full_loop_kernel_shell_disintegration" in names


class TestKnockoutsView:
    """Tests for primitive knockout exports."""

    def test_both_witnesses_exported(self):
        _run_export()
        for name in ["continuous_full_loop_kernel_knockouts", "continuous_full_loop_kernel_shell_knockouts"]:
            path = OUTPUT_DIR / "knockouts" / f"{name}.json"
            assert path.exists(), f"Missing knockout export: {name}"

    def test_top_level_keys(self):
        _run_export()
        data = _load("knockouts/continuous_full_loop_kernel_knockouts.json")
        for key in ["schema_version", "witness_id", "scope", "full_loop", "knockouts", "theoremlet"]:
            assert key in data, f"Missing key: {key}"

    def test_six_knockouts(self):
        _run_export()
        data = _load("knockouts/continuous_full_loop_kernel_knockouts.json")
        assert len(data["knockouts"]) == 6
        removed = {k["removed"] for k in data["knockouts"]}
        assert removed == {"P1", "P2", "P3", "P4", "P5", "P6"}

    def test_all_knockouts_show_degradation(self):
        _run_export()
        data = _load("knockouts/continuous_full_loop_kernel_knockouts.json")
        for ko in data["knockouts"]:
            assert ko["material_degradation"] is True

    def test_full_loop_has_metrics(self):
        _run_export()
        data = _load("knockouts/continuous_full_loop_kernel_knockouts.json")
        fl = data["full_loop"]
        for key in ["lens_switch_count", "packaging_switch_count", "tau_switch_count",
                     "budget_min", "budget_max"]:
            assert key in fl, f"Full loop missing key: {key}"

    def test_knockout_has_summary(self):
        _run_export()
        data = _load("knockouts/continuous_full_loop_kernel_knockouts.json")
        ko = data["knockouts"][0]
        assert "summary" in ko
        assert "material_reasons" in ko

    def test_p5_shows_budget_collapse(self):
        _run_export()
        data = _load("knockouts/continuous_full_loop_kernel_knockouts.json")
        p5 = next(k for k in data["knockouts"] if k["removed"] == "P5")
        assert p5["material_degradation"] is True
        assert any("budget" in r.lower() for r in p5["material_reasons"])

    def test_index_lists_knockout_datasets(self):
        _run_export()
        index = _load("index.json")
        names = {d["name"] for d in index["datasets"]}
        assert "knockouts/continuous_full_loop_kernel_knockouts" in names
        assert "knockouts/continuous_full_loop_kernel_shell_knockouts" in names


class TestAnnotationPolicy:
    """Tests for annotation policy export."""

    def test_policy_exported(self):
        _run_export()
        path = OUTPUT_DIR / "policy" / "annotation_policy.json"
        assert path.exists()

    def test_top_level_keys(self):
        _run_export()
        data = _load("policy/annotation_policy.json")
        for key in ["schema_version", "paper_core_positioning", "core_claim_ids",
                     "support_only_claim_ids", "reserve_claim_ids", "nonclaim_ids",
                     "scope_guards", "per_theoremlet_bindings", "claim_classifications"]:
            assert key in data, f"Missing key: {key}"

    def test_core_claims_present(self):
        _run_export()
        data = _load("policy/annotation_policy.json")
        assert len(data["core_claim_ids"]) == 4

    def test_nonclaims_present(self):
        _run_export()
        data = _load("policy/annotation_policy.json")
        assert len(data["nonclaim_ids"]) >= 5

    def test_scope_guards_present(self):
        _run_export()
        data = _load("policy/annotation_policy.json")
        assert len(data["scope_guards"]) > 0

    def test_per_theoremlet_bindings(self):
        _run_export()
        data = _load("policy/annotation_policy.json")
        assert len(data["per_theoremlet_bindings"]) > 0
        binding = data["per_theoremlet_bindings"][0]
        assert "theoremlet_id" in binding
        assert "allowed_claim_ids" in binding
        assert "forbidden_claim_ids" in binding
