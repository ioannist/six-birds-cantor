#!/usr/bin/env python3
from __future__ import annotations

import csv
import datetime as dt
import json
import math
import sys
from pathlib import Path
from typing import Any


def _root_proxy_and_rows(config: dict[str, Any], depths: list[int]) -> tuple[float | None, list[dict[str, Any]]]:
    from contextual_cantor.local_pressure import analyze_config

    analysis = analyze_config(config, depths=depths)
    rows = analysis["rows"]
    root_proxy = rows[-1].get("upper_root") if rows else None
    return root_proxy, rows


def _memory_growth_proxy(config: dict[str, Any]) -> dict[str, Any]:
    family_id = str(config["family_id"])
    params = config["parameters"]
    if family_id.startswith("contextual_local.prefix_memory"):
        transitions = params.get("transition_digits", {})
        return {"method": "explicit_transition_context_count", "value": len(transitions)}
    if str(config["engine"]) == "classical_similarity":
        return {"method": "single_scale_branching", "value": len(params.get("allowed_digits", []))}
    if str(config["engine"]) == "local_ifs":
        return {"method": "local_domain_map_count", "value": len(params.get("maps", []))}
    return {"method": "unknown", "value": None}


def _generate_classical_intervals(base: int, allowed_digits: list[int], depth: int) -> list[tuple[float, float]]:
    words = [[]]
    for _ in range(depth):
        nxt = []
        for word in words:
            for d in allowed_digits:
                nxt.append(word + [d])
        words = nxt
    width = 1.0 / (float(base) ** depth)
    intervals = []
    for word in words:
        offset = 0.0
        for i, digit in enumerate(word, start=1):
            offset += float(digit) / (float(base) ** i)
        intervals.append((offset, offset + width))
    return intervals


def _generate_prefix_intervals(base: int, start_digits: list[int], transitions: dict[str, list[int]], depth: int) -> list[tuple[float, float]]:
    if depth <= 0:
        return [(0.0, 1.0)]
    words = [[d] for d in start_digits]
    for _ in range(1, depth):
        nxt = []
        for word in words:
            for d in transitions[str(word[-1])]:
                nxt.append(word + [d])
        words = nxt
    width = 1.0 / (float(base) ** depth)
    intervals = []
    for word in words:
        offset = 0.0
        for i, digit in enumerate(word, start=1):
            offset += float(digit) / (float(base) ** i)
        intervals.append((offset, offset + width))
    return intervals


def _generate_local_ifs_raw_intervals(config: dict[str, Any], depth: int) -> list[tuple[float, float]]:
    from contextual_cantor.local_ifs import Interval, IntervalUnion, LocalIFS

    local_ifs = LocalIFS.from_dict(config["parameters"])
    current = [IntervalUnion.from_interval(Interval(0.0, 1.0))]
    for _ in range(depth):
        nxt = []
        for union in current:
            for local_map in local_ifs.maps:
                restricted = union.intersection_interval(local_map.domain)
                if restricted.is_empty():
                    continue
                mapped = local_map.apply_union(restricted)
                if mapped.is_empty():
                    continue
                nxt.append(mapped)
        current = nxt
    out = []
    for union in current:
        for iv in union.intervals:
            out.append((iv.left, iv.right))
    return out


def _packaged_intervals(config: dict[str, Any], depth: int) -> list[tuple[float, float]] | None:
    from contextual_cantor.local_pressure import lower_partition_sum
    engine = str(config["engine"])
    family_id = str(config["family_id"])
    params = config["parameters"]

    if engine == "classical_similarity":
        union = _coalesced_intervals(_generate_classical_intervals(int(params["base"]), [int(d) for d in params["allowed_digits"]], depth))
        return union
    if family_id.startswith("contextual_local.prefix_memory"):
        union = _coalesced_intervals(_generate_prefix_intervals(int(params["base"]), [int(d) for d in params["start_digits"]], {k: [int(v) for v in vals] for k, vals in params["transition_digits"].items()}, depth))
        return union
    if engine == "local_ifs":
        from contextual_cantor.local_ifs import Interval, IntervalUnion, LocalIFS, iterate_set
        local_ifs = LocalIFS.from_dict(params)
        seq = iterate_set(local_ifs, steps=depth)
        union = seq[-1]
        return [(iv.left, iv.right) for iv in union.intervals]
    lower = lower_partition_sum(config, depth=depth, s=0.0)
    if lower is None:
        return None
    return None


