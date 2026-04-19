#!/usr/bin/env python3
from __future__ import annotations

import csv
import datetime as dt
import json
from pathlib import Path
from typing import Any


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _candidate_config(
    family_id: str,
    source_id: str,
    source_title_short: str,
    paper_ref: str,
    theorem_route_fit: str,
    geometric_type: str,
    symbolic_type: str,
) -> dict[str, Any]:
    slug = family_id.replace(".", "-").replace("_", "-")
    return {
        "schema_version": "1.0",
        "experiment_id": slug,
        "family_id": family_id,
        "engine": "external_schematic",
        "source_id": source_id,
        "source_title_short": source_title_short,
        "paper_ref": paper_ref,
        "theorem_route_fit": theorem_route_fit,
        "description": f"Imported external witness skeleton from {source_title_short}.",
        "parameters": {
            "geometric_type": geometric_type,
            "symbolic_type": symbolic_type,
            "countable_alphabet": True,
            "import_status": "skeletal",
        },
        "run_controls": {"save_outputs": False, "seed": 0},
        "output_root": f"results/external_witness_import/{slug}",
    }


def _write_config(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    repo_root = _repo_root()
    external_dir = repo_root / "configs" / "experiments" / "external"
    external_dir.mkdir(parents=True, exist_ok=True)

    source_families = [
        {
            "source_id": "local_ifs_foundations",
            "source_type": "local_ifs_framework",
            "paper_title_short": "Foundations of local iterated function systems",
            "paper_ref": "arXiv:2601.07804",
            "why_considered": "Gives the repo-language bridge: local admissibility, extended shift, and examples not modeled by SFT.",
        },
        {
            "source_id": "countable_gdms_dimension_spectrum",
            "source_type": "countable_conformal_gdms",
            "paper_title_short": "The dimension spectrum of graph directed Markov systems",
            "paper_ref": "arXiv:1802.01125",
            "why_considered": "Countable-state GDMS with topological pressure estimates and explicit countable alphabet dynamics.",
        },
        {
            "source_id": "kuperberg_pseudomarkov_minimal_sets",
            "source_type": "graph_directed_pseudo_markov",
            "paper_title_short": "Hausdorff dimension of Kuperberg minimal sets",
            "paper_ref": "arXiv:1801.04034",
            "why_considered": "Pseudo-Markov system over a countable alphabet, a genuine step beyond finite-state renewal-like control.",
        },
        {
            "source_id": "countable_ifs_overlaps_complete_connections",
            "source_type": "countable_ifs_overlap",
            "paper_title_short": "Geometry of measures in random systems with complete connections",
            "paper_ref": "arXiv:2202.07335",
            "why_considered": "Countable conformal IFS with overlaps and exact dimensional stationary measures, useful as a geometric pressure target.",
        },
    ]

    candidate_families = [
        {
            "candidate_id": "external.local_ifs_non_sft_bridge",
            "source_id": "local_ifs_foundations",
            "geometric_type": "local_domain",
            "symbolic_type": "extended_shift_non_sft",
            "countable_state_relevance": "medium",
            "local_domain_relevance": "strong",
            "importability_to_repo": "high",
            "theorem_amenability": "medium",
            "finite_state_compressibility": "likely_no",
            "renewal_like_compressibility": "likely_no",
            "countable_state_signal": "medium",
            "local_domain_signal": "strong",
            "repo_import_difficulty": "low",
            "theorem_route_fit": "bounded_overlap",
            "frontier_status": "promising",
            "note": "Best bridge into the repo language: local admissibility and non-SFT examples already live in the source family.",
            "config": _candidate_config(
                "external.local_ifs_non_sft_bridge",
                "local_ifs_foundations",
                "Foundations of local iterated function systems",
                "arXiv:2601.07804",
                "bounded_overlap",
                "local_domain",
                "extended_shift_non_sft",
            ),
        },
        {
            "candidate_id": "external.countable_gdms_countable_alphabet",
            "source_id": "countable_gdms_dimension_spectrum",
            "geometric_type": "graph_directed_markov",
            "symbolic_type": "countable_markov_shift",
            "countable_state_relevance": "strong",
            "local_domain_relevance": "medium",
            "importability_to_repo": "medium",
            "theorem_amenability": "strong",
            "finite_state_compressibility": "likely_no",
            "renewal_like_compressibility": "likely_no",
            "countable_state_signal": "strong",
            "local_domain_signal": "medium",
            "repo_import_difficulty": "medium",
            "theorem_route_fit": "countable_state_pressure",
            "frontier_status": "promising",
            "note": "Explicit countable-alphabet GDMS with pressure asymptotics; clearly beyond the delayed-return finite-state-renewal limit.",
            "config": _candidate_config(
                "external.countable_gdms_countable_alphabet",
                "countable_gdms_dimension_spectrum",
                "The dimension spectrum of graph directed Markov systems",
                "arXiv:1802.01125",
                "countable_state_pressure",
                "graph_directed_markov",
                "countable_markov_shift",
            ),
        },
        {
            "candidate_id": "external.pseudo_markov_countable_alphabet",
            "source_id": "kuperberg_pseudomarkov_minimal_sets",
            "geometric_type": "pseudo_markov",
            "symbolic_type": "countable_pseudomarkov_shift",
            "countable_state_relevance": "strong",
            "local_domain_relevance": "medium",
            "importability_to_repo": "medium",
            "theorem_amenability": "strong",
            "finite_state_compressibility": "likely_no",
            "renewal_like_compressibility": "likely_no",
            "countable_state_signal": "strong",
            "local_domain_signal": "medium",
            "repo_import_difficulty": "medium",
            "theorem_route_fit": "countable_state_pressure",
            "frontier_status": "promising",
            "note": "Pseudo-Markov coding over a countable alphabet is the cleanest non-finite-state witness in the external pool.",
            "config": _candidate_config(
                "external.pseudo_markov_countable_alphabet",
                "kuperberg_pseudomarkov_minimal_sets",
                "Hausdorff dimension of Kuperberg minimal sets",
                "arXiv:1801.04034",
                "countable_state_pressure",
                "pseudo_markov",
                "countable_pseudomarkov_shift",
            ),
        },
        {
            "candidate_id": "external.countable_ifs_complete_connections",
            "source_id": "countable_ifs_overlaps_complete_connections",
            "geometric_type": "countable_conformal_ifs_with_overlaps",
            "symbolic_type": "complete_connections_countable_shift",
            "countable_state_relevance": "strong",
            "local_domain_relevance": "medium",
            "importability_to_repo": "medium",
            "theorem_amenability": "medium",
            "finite_state_compressibility": "likely_no",
            "renewal_like_compressibility": "unknown",
            "countable_state_signal": "medium",
            "local_domain_signal": "medium",
            "repo_import_difficulty": "medium",
            "theorem_route_fit": "induced_renewal",
            "frontier_status": "partial",
            "note": "Countable-overlap geometry is useful, but the route is more measure-theoretic than a clean next theorem target.",
        },
    ]

    for candidate in candidate_families[:3]:
        cfg = candidate["config"]
        _write_config(external_dir / f"{cfg['experiment_id']}.json", cfg)

    report_candidates = [
        {k: v for k, v in candidate.items() if k != "config"}
        for candidate in candidate_families
    ]

    top_candidates = [
        candidate_families[1],
        candidate_families[2],
        candidate_families[0],
    ]
    decision = "external_witness_imported"

    report = {
        "schema_version": "1.0",
        "shortlist_id": "external-witness-import-v1",
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
        "decision": decision,
        "source_families_examined": source_families,
        "candidate_families": report_candidates,
        "top_candidates": [
            {
                k: v
                for k, v in candidate.items()
                if k
                not in {
                    "config",
                }
            }
            for candidate in top_candidates
        ],
        "selection_rule": "Prefer sources that are explicitly countable-state or non-SFT, have a direct geometric bridge to the repo language, and are concrete enough to freeze as external witness skeletons.",
        "notes": [
            "The current delayed-return theorem package is closed but finite-state-renewal-like only, so it is not the frontier target we want.",
            "The imported countable-GDMS and pseudo-Markov directions are materially better because they already live beyond finite-state renewal-like control in the literature.",
            "The local IFS bridge is the most repo-native import and supplies the geometric language needed for the next theorem branch.",
        ],
    }

    report_dir = repo_root / "results" / "external_witness_import"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "report.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    csv_path = report_dir / "report.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "candidate_id",
                "source_id",
                "geometric_type",
                "symbolic_type",
                "countable_state_relevance",
                "local_domain_relevance",
                "importability_to_repo",
                "theorem_amenability",
                "finite_state_compressibility",
                "renewal_like_compressibility",
                "countable_state_signal",
                "local_domain_signal",
                "repo_import_difficulty",
                "theorem_route_fit",
                "frontier_status",
            ],
        )
        writer.writeheader()
        for candidate in report_candidates:
            writer.writerow({k: v for k, v in candidate.items() if k != "note"})

    note_lines = [
        "# External Witness Import v1",
        "",
        "## Question",
        "Which external literature-backed family should replace the blocked in-repo redesign language as the next theorem target?",
        "",
        "## External source families examined",
    ]
    for src in source_families:
        note_lines.append(
            f"- {src['paper_title_short']} ({src['paper_ref']}): {src['why_considered']}"
        )
    note_lines.extend(
        [
            "",
            "## What counts as a usable imported witness",
            "- It must be beyond finite-state-renewal-like control in the theorem-relevant sense.",
            "- It must be concrete enough to anchor a repo-ready candidate family or config skeleton.",
            "- It must be materially better than the closed delayed-return branch, which is theorem-closed but still finite-state-renewal-like on audit.",
            "",
            "## Top imported candidates",
        ]
    )
    for cand in top_candidates:
        note_lines.append(
            f"- `{cand['candidate_id']}` from `{cand['source_id']}`: `promising`; countable-state signal `{cand['countable_state_signal']}`, local-domain signal `{cand['local_domain_signal']}`, route fit `{cand['theorem_route_fit']}`."
        )
    note_lines.extend(
        [
            "",
            "## Why they are better than current in-repo families",
            "- The current delayed-return package is closed but finite-state-renewal-like only.",
            "- The imported countable-GDMS and pseudo-Markov candidates are explicitly countable-alphabet systems, so they are not trapped in the finite-state-renewal regime.",
            "- The local IFS bridge is the best repo-language anchor because it keeps the admissible-composition viewpoint while escaping the old toy redesign collapses.",
            "",
            "## Decision",
            f"- `{decision}`",
            "",
            "## Next theorem branch enabled",
            "- A countable-state pressure / local-domain bridge branch anchored in an imported witness family.",
        ]
    )
    note_path = repo_root / "docs" / "internal" / "external_witness_import_v1.md"
    note_path.write_text("\n".join(note_lines) + "\n", encoding="utf-8")

    shortlist = {
        "schema_version": "1.0",
        "shortlist_id": "external-witness-import-v1",
        "generated_at_utc": report["generated_at_utc"],
        "decision": decision,
        "source_families_examined": source_families,
        "candidate_families": report_candidates,
        "top_candidates": [
            {
                "candidate_id": candidate["candidate_id"],
                "source_id": candidate["source_id"],
                "geometric_type": candidate["geometric_type"],
                "symbolic_type": candidate["symbolic_type"],
                "countable_state_relevance": candidate["countable_state_relevance"],
                "local_domain_relevance": candidate["local_domain_relevance"],
                "importability_to_repo": candidate["importability_to_repo"],
                "theorem_amenability": candidate["theorem_amenability"],
                "frontier_status": candidate["frontier_status"],
                "note": candidate["note"],
            }
            for candidate in top_candidates
        ],
        "selection_rule": "Prefer external families that are explicitly countable-state or non-SFT, with a usable geometric bridge into the repo's local-domain language.",
        "notes": [
            "Imported candidates are literature-backed skeletons, not yet numerically run through the repo's current engines.",
            "The goal is to move from a finite-state-renewal-like theorem branch to a countable-state or local-domain bridge branch.",
        ],
    }
    shortlist_path = repo_root / "docs" / "internal" / "external_witness_shortlist_v1.json"
    shortlist_path.write_text(json.dumps(shortlist, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"wrote {report_path}")
    print(f"decision={decision}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
