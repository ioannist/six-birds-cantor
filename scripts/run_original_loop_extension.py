#!/usr/bin/env python3
"""Exact original-parameter warm-loop witness; not a global shell certificate."""
from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import sys


def run() -> int:
    root=Path(__file__).resolve().parents[1]
    sys.path.insert(0,str(root/'src'))
    from contextual_cantor.original_loop_extension import construct_original_loop_extension, exact_pre_noise
    w=construct_original_loop_extension()
    endpoints=[]
    for c in (Q(79,100),Q(4,5)):
        outputs=exact_pre_noise(w,c)
        endpoints.append({'package_score':str(c),
            'maximum_required_noise':str(max(abs(x-Q(1,20)) for m in outputs for row in m for x in row)),
            'legal_noise_amplitude':'9/2000'})
    inputs=['src/contextual_cantor/original_loop_extension.py',
            'src/contextual_cantor/exact_completion.py',
            'src/contextual_cantor/continuous_kernel_substrate.py',
            'scripts/run_continuous_pressure_closure_checks.py',
            'scripts/run_continuous_pressure_checks.py',
            'configs/experiments/generated/continuous_full_loop_kernel_shell.json',
            'lean/LoopExtension.lean','scripts/run_original_loop_extension.py']
    report={
        'generated_at_utc':datetime.now(timezone.utc).isoformat(),
        'scope':'exact_original_parameter_warm_controlled_pair_with_analytic_source_bridge',
        'main_theorem_package_complete':False,
        'original_global_shell_membership':'not_established',
        'seeded_reachability':'not_established',
        'exact_paper_base_definition':'unresolved',
        'outer_update_modified':False,'minorization_added':False,
        'input_sha256':{p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in inputs},
        'kernel_dimension':20,'tau':str(w.tau),'lens':'audit_flow_quantile_lens',
        'forward_kernel':[[str(x) for x in row] for row in w.kernels[0]],
        'reverse_kernel':'transpose of forward_kernel',
        'current_audit_groups':w.audit_groups,
        'pointwise_weighted_row_moment_equality':True,
        'audit_stationary':[[str(x) for x in a.stationary] for a in w.audit],
        'audit_split_coordinate_zero':str(w.audit[0].stationary[0]-w.audit[1].stationary[0]),
        'shared_spectral_stationary':[str(x) for x in w.spectral.stationary],
        'shared_cluster_stationary':[str(x) for x in w.cluster.stationary],
        'audit_macro_defects':[str(a.lumpability_defect) for a in w.audit],
        'legal_noise_endpoint_bounds':endpoints,
        'all_parameter_all_horizon_pressure_profile_bridge':
            'equal weighted row sums; rank-one second matrix; common arbitrary moving tail',
        'formal_endpoints':['CantorAudit.equal_rows_mul_rankOne',
            'CantorAudit.joinedHistory_norms_equal','CantorAudit.joinedHistory_partitions_equal'],
        'formal_instance_scope':'generic ordered-matrix bridge; 20-state dataset not imported as Lean terms',
        'conditional_disintegration':{'finite_two_world_equal_partitions':True,
            'gap_if_common_pressure_exists':'zero',
            'paper_conditional_law_identified':False},
    }
    out=root/'results/original_loop_extension/report.json'
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(f'wrote {out}')
    return 0


if __name__=='__main__':
    raise SystemExit(run())