def _coalesced_intervals(intervals: list[tuple[float, float]]) -> list[tuple[float, float]]:
    if not intervals:
        return []
    intervals = sorted(intervals)
    out = [list(intervals[0])]
    for left, right in intervals[1:]:
        prev = out[-1]
        if left <= prev[1] + 1e-15:
            prev[1] = max(prev[1], right)
        else:
            out.append([left, right])
    return [(left, right) for left, right in out]


def _max_overlap_multiplicity(intervals: list[tuple[float, float]]) -> int | None:
    if not intervals:
        return None
    events = []
    for left, right in intervals:
        events.append((left, 0, 1))
        events.append((right, 1, -1))
    events.sort()
    current = 0
    best = 0
    for _, _, delta in events:
        current += delta
        if current > best:
            best = current
    return best


def _raw_intervals(config: dict[str, Any], depth: int) -> list[tuple[float, float]]:
    engine = str(config["engine"])
    family_id = str(config["family_id"])
    params = config["parameters"]
    if engine == "classical_similarity":
        return _generate_classical_intervals(int(params["base"]), [int(d) for d in params["allowed_digits"]], depth)
    if family_id.startswith("contextual_local.prefix_memory"):
        return _generate_prefix_intervals(int(params["base"]), [int(d) for d in params["start_digits"]], {k: [int(v) for v in vals] for k, vals in params["transition_digits"].items()}, depth)
    if engine == "local_ifs":
        return _generate_local_ifs_raw_intervals(config, depth)
    return []


