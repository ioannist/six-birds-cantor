#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


SUPPORTED_HASH_METHOD = "sha256-json-canonical-v1"
REDUCED_CELL_PAIRS = {
    ("P2<-P4", "A10"),
    ("P4<-P4", "A15"),
    ("P4<-P3", "A14"),
    ("P3<-P4", "A19"),
    ("P2<-P6", "A12"),
    ("P5<-P4", "A22"),
    ("P5<-P6", "A23"),
    ("P6<-P6", "A25"),
}


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ValueError(f"missing file: {path}") from None
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path}: {exc}") from None


def canonical_json_sha256(data: Any) -> str:
    if not isinstance(data, dict):
        raise ValueError("config hash policy requires top-level JSON object")
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _expect_type(errors: list[str], obj: dict[str, Any], field: str, expected: type | tuple[type, ...]) -> None:
    value = obj.get(field)
    if not isinstance(value, expected):
        errors.append(f"field '{field}' must be {expected}, got {type(value)}")


def _validate_experiment_config_builtin(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["experiment config must be a JSON object"]

    required = [
        "schema_version",
        "experiment_id",
        "family_id",
        "engine",
        "parameters",
        "run_controls",
        "output_root",
    ]
    for key in required:
        if key not in data:
            errors.append(f"missing required field '{key}'")

    if errors:
        return errors

    _expect_type(errors, data, "schema_version", str)
    _expect_type(errors, data, "experiment_id", str)
    _expect_type(errors, data, "family_id", str)
    _expect_type(errors, data, "engine", str)
    _expect_type(errors, data, "parameters", dict)
    _expect_type(errors, data, "run_controls", dict)
    _expect_type(errors, data, "output_root", str)

    if "description" in data and not isinstance(data["description"], str):
        errors.append("field 'description' must be string when provided")
    if "tags" in data:
        tags = data["tags"]
        if not isinstance(tags, list) or any(not isinstance(x, str) for x in tags):
            errors.append("field 'tags' must be an array of strings when provided")
    if "notes" in data and data["notes"] is not None and not isinstance(data["notes"], str):
        errors.append("field 'notes' must be string or null when provided")
    if "provenance" in data and not isinstance(data["provenance"], dict):
        errors.append("field 'provenance' must be object when provided")
    return errors


def _validate_result_manifest_builtin(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["result manifest must be a JSON object"]

    required = [
        "schema_version",
        "run_id",
        "timestamp_utc",
        "status",
        "code_version",
        "config_path",
        "config_hash_method",
        "config_hash_sha256",
        "family_id",
        "engine",
        "parameters",
        "artifacts",
        "summary_metrics",
    ]
    for key in required:
        if key not in data:
            errors.append(f"missing required field '{key}'")
    if errors:
        return errors

    _expect_type(errors, data, "schema_version", str)
    _expect_type(errors, data, "run_id", str)
    _expect_type(errors, data, "timestamp_utc", str)
    _expect_type(errors, data, "status", str)
    _expect_type(errors, data, "code_version", str)
    _expect_type(errors, data, "config_path", str)
    _expect_type(errors, data, "config_hash_method", str)
    _expect_type(errors, data, "config_hash_sha256", str)
    _expect_type(errors, data, "family_id", str)
    _expect_type(errors, data, "engine", str)
    _expect_type(errors, data, "parameters", dict)
    _expect_type(errors, data, "artifacts", list)
    _expect_type(errors, data, "summary_metrics", dict)

    if isinstance(data.get("timestamp_utc"), str):
        if not re.match(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[^\s]+$", data["timestamp_utc"]):
            errors.append("field 'timestamp_utc' must look like an ISO datetime string")
    if isinstance(data.get("config_hash_sha256"), str):
        if not re.match(r"^[0-9a-f]{64}$", data["config_hash_sha256"]):
            errors.append("field 'config_hash_sha256' must be a 64-char lowercase hex SHA256")

    artifacts = data.get("artifacts")
    if isinstance(artifacts, list):
        for i, entry in enumerate(artifacts):
            if not isinstance(entry, dict):
                errors.append(f"artifacts[{i}] must be an object")
                continue
            if "path" not in entry or not isinstance(entry.get("path"), str):
                errors.append(f"artifacts[{i}].path must be a string")
            if "kind" not in entry or not isinstance(entry.get("kind"), str):
                errors.append(f"artifacts[{i}].kind must be a string")

    if "command" in data and not isinstance(data["command"], str):
        errors.append("field 'command' must be string when provided")
    if "exit_status" in data and not isinstance(data["exit_status"], int):
        errors.append("field 'exit_status' must be integer when provided")
    if "warnings" in data:
        warnings = data["warnings"]
        if not isinstance(warnings, list) or any(not isinstance(x, str) for x in warnings):
            errors.append("field 'warnings' must be an array of strings when provided")
    if "notes" in data and data["notes"] is not None and not isinstance(data["notes"], str):
        errors.append("field 'notes' must be string or null when provided")
    if "environment" in data and not isinstance(data["environment"], dict):
        errors.append("field 'environment' must be object when provided")
    return errors


def _validate_family_registry_builtin(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["family registry must be a JSON object"]

    required = ["schema_version", "registry_id", "tiers"]
    for key in required:
        if key not in data:
            errors.append(f"missing required field '{key}'")
    if errors:
        return errors

    _expect_type(errors, data, "schema_version", str)
    _expect_type(errors, data, "registry_id", str)
    _expect_type(errors, data, "tiers", dict)
    tiers = data.get("tiers")
    if not isinstance(tiers, dict):
        return errors

    expected_tiers = {"classical", "finite_state", "contextual_local"}
    actual_tiers = set(tiers.keys())
    if actual_tiers != expected_tiers:
        errors.append(
            f"'tiers' must contain exactly {sorted(expected_tiers)}, got {sorted(actual_tiers)}"
        )
        return errors

    allowed_engines = {
        "classical_similarity",
        "finite_state_symbolic",
        "graph_directed_similarity",
        "nonautonomous_symbolic",
        "local_ifs",
    }
    required_family_fields = {
        "family_id",
        "label",
        "parameter_list",
        "engine",
        "known_exact_quantities",
        "notes",
    }

    for tier_name, families in tiers.items():
        if not isinstance(families, list):
            errors.append(f"tiers.{tier_name} must be an array")
            continue
        for i, entry in enumerate(families):
            if not isinstance(entry, dict):
                errors.append(f"tiers.{tier_name}[{i}] must be an object")
                continue
            missing = required_family_fields - set(entry.keys())
            if missing:
                errors.append(f"tiers.{tier_name}[{i}] missing fields: {sorted(missing)}")
                continue
            if not isinstance(entry.get("family_id"), str):
                errors.append(f"tiers.{tier_name}[{i}].family_id must be a string")
            if not isinstance(entry.get("label"), str):
                errors.append(f"tiers.{tier_name}[{i}].label must be a string")
            param_list = entry.get("parameter_list")
            if not isinstance(param_list, list) or any(not isinstance(x, str) for x in param_list):
                errors.append(f"tiers.{tier_name}[{i}].parameter_list must be an array of strings")
            engine = entry.get("engine")
            if not isinstance(engine, str) or engine not in allowed_engines:
                errors.append(f"tiers.{tier_name}[{i}].engine must be one of {sorted(allowed_engines)}")
            keq = entry.get("known_exact_quantities")
            if keq is not None and not isinstance(keq, dict):
                errors.append(f"tiers.{tier_name}[{i}].known_exact_quantities must be object or null")
            if not isinstance(entry.get("notes"), str):
                errors.append(f"tiers.{tier_name}[{i}].notes must be a string")
    return errors


def _validate_pica_alignment_builtin(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["pica alignment must be a JSON object"]

    required = [
        "schema_version",
        "alignment_id",
        "project_scope",
        "p1_policy",
        "primitive_semantics",
        "reduced_cell_set",
        "family_alignment",
    ]
    for key in required:
        if key not in data:
            errors.append(f"missing required field '{key}'")
    if errors:
        return errors

    _expect_type(errors, data, "schema_version", str)
    _expect_type(errors, data, "alignment_id", str)
    _expect_type(errors, data, "project_scope", str)
    _expect_type(errors, data, "p1_policy", str)
    _expect_type(errors, data, "primitive_semantics", dict)
    _expect_type(errors, data, "reduced_cell_set", list)
    _expect_type(errors, data, "family_alignment", list)

    semantics = data.get("primitive_semantics")
    if isinstance(semantics, dict):
        for p in ["P1", "P2", "P3", "P4", "P5", "P6"]:
            if p not in semantics or not isinstance(semantics[p], str):
                errors.append(f"primitive_semantics.{p} must be present and string")

    reduced = data.get("reduced_cell_set")
    if isinstance(reduced, list):
        for i, entry in enumerate(reduced):
            if not isinstance(entry, dict):
                errors.append(f"reduced_cell_set[{i}] must be object")
                continue
            for f in ["cell", "code", "status", "notes"]:
                if f not in entry:
                    errors.append(f"reduced_cell_set[{i}] missing field '{f}'")
            if "status" in entry and entry["status"] not in {"current", "planned", "not_in_scope"}:
                errors.append(f"reduced_cell_set[{i}].status invalid")

    fam = data.get("family_alignment")
    if isinstance(fam, list):
        required_family_fields = [
            "family_id",
            "role",
            "pica_status",
            "primitive_tags",
            "active_cells_current",
            "active_cells_target",
            "lens_modes_current",
            "lens_modes_target",
            "packaging_modes_current",
            "packaging_modes_target",
            "notes",
        ]
        for i, entry in enumerate(fam):
            if not isinstance(entry, dict):
                errors.append(f"family_alignment[{i}] must be object")
                continue
            for f in required_family_fields:
                if f not in entry:
                    errors.append(f"family_alignment[{i}] missing field '{f}'")
            if "role" in entry and entry["role"] not in {"baseline", "control", "probe", "toy"}:
                errors.append(f"family_alignment[{i}].role invalid")
            if "pica_status" in entry and entry["pica_status"] not in {"representative", "partial", "control_only"}:
                errors.append(f"family_alignment[{i}].pica_status invalid")
    return errors


def _validate_pica_alignment_semantics(data: dict[str, Any], repo_root: Path) -> list[str]:
    errors: list[str] = []
    reduced = data.get("reduced_cell_set", [])
    reduced_pairs = set()
    for entry in reduced:
        if isinstance(entry, dict):
            reduced_pairs.add((str(entry.get("cell")), str(entry.get("code"))))
    if reduced_pairs != REDUCED_CELL_PAIRS:
        errors.append("reduced_cell_set must match the agreed 8 (cell, code) pairs exactly")

    expected_family_ids: set[str] = set()
    for config_path in (repo_root / "configs" / "experiments").rglob("*.json"):
        try:
            cfg = load_json(config_path)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        if isinstance(cfg, dict) and isinstance(cfg.get("family_id"), str):
            expected_family_ids.add(cfg["family_id"])

    aligned_ids: set[str] = set()
    for entry in data.get("family_alignment", []):
        if isinstance(entry, dict) and isinstance(entry.get("family_id"), str):
            aligned_ids.add(entry["family_id"])

    missing = sorted(expected_family_ids - aligned_ids)
    if missing:
        errors.append(f"missing family_alignment entries for: {missing}")

    justification_keywords = [
        "internal feedback",
        "protocol adaptation",
        "timescale adaptation",
        "closed-loop",
    ]
    for entry in data.get("family_alignment", []):
        if not isinstance(entry, dict):
            continue
        tags = entry.get("primitive_tags", [])
        active = entry.get("active_cells_current", [])
        notes = str(entry.get("notes", "")).lower()
        claims_p3 = False
        if isinstance(tags, list) and any(str(t) == "P3" for t in tags):
            claims_p3 = True
        if isinstance(active, list) and any("P3" in str(c) for c in active):
            claims_p3 = True
        if claims_p3 and not any(k in notes for k in justification_keywords):
            errors.append(
                f"family '{entry.get('family_id')}' claims current P3 without explicit internal-feedback justification"
            )
    return errors


def validate_with_optional_jsonschema(instance: Any, schema: dict[str, Any], fallback: str) -> list[str]:
    try:
        import jsonschema  # type: ignore
    except Exception:
        if fallback == "config":
            return _validate_experiment_config_builtin(instance)
        if fallback == "manifest":
            return _validate_result_manifest_builtin(instance)
        if fallback == "registry":
            return _validate_family_registry_builtin(instance)
        return _validate_pica_alignment_builtin(instance)

    try:
        jsonschema.validate(instance=instance, schema=schema)
        return []
    except jsonschema.ValidationError as exc:  # type: ignore[attr-defined]
        path = ".".join(str(p) for p in exc.path) or "<root>"
        return [f"{path}: {exc.message}"]


def normalize_repo_relative(path_value: str, repo_root: Path, cwd: Path) -> str:
    path = Path(path_value)
    resolved = path.resolve() if path.is_absolute() else (cwd / path).resolve()
    try:
        return resolved.relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


def run(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate experiment config and result manifest metadata.")
    parser.add_argument("--config", type=Path, help="Path to experiment config JSON.")
    parser.add_argument("--manifest", type=Path, help="Path to result manifest JSON.")
    parser.add_argument("--registry", type=Path, help="Path to benchmark family registry JSON.")
    parser.add_argument("--pica-alignment", type=Path, help="Path to Cantor PICA alignment JSON.")
    parser.add_argument(
        "--check-config-hash",
        action="store_true",
        help="Cross-check manifest config hash against the provided config.",
    )
    args = parser.parse_args(argv)

    if not args.config and not args.manifest and not args.registry and not args.pica_alignment:
        print("error: provide --config and/or --manifest and/or --registry and/or --pica-alignment", file=sys.stderr)
        return 2
    if args.check_config_hash and (not args.config or not args.manifest):
        print("error: --check-config-hash requires both --config and --manifest", file=sys.stderr)
        return 2

    script_path = Path(__file__).resolve()
    repo_root = script_path.parent.parent
    cwd = Path.cwd()

    config_schema = load_json(repo_root / "configs" / "schema" / "experiment-config.schema.json")
    manifest_schema = load_json(repo_root / "configs" / "schema" / "result-manifest.schema.json")
    registry_schema = load_json(repo_root / "configs" / "schema" / "benchmark-family-registry.schema.json")
    pica_schema = load_json(repo_root / "configs" / "schema" / "cantor-pica-alignment.schema.json")

    any_error = False
    config_data: dict[str, Any] | None = None
    manifest_data: dict[str, Any] | None = None

    if args.config:
        config_data_raw = load_json(args.config)
        config_errors = validate_with_optional_jsonschema(config_data_raw, config_schema, "config")
        if config_errors:
            any_error = True
            print("config validation: FAIL", file=sys.stderr)
            for err in config_errors:
                print(f"  - {err}", file=sys.stderr)
        else:
            print("config validation: PASS")
        if isinstance(config_data_raw, dict):
            config_data = config_data_raw

    if args.manifest:
        manifest_data_raw = load_json(args.manifest)
        manifest_errors = validate_with_optional_jsonschema(manifest_data_raw, manifest_schema, "manifest")
        if manifest_errors:
            any_error = True
            print("manifest validation: FAIL", file=sys.stderr)
            for err in manifest_errors:
                print(f"  - {err}", file=sys.stderr)
        else:
            print("manifest validation: PASS")
        if isinstance(manifest_data_raw, dict):
            manifest_data = manifest_data_raw

    if args.registry:
        registry_data_raw = load_json(args.registry)
        registry_errors = validate_with_optional_jsonschema(registry_data_raw, registry_schema, "registry")
        if registry_errors:
            any_error = True
            print("registry validation: FAIL", file=sys.stderr)
            for err in registry_errors:
                print(f"  - {err}", file=sys.stderr)
        else:
            print("registry validation: PASS")

    if args.pica_alignment:
        pica_data_raw = load_json(args.pica_alignment)
        pica_errors = validate_with_optional_jsonschema(pica_data_raw, pica_schema, "pica_alignment")
        if not pica_errors and isinstance(pica_data_raw, dict):
            pica_errors = _validate_pica_alignment_semantics(pica_data_raw, repo_root)
        if pica_errors:
            any_error = True
            print("pica alignment validation: FAIL", file=sys.stderr)
            for err in pica_errors:
                print(f"  - {err}", file=sys.stderr)
        else:
            print("pica alignment validation: PASS")

    if args.check_config_hash and config_data is not None and manifest_data is not None:
        check_errors: list[str] = []

        method = manifest_data.get("config_hash_method")
        if method != SUPPORTED_HASH_METHOD:
            check_errors.append(
                f"unsupported config_hash_method '{method}', expected '{SUPPORTED_HASH_METHOD}'"
            )

        expected_hash = canonical_json_sha256(config_data)
        actual_hash = manifest_data.get("config_hash_sha256")
        if actual_hash != expected_hash:
            check_errors.append("config_hash_sha256 mismatch")

        provided_cfg_rel = normalize_repo_relative(str(args.config), repo_root, cwd)
        manifest_cfg_rel = normalize_repo_relative(str(manifest_data.get("config_path", "")), repo_root, cwd)
        if provided_cfg_rel != manifest_cfg_rel:
            check_errors.append(
                f"config_path mismatch: manifest='{manifest_cfg_rel}' provided='{provided_cfg_rel}'"
            )

        if check_errors:
            any_error = True
            print("config hash cross-check: FAIL", file=sys.stderr)
            for err in check_errors:
                print(f"  - {err}", file=sys.stderr)
        else:
            print("config hash cross-check: PASS")

    return 1 if any_error else 0


if __name__ == "__main__":
    raise SystemExit(run())
