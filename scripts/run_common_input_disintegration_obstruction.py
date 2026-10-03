#!/usr/bin/env python3
"""Bind the common-input zero-gap theorem to the actual twenty-state witness.

This is analytic theorem-instance evidence plus exact rational source checks.
The countable reference measures are not numerically instantiated here.
"""
from datetime import datetime,timezone
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import sys


def current_receipt(root,relative):
    path=root/relative
    report=json.loads(path.read_text())
    hashes=report.get('input_sha256',{})
    if not hashes:
        raise ValueError(f'no source binding in {relative}')
    stale=[p for p,h in hashes.items() if hashlib.sha256((root/p).read_bytes()).hexdigest()!=h]
    if stale:
        raise ValueError(f'stale input receipt {relative}: {stale}')
    return report,hashlib.sha256(path.read_bytes()).hexdigest()


def exact_warm_checks():
    from contextual_cantor.original_loop_extension import (
        construct_original_loop_extension,exact_fixed_half_join,integer_moving_history_rows,
    )
    w=construct_original_loop_extension()
    joins=tuple(exact_fixed_half_join(w,c) for c in (Q(79,100),Q(4,5)))
    r=joins[0].common_kernel
    support=(0,1,2)
    if (r!=joins[1].common_kernel or r!=tuple(zip(*r))
            or any(sorted(a)!=sorted(b) for a,b in zip(*w.kernels))
            or any(w.kernels[0][i][j]!=w.kernels[1][i][j]
                   for i in range(20) for j in range(20) if j not in support)
            or any(r[j]!=r[0] for j in support)):
        raise ArithmeticError('original matched-history source bridge failed')
    if (any(a.minorization<=0 or a.lumpability_defect<=0 for a in w.audit)
            or w.audit[0].stationary==w.audit[1].stationary
            or any(a.stationary==w.spectral.stationary for a in w.audit)):
        raise ArithmeticError('actual saturation, strictness or forcing witness failed')
    scales=(Q(2,3),Q(3,5))
    rows=tuple(integer_moving_history_rows((k,r),2,scales) for k in w.kernels)
    if rows[0]!=rows[1]:
        raise ArithmeticError('exact two-step history identity failed')
    # Factor out the common scalar; do NOT replace the original real q by
    # the rational test scales. Actual s=2 partitions multiply these raw
    # coefficients by exp(-2*(q_0+q_1)), which is common and positive.
    raw_rows=tuple(v/(scales[0]*scales[1])**2 for v in rows[0])
    raw_partitions=tuple(sum(p*v for p,v in zip(a.stationary,raw_rows)) for a in w.audit)
    if raw_partitions[0]==raw_partitions[1]:
        raise ArithmeticError('finite conditional partitions unexpectedly coincide')
    return w,{
        'kernel_dimension':20,'timescale':'3/5','active_lens':'audit_flow_quantile_lens',
        'actual_objects':[[str(v) for v in a.stationary] for a in w.audit],
        'initial_probability_floors':[str(min(a.stationary)) for a in w.audit],
        'completion_entry_floors':[str(a.minorization) for a in w.audit],
        'macro_lumpability_defects':[str(a.lumpability_defect) for a in w.audit],
        'two_step_norm_matching_support':list(support),
        'actual_source_score_interval':['79/100','4/5'],
        'fixed_join_noise_caps':[str(j.maximum_noise) for j in joins],
        'minimum_original_noise_support':'1/400',
        'two_step_unscaled_partitions':list(map(str,raw_partitions)),
        'two_step_unscaled_partition_difference':str(raw_partitions[0]-raw_partitions[1]),
        'finite_source_factor_at_s_two':'exp(-2*(q_0+q_1)); original q, common to both warm worlds',
        'finite_partition_scope':'the exact coefficient differs even though the true limiting conditional pressures agree',
    }


