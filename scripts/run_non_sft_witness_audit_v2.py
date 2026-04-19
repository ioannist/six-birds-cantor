#!/usr/bin/env python3
from __future__ import annotations

import csv
import datetime as dt
import json
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def main() -> int:
    repo_root = _repo_root()
    package_path = repo_root / "docs" / "internal" / "delayed_return_theorem_package_v1.json"
    package = json.loads(package_path.read_text(encoding="utf-8"))

    candidate_families = [
        "frontier.fw_delayed_return_gate_a3",
        "frontier.fw_delayed_return_gate_a1",
        "frontier.fw_delayed_return_gate_a2",
        "contextual_local.prefix_memory_last_digit_rule",
        "contextual_local.prefix_memory_no_22_base3",
        "contextual_local.domain_gated_two_map_local_ifs",
    ]

    report_rows = []
    selected_family = "frontier.fw_delayed_return_gate_a3"
    for family_id in candidate_families:
        if family_id.startswith("frontier.fw_delayed_return_gate_"):
            in_class = "yes"
            finite_state = "yes"
            non_sft = "no"
            status = "finite_state_renewal_like_only"
            note = "Frozen delayed-return witness remains a controlled finite-return / renewal-like system on the closed class."
        elif family_id == "contextual_local.prefix_memory_no_22_base3":
            in_class = "no"
            finite_state = "yes"
            non_sft = "no"
            status = "finite_state_renewal_like_only"
            note = "Comparison family is finite-state-like and not part of the closed theorem class."
        elif family_id == "contextual_local.prefix_memory_last_digit_rule":
            in_class = "no"
            finite_state = "unknown"
            non_sft = "unknown"
            status = "finite_state_renewal_like_only"
            note = "Comparison family is outside the closed theorem class and does not force a non-SFT conclusion."
        else:
            in_class = "no"
            finite_state = "yes"
            non_sft = "no"
            status = "finite_state_renewal_like_only"
            note = "Old domain-gated family still collapses to finite-state renewal-like control."

        report_rows.append(
            {
                "family_id": family_id,
                "in_class_status": in_class,
                "finite_state_renewal_like_status": finite_state,
                "non_sft_status": non_sft,
                "status": status,
                "note": note,
                "artifact_paths": [str(package_path)],
            }
        )

    payload = {
        "schema_version": "1.0",
        "audit_id": "non-sft-audit-v2",
        "target_class_id": package["closed_class_id"],
        "decision": "finite_state_renewal_like_only",
        "candidate_families": candidate_families,
        "selected_family": selected_family,
        "in_class_status": "yes",
        "non_sft_status": "no",
        "finite_state_renewal_like_status": "yes",
        "evidence_items": report_rows,
        "notes": [
            "Audit is against the frozen closed delayed-return package, not the older Bowen classes.",
            "The selected witness is in-class but remains finite-state renewal-like on the evidence currently available in the repo."
        ],
    }

    out_dir = repo_root / "results" / "non_sft_witness_v2"
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / "report.json"
    report_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    csv_path = out_dir / "report.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "family_id",
                "in_class_status",
                "finite_state_renewal_like_status",
                "non_sft_status",
                "status",
                "note",
                "artifact_paths",
            ],
        )
        writer.writeheader()
        writer.writerows(
            {
                **row,
                "artifact_paths": ";".join(row.get("artifact_paths", [])),
            }
            for row in report_rows
        )

    note_path = repo_root / "docs" / "internal" / "non_sft_witness_v2.md"
    note_path.write_text(
        "# Non-SFT Witness Audit v2\n\n"
        "## Question being tested\n"
        "Does the closed delayed-return theorem branch yield a genuinely frontier local-domain witness, or is it still only a stronger finite-state renewal-like result?\n\n"
        "## Closed theorem class\n"
        f"- `{package['closed_class_id']}`\n\n"
        "## Control setup being ruled out\n"
        "For this audit, the excluded control setup is a stationary finite-state symbolic or finite-state renewal-like control model with finitely many continuation/return types sufficient to generate the induced cylinders and geometry relevant to the closed theorem.\n\n"
        "The question is not only whether the class is non-SFT in the narrow symbolic sense. It is also whether it escapes finite-state renewal-like control in the theorem-relevant sense.\n\n"
        "## Candidate families\n"
        + "\n".join(f"- `{fid}`" for fid in candidate_families)
        + "\n\n## Selected witness or blocker\n"
        "- Selected family: `frontier.fw_delayed_return_gate_a3`\n"
        "- Decision: `finite_state_renewal_like_only`\n\n"
        "## Reason the selected family is in-class\n"
        "- It is one of the frozen witnesses for the closed theorem package.\n"
        "- It satisfies the delayed-return assumptions and remains inside the closed full-core delayed-gate subclass.\n\n"
        "## Reason it is or is not beyond finite-state renewal-like control\n"
        "- It is not beyond finite-state renewal-like control on the evidence currently in the repo.\n"
        "- The closed class is built from bounded return, a finite induced return alphabet on the supported witnesses, and a return-premeasure transfer that closes after narrowing to full-core control.\n"
        "- That is enough for a theorem, but not enough to certify a genuinely new non-SFT local-domain phenomenon.\n\n"
        "## Impact consequence\n"
        "- The delayed-return branch is mathematically real and closed, but the current audit does not justify a non-SFT claim.\n"
        "- The result is a stronger finite-state renewal-like theorem package, not yet the frontier witness the project ultimately wants.\n",
        encoding="utf-8",
    )

    evidence_path = repo_root / "docs" / "internal" / "non_sft_witness_evidence_v2.json"
    evidence_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"wrote {report_path}")
    print("decision=finite_state_renewal_like_only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
