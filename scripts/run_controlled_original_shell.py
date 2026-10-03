#!/usr/bin/env python3
"""Build exact interval evidence for a controlled original-parameter shell."""
from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import sys


def run():
    root=Path(__file__).resolve().parents[1]
    sys.path.insert(0,str(root/'src'))
    from contextual_cantor.controlled_shell import (
        certify_cycle,certify_entry_prefix,certify_six_role_dependence,
    )
    from contextual_cantor.original_loop_extension import (
        construct_original_loop_extension,exact_fixed_half_join,
    )
    from contextual_cantor.controlled_pressure_separation import certify_pressure_separation
    config=json.loads((root/'configs/experiments/generated/continuous_full_loop_kernel_shell.json')
                      .read_text(),parse_float=Q)['parameters']
    expected={'lens_hysteresis':Q(17,1000),'packaging_hysteresis':Q(12,1000),
        'budget_income_scale':Q(108,100),'budget_cost_scale':Q(96,100),
        'tau_initial':Q(88,100),'action_temperature_bias':Q(45,1000),
        'lens_temperature_shift':Q(2,100)}
    if (config['kernel_dim']!=20 or any(config['pilot_parameters'].get(k)!=v for k,v in expected.items())
            or config['pilot_parameters'].get('kernel_minorization',0)!=0
            or not all(config['primitive_activity'].get(f'P{i}') is True for i in range(1,7))):
        raise ValueError('source pilot configuration differs from the certified original parameters')
    w=construct_original_loop_extension()
    join=[exact_fixed_half_join(w,c) for c in (Q(79,100),Q(4,5))]
    report=certify_cycle()
    report['entry_prefix']=certify_entry_prefix()
    report['six_role_dependence']=certify_six_role_dependence()
    report['six_role_nonredundancy_certified']=True
    report['original_extension_pair_joined_to_this_shell']=True
    report['fixed_half_join']={'target_construction_score':'159/200',
        'actual_source_score_interval':['79/100','4/5'],
        'endpoint_noise_caps':[str(j.maximum_noise) for j in join],
        'legal_noise_lower_bound':'1/400','initial_budget':'3',
        'final_variations_squared_equal':True,
        'first_history_difference_supported_on_columns':[0,1,2],
        'second_kernel_rows_equal_on_those_columns':True}
    report['all_time_return']='positive stochastic target plus legal compensating noise; phase/budget induction'
    report['arithmetic_scope']='exact-real interpretation of the original formulas; not bitwise floating simulator invariance'
    report['floating_quantile_caveat']='uniform prefix ties are certified exactly; floating rounding may choose different cores'
    report['six_role_scope']='each primitive changes the physical update at some shell state; not every coordinate at every state'
    report['conditional_pressure_gap']='not established; the joined strict pair has zero two-world gap'
    report['exact_paper_base_definition']='unresolved; extension covers the declared coarse scalar-history object'
    report['same_potential_pressure_separation']=certify_pressure_separation()
    report['generated_at_utc']=datetime.now(timezone.utc).isoformat()
    inputs=['configs/mathematics/original_controlled_cycle.json',
        'configs/experiments/generated/continuous_full_loop_kernel_shell.json',
        'src/contextual_cantor/continuous_kernel_substrate.py',
        'src/contextual_cantor/rational_interval.py','src/contextual_cantor/controlled_shell.py',
        'src/contextual_cantor/original_loop_extension.py',
        'src/contextual_cantor/controlled_pressure_separation.py','lean/ControlledShell.lean',
        'lean/ConditionalPressure.lean',
        'lean/LoopExtension.lean','scripts/run_controlled_original_shell.py']
    report['input_sha256']={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in inputs}
    out=root/'results/controlled_original_shell/report.json'
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(f'wrote {out}')
    return 0


if __name__=='__main__':
    raise SystemExit(run())
