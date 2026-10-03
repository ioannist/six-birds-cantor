#!/usr/bin/env python3
"""Record all-word bounds and the exact scope of the analytic law construction."""
from datetime import datetime,timezone
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import sys


def run():
    root=Path(__file__).resolve().parents[1]
    sys.path.insert(0,str(root/'src'))
    from contextual_cantor.all_word_pressure_disintegration import certify_all_word_pressure_disintegration
    config=json.loads((root/'configs/experiments/generated/continuous_full_loop_kernel_shell.json')
                      .read_text(),parse_float=Q)['parameters']
    expected={'lens_hysteresis':Q(17,1000),'packaging_hysteresis':Q(12,1000),
        'budget_income_scale':Q(108,100),'budget_cost_scale':Q(96,100),
        'tau_initial':Q(88,100),'action_temperature_bias':Q(45,1000),
        'lens_temperature_shift':Q(2,100)}
    if (config['kernel_dim']!=20 or any(config['pilot_parameters'].get(k)!=v for k,v in expected.items())
            or config['pilot_parameters'].get('kernel_minorization',0)!=0
            or not all(config['primitive_activity'].get(f'P{i}') is True for i in range(1,7))):
        raise ValueError('source pilot parameters differ from the original carrier')
    report=certify_all_word_pressure_disintegration()
    report['generated_at_utc']=datetime.now(timezone.utc).isoformat()
    inputs=['configs/mathematics/original_controlled_cycle.json',
        'configs/experiments/generated/continuous_full_loop_kernel_shell.json',
        'src/contextual_cantor/continuous_kernel_substrate.py',
        'src/contextual_cantor/rational_interval.py','src/contextual_cantor/controlled_shell.py',
        'src/contextual_cantor/original_loop_extension.py',
        'src/contextual_cantor/controlled_pressure_separation.py',
        'src/contextual_cantor/packaged_world_disintegration.py',
        'src/contextual_cantor/all_word_pressure_disintegration.py',
        'scripts/run_all_word_pressure_disintegration.py',
        'lean/ReferencePressure.lean','lean/WeightedHistoryBounds.lean',
        'docs/internal/all_word_pressure_disintegration_2026_10_03.md']
    report['input_sha256']={f:hashlib.sha256((root/f).read_bytes()).hexdigest() for f in inputs}
    out=root/'results/all_word_pressure_disintegration/report.json'
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(f'wrote {out}')
    return 0


if __name__=='__main__':
    raise SystemExit(run())
