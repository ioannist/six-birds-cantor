#!/usr/bin/env python3
"""Receipt for original sparse-kernel pressure and derived branching bounds."""
from datetime import datetime,timezone
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path


def run() -> int:
    root=Path(__file__).resolve().parents[1]
    paths=['configs/experiments/generated/continuous_full_loop_kernel.json',
           'configs/experiments/generated/continuous_full_loop_kernel_shell.json']
    configs=[]
    for p in paths:
        cfg=json.loads((root/p).read_text(),parse_float=Q)['parameters']
        params=cfg['pilot_parameters']
        assert cfg['kernel_dim'] in (16,20)
        assert all(cfg['primitive_activity'].values())
        assert params.get('kernel_minorization',0)==0
        assert params['lens_hysteresis']<=Q(3,100)
        assert params['packaging_hysteresis']+Q(3,100)<=Q(48,1000)
        configs.append({'config_path':p,'dimension':cfg['kernel_dim'],
                        'original_parameters_within_derived_selector_bounds':True})
    pre=Q(13,20)*Q(501,4000)*Q(1799,20000)/Q(79,50)
    post=(pre-Q(9,2000))/Q(109,100)
    assert post>Q(1,10000)
    inputs=paths+['src/contextual_cantor/continuous_kernel_substrate.py',
        'src/contextual_cantor/cocycle_pressure.py',
        'scripts/run_continuous_pressure_checks.py','scripts/run_continuous_pressure_closure_checks.py',
        'lean/SparsePressure.lean','lean/MatrixPressure.lean','lean/KernelCocycle.lean',
        'docs/internal/original_sparse_pressure_2026_10_02.md','scripts/run_original_sparse_pressure.py']
    report={
        'generated_at_utc':datetime.now(timezone.utc).isoformat(),
        'scope':'ideal_real_original_full_role_physical_update_without_added_minorization',
        'original_main_theorem_package_complete':False,
        'original_tighter_audited_shell_membership':'not_established',
        'outer_update_changed':False,'configs':configs,
        'input_sha256':{p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in inputs},
        'observable_variants':{
            'pressure_existence_and_restoration':{'coefficients':['.28','.32','.10','.08']},
            'pressure_closure':{'coefficients':['.25','.30','.05','.05']}},
        'both_observable_bounds':['log(5/4)','log(10)'],
        'declared_observable_clamp':'inactive on this original full-role physical carrier',
        'sparse_pressure_exists':'for any nonempty invariant instance; matrix bounds mechanized',
        'strict_pressure_decrease':'derived parameter secant bound mechanized',
        'positive_parameter_regularities':'Holder convexity and interior continuity/local Lipschitz; analytic',
        'recurrent_branch':{'source_pre_phase':8,'selected_packaging':'budget_audit_packaging',
            'minimum_selector_advantage':'51/1000','maximum_original_hysteresis':'48/1000',
            'at_least_core_columns':4,'pre_noise_core_floor':str(pre),
            'post_noise_core_floor':str(post),'short_core_floor':'1/10000',
            'recurrence_period':12,'source_selector_and_gate_bridge':'analytic',
            'noise_clipping_normalization_return':'mechanized'},
        'positive_root':{'anchor_parameter':'1/32',
            'anchor_pressure_lower_bound':'log(8/5)/24 > 0',
            'negative_anchor_parameter':1,'negative_anchor_upper_bound':'-log(5/4)',
            'unique_root_interval':['1/32','1'],
            'phase_count_and_root_assembly':'analytic',
            'uniform_positive_entry_floor_on_every_kernel':'not_required'},
        'fully_mechanized_simulator_instance':False,
        'conditional_disintegration_gap':'not supplied by pressure existence or strict extension',
    }
    out=root/'results/original_sparse_pressure/report.json'
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
    print(f'wrote {out}')
    return 0


if __name__=='__main__':
    raise SystemExit(run())