def _family_status(max_mults: list[int | None], ratios: list[float | None], drift: float | None, family_id: str) -> tuple[str, str]:
    observed_mults = [m for m in max_mults if m is not None]
    observed_ratios = [r for r in ratios if r is not None]
    max_mult = max(observed_mults) if observed_mults else None
    max_ratio = max(observed_ratios) if observed_ratios else None
    if family_id == "contextual_local.prefix_memory_last_digit_rule":
        if max_mult is not None and max_mult <= 2 and max_ratio is not None and max_ratio <= 2.0 and (drift is None or drift <= 0.03):
            return "promising", "Bounded-overlap proxy stays uniformly small on checked depths; this is the main candidate for the overlap-lemma sprint."
    if max_mult is not None and max_mult >= 5:
        return "blocked", "Multiplicity already grows to a level inconsistent with an easy bounded-overlap route on checked depths."
    if max_ratio is not None and max_ratio >= 4.0:
        return "blocked", "Upper/lower ratio proxy is too large for a clean bounded-ratio coincidence route."
    if drift is not None and drift >= 0.05:
        return "blocked", "Depth sensitivity is high enough that bounded-overlap does not look like the main obstruction."
    return "inconclusive", "Current diagnostics do not falsify bounded-overlap, but they are not yet strong enough to justify the lemma sprint automatically."


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    src_path = repo_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

    from contextual_cantor.local_pressure import upper_partition_sum, lower_partition_sum

    family_paths = [
        repo_root / 'configs' / 'experiments' / 'contextual' / 'prefix_memory_last_digit_rule.json',
        repo_root / 'configs' / 'experiments' / 'contextual' / 'prefix_memory_no_22_base3.json',
        repo_root / 'configs' / 'experiments' / 'contextual' / 'domain_gated_two_map_local_ifs.json',
        repo_root / 'configs' / 'experiments' / 'local_ifs' / 'nested_three_map_local_ifs.json',
        repo_root / 'configs' / 'experiments' / 'classical' / 'middle_thirds.json',
        repo_root / 'configs' / 'experiments' / 'classical' / 'restricted_digits_base5_024.json',
    ]
    depths = [4, 6, 8, 10]
    families = []
    csv_rows = []
    for path in family_paths:
        config = json.loads(path.read_text(encoding='utf-8'))
        family_id = str(config['family_id'])
        applicable_depths = depths if str(config['engine']) != 'local_ifs' or family_id == 'contextual_local.domain_gated_two_map_local_ifs' else [4, 6, 8]
        root_proxy, rows = _root_proxy_and_rows(config, applicable_depths)
        ratios = {}
        multiplicities = {}
        upper_lower_gap = {}
        for row in rows:
            depth = int(row['depth'])
            raw = _raw_intervals(config, depth)
            mult = _max_overlap_multiplicity(raw)
            multiplicities[str(depth)] = mult
            if root_proxy is not None:
                upper_z, _ = upper_partition_sum(config, depth=depth, s=root_proxy)
                lower = lower_partition_sum(config, depth=depth, s=root_proxy)
                ratio = None if lower is None or lower[0] == 0 else upper_z / lower[0]
            else:
                ratio = None
            ratios[str(depth)] = ratio
            gap = None
            if row.get('upper_root') is not None and row.get('lower_root') is not None:
                gap = row['upper_root'] - row['lower_root']
            upper_lower_gap[str(depth)] = gap
            csv_rows.append({
                'family_id': family_id,
                'depth': depth,
                'max_overlap_multiplicity': mult,
                'ratio_proxy': ratio,
                'upper_lower_gap': gap,
                'upper_root': row.get('upper_root'),
                'lower_root': row.get('lower_root'),
            })
        upper_roots = [row['upper_root'] for row in rows if row.get('upper_root') is not None]
        last_step_drift = None
        if len(upper_roots) >= 2:
            last_step_drift = abs(upper_roots[-1] - upper_roots[-2])
        depth_sensitivity = {
            'depth_series': applicable_depths,
            'last_step_drift': last_step_drift,
            'max_spread_upper_root': (max(upper_roots) - min(upper_roots)) if upper_roots else None,
        }
        status, note = _family_status(list(multiplicities.values()), list(ratios.values()), last_step_drift, family_id)
        artifact_paths = []
        output_root = config.get('output_root')
        if isinstance(output_root, str):
            artifact_paths.append(output_root)
        families.append({
            'family_id': family_id,
            'config_path': path.relative_to(repo_root).as_posix(),
            'depths_checked': applicable_depths,
            'root_proxy_used': root_proxy,
            'max_overlap_multiplicity_by_depth': multiplicities,
            'max_overlap_multiplicity_overall': max(v for v in multiplicities.values() if v is not None) if any(v is not None for v in multiplicities.values()) else None,
            'ratio_proxy_by_depth': ratios,
            'memory_growth_proxy': _memory_growth_proxy(config),
            'depth_sensitivity': depth_sensitivity,
            'bounded_overlap_status': status,
            'classification_note': note,
            'artifact_paths': artifact_paths,
            'upper_lower_gap_by_depth': upper_lower_gap,
        })

    by_id = {f['family_id']: f for f in families}
    decision = 'advance_to_overlap_lemmas' if by_id['contextual_local.prefix_memory_last_digit_rule']['bounded_overlap_status'] == 'promising' else 'stop_bounded_overlap_branch'
    notes = [
        'Bounded overlap is being tested as a replacement for disjoint cylinder geometry in the T19 coincidence step.',
        'The kept assumptions are the T19 fixed assumptions except that disjoint cylinder geometry is replaced by a bounded cylinder multiplicity hypothesis.',
        'Any proof sprint after this ticket still needs a geometric overlap-counting lemma giving a family-uniform multiplicity bound M independent of depth.',
    ]
    payload = {
        'schema_version': '1.0',
        'bounded_overlap_id': 'bounded-overlap-v1',
        'generated_at_utc': dt.datetime.now(dt.timezone.utc).isoformat().replace('+00:00','Z'),
        'target_theorem_class': 'narrow_hybrid_affine_cylinder_class',
        'candidate_enlarged_class_label': 'finite-memory affine class with exact cylinder packaging and bounded cylinder multiplicity',
        'fixed_assumptions_from_t15': [
            'uniform_contraction','finite_memory_bound','stationary_admissibility_rule','bounded_distortion','usable_separation','feedback_free_admissibility','fixed_lens','fixed_packaging','lower_pressure_packaging_admissible','lens_affects_admissibility','packaging_affects_admissibility','exact_cylinder_packaging'
        ],
        'new_overlap_assumption': 'bounded_cylinder_multiplicity',
        'families': families,
        'decision': decision,
        'notes': notes,
    }

    out_dir = repo_root / 'results' / 'bounded_overlap_diagnostics'
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / 'report.json'
    report_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding='utf-8')
    with (out_dir / 'report.csv').open('w', newline='', encoding='utf-8') as fh:
        writer = csv.DictWriter(fh, fieldnames=['family_id','depth','max_overlap_multiplicity','ratio_proxy','upper_lower_gap','upper_root','lower_root'])
        writer.writeheader()
        writer.writerows(csv_rows)

    docs_path = repo_root / 'docs' / 'internal' / 'bounded_overlap_class_v1.json'
    docs_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding='utf-8')
    print(f'wrote {report_path}')
    print(f'decision={decision}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