def original_panel_checks(root):
    """Derive singleton exact fibers on BOTH original fixed-input witnesses.

    The raw recorded table is interpreted by exact real row normalization,
    as in the existing support proof. This is not seeded-real reachability.
    """
    from contextual_cantor.completion_support import completion_support_certificate,verify_power_support
    support_path=root/'results/packaging_completion_endomap/support_summary.json'
    report_path=root/'results/packaging_completion_endomap/report.json'
    support=json.loads(support_path.read_text())
    if (support['full_report_sha256']!=hashlib.sha256(report_path.read_bytes()).hexdigest()
            or support['source_sha256']!=hashlib.sha256((root/'src/contextual_cantor/continuous_kernel_substrate.py').read_bytes()).hexdigest()
            or support['support_verifier_sha256']!=hashlib.sha256((root/'src/contextual_cantor/completion_support.py').read_bytes()).hexdigest()):
        raise ValueError('original recorded-input support binding is stale')
    full=json.loads(report_path.read_text())
    output=[]
    for cfg in support['configs']:
        if cfg['config_sha256']!=hashlib.sha256((root/cfg['config_path']).read_bytes()).hexdigest():
            raise ValueError('original panel configuration has changed')
        data=next(s for s in full['summaries'] if s['config_id']==cfg['config_id'])
        kernel=data['recorded_input_kernel']
        panels=[]
        for tau in data['tau_values_checked']:
            for lens in data['lens_values_checked']:
                runs=[r for r in data['runs'] if r['tau']==tau and r['lens_state']==lens]
                if not runs or any(r['packaging_state']['groups']!=runs[0]['packaging_state']['groups'] for r in runs):
                    raise ValueError('the fixed-input descriptor does not determine one package')
                groups=runs[0]['packaging_state']['groups']
                cert=completion_support_certificate(kernel,groups)
                archived=cfg['completion_support_certificates'][lens]
                if (cert!=archived or not cert['every_kernel_column_has_positive_entry']
                        or cert['transport_power'] is None
                        or not verify_power_support(cert['transport_power'])
                        or cert['completion_power'] is None
                        or not verify_power_support(cert['completion_power'])):
                    raise ArithmeticError('original primitive-completion source certificate failed')
                panels.append({'tau':tau,'lens':lens,'sampled_initial_count':len(runs),
                    'groups':groups,'transport_positive_power':cert['transport_power']['power'],
                    'completion_positive_power':cert['completion_power']['power'],
                    'exact_fixed_probability_object_count':1,
                    'exact_limit_frequency_weights':['1'],
                    'weight_proof':'ALL mass-one starts converge to the unique fixed vector; transient rounded signatures are not separate exact fibers'})
        output.append({'config_id':cfg['config_id'],'kernel_dimension':cfg['kernel_dim'],
            'recorded_kernel_hex':[[float(x).hex() for x in row] for row in kernel],
            'kernel_data_sha256':cert['kernel_data_sha256'],
            'real_input_interpretation':'K_ij=v_ij/sum_j(v_ij), preserving support of the recorded binary-rational table',
            'panels':panels,'ideal_real_seeded_snapshot_certified':False})
    if {c['kernel_dimension'] for c in output}!={16,20}:
        raise ValueError('both original recorded witnesses are required')
    return output,hashlib.sha256(support_path.read_bytes()).hexdigest()


def run():
    root=Path(__file__).resolve().parents[1]
    sys.path.insert(0,str(root/'src'))
    basis,digest=current_receipt(root,'results/all_word_pressure_disintegration/report.json')
    if (basis.get('periodic_only_restriction') is not False
            or basis.get('reference_pressure_equals_global_shell_supremum_analytic') is not True
            or len(basis.get('all_time_carriers',()))!=2
            or len(basis.get('legal_entry_prefixes',()))!=2):
        raise ValueError('the full all-word source construction is missing')
    w,exact=exact_warm_checks()
    original_panels,support_digest=original_panel_checks(root)
    profiles=[]
    for row in basis['uniform_all_word_pressure_profiles']:
        intervals=[tuple(map(Q,p)) for p in row['carrier_pressure_intervals']]
        global_interval=[str(max(p[k] for p in intervals)) for k in (0,1)]
        profiles.append({'parameter':row['parameter'],'observable':row['observable'],
            'global_shell_pressure_interval':global_interval,
            'both_conditional_pressures':'P_S, exactly; proved through actual reference integrals',
            'gap_exact':'0'})
    report={
        'scope':'the SAME exact-real original-parameter twenty-state controlled shell, potential, current completion readout and coarse base as the all-word positive-gap construction',
        'generated_at_utc':datetime.now(timezone.utc).isoformat(),
        'basis_receipt':'results/all_word_pressure_disintegration/report.json',
        'basis_receipt_sha256':digest,
        'reference_law':'sample actual warm audit object with weights w,1-w; independently sample return carrier with weights theta,1-theta; then its previously constructed fixed all-word law nu_i; use the same legal join and entry controls',
        'weights_scope':'any fixed 0<w<1 and 0<theta<1; not asserted empirical frequencies',
        'displayed_current_object_weights':['1/2','1/2'],
        'displayed_future_carrier_weights':['1/2','1/2'],
        'displayed_joint_weights':[['1/4','1/4'],['1/4','1/4']],
        'fiber_map':'world -> its actual current audit stationary vector; future-carrier labels are NOT packaging objects',
        'path_integrand':'product_t A_s(i_t,i_(t+1))/K_t(i_t,i_(t+1)); unchanged original A_s and original K path reference',
        'original_potential_unchanged':True,'original_outer_update_unchanged':True,
        'same_shell_as_positive_gap_construction':True,
        'strict_current_object_extension':True,
        'saturation_and_material_fixed_completion_forcing':True,
        'full_shell_pressure_return_analytic':True,
        'zero_gap_for_all_nonnegative_parameters_and_both_original_q_definitions':True,
        'conditional_profiles_assigned_by_hand':False,
        'reference_measure_construction_analytic':True,
        'reference_measure_numerically_instantiated':False,
        'independent_original_raw_noise_law':False,
        'seeded_audited_shell_identified':False,
        'paper_current_state_family_interpretation_resolved':False,
        'original_generic_strictness_to_positive_gap_implication':False,
        'main_theorem_package_complete':False,
        'exact_source_checks':exact,
        'original_recorded_panel_audit':original_panels,
        'original_recorded_support_receipt':'results/packaging_completion_endomap/support_summary.json',
        'original_recorded_support_receipt_sha256':support_digest,
        'original_panel_weight_scope':'exact limits of repeated starts at fixed config/tau/lens have one object of weight one; this is not a multi-object descriptor law over varying kernels',
        'audited_profile_return':profiles,
        'formal_exports':['CantorAudit.constant_package_fiber_partition',
            'CantorAudit.expected_row_history_bounds',
            'CantorAudit.expected_row_history_same_pressure',
            'CantorAudit.common_input_actual_package_zero_gap'],
        'mechanization_scope':'actual Bochner integral comparisons, pressure transfer, actual-object conditioning, nonfactorization and zero gap; source dataset and compact variational measure construction remain analytic',
        'required_claim_repair':'specify the reference law/fibers and independently establish conditional-pressure separation; structural strictness and well-defined profiles alone cannot imply it',
    }
    inputs=['scripts/run_common_input_disintegration_obstruction.py',
        'src/contextual_cantor/original_loop_extension.py',
        'src/contextual_cantor/exact_completion.py',
        'src/contextual_cantor/completion_support.py',
        'lean/PrimitiveCompletion.lean',
        'lean/CommonInputDisintegration.lean','lean/HistoryConditioning.lean',
        'lean/LoopExtension.lean','lean/ReferencePressure.lean',
        'docs/internal/common_input_disintegration_obstruction_2026_10_03.md',
        'docs/internal/proof_dependency_conditional_disintegration_v1.json',
        'paper/sections/03_canonical_object.tex','paper/sections/07_conditional_disintegration.tex']
    report['input_sha256']={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in inputs}
    out=root/'results/common_input_disintegration_obstruction/report.json'
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(f'wrote {out}')
    return 0


if __name__=='__main__':
    raise SystemExit(run())
