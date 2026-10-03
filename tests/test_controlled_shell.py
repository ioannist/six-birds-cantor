from fractions import Fraction as Q
import json
from pathlib import Path

import mpmath as mp
import pytest

from contextual_cantor.rational_interval import Interval as I
from contextual_cantor.controlled_shell import (
    load_cycle,informants,evaluate_phase,tau_box,certify_cycle,
    construct_entry_prefix,certify_entry_prefix,certify_six_role_dependence,
)
from contextual_cantor.original_loop_extension import (
    construct_original_loop_extension,exact_fixed_half_join,
)
from contextual_cantor.continuous_kernel_substrate import (
    KernelSubstrateState,PilotParameters,refresh_informants,compute_p4_lenses,
    compute_p5_packagings,apply_p1_rewrite,apply_p2_gating,step_substrate,
)


ROOT=Path(__file__).resolve().parents[1]
LENSES=('spectral_lens','row_similarity_cluster_lens','audit_flow_quantile_lens')
PACKS=('partition_cluster_packaging','return_core_packaging','budget_audit_packaging')


def state_at(kernel,phase,tau,budget):
    params=PilotParameters(**json.loads((ROOT/'configs/experiments/generated/continuous_full_loop_kernel_shell.json')
        .read_text())['parameters']['pilot_parameters'])
    prev=((phase-1)%12)//4
    protocol='refresh' if phase<3 else 'audit' if phase<6 else 'packaging' if phase<9 else 'settle'
    return KernelSubstrateState([[float(v) for v in row] for row in kernel.full()],
        float(tau),float(budget),0.,phase,protocol,LENSES[prev],PACKS[prev],[1.]*6,
        pilot_parameters=params,lens_history=[LENSES[prev]],packaging_history=[PACKS[prev]])


class Noise:
    def __init__(self,values):self.values=iter(values)
    def random(self):return .5
    def uniform(self,a,b):
        v=next(self.values)
        assert a<=v<=b
        return v


class UnitNoise(Noise):
    def uniform(self,a,b):
        z=next(self.values)
        assert -1<=z<=1
        return (a+b)/2+(b-a)*z/2


@pytest.fixture(scope='module')
def cycle():return load_cycle()


@pytest.mark.parametrize('x',[Q(1,20),Q(1),Q(3,2),Q(2),Q(20),Q(7,3)])
def test_rational_transcendental_enclosures(x):
    sq=I(x).sqrt()
    assert sq.lo**2<=x<=sq.hi**2
    lg=I(x).log()
    with mp.workdps(80):
        value=mp.log(mp.mpf(x.numerator)/x.denominator)
        assert mp.mpf(lg.lo.numerator)/lg.lo.denominator<=value<=mp.mpf(lg.hi.numerator)/lg.hi.denominator
        ex=I(x).exp()
        value=mp.exp(mp.mpf(x.numerator)/x.denominator)
        assert mp.mpf(ex.lo.numerator)/ex.lo.denominator<=value<=mp.mpf(ex.hi.numerator)/ex.hi.denominator
        neg=I(-x).exp()
        value=mp.exp(-mp.mpf(x.numerator)/x.denominator)
        assert mp.mpf(neg.lo.numerator)/neg.lo.denominator<=value<=mp.mpf(neg.hi.numerator)/neg.hi.denominator


def test_interval_illegal_operations_rejected():
    with pytest.raises(ValueError):I(1)/I(-1,1)
    with pytest.raises(ValueError):I(-1,0).sqrt()
    with pytest.raises(ValueError):I(0,1).log()


def test_class_informant_matches_exact_full_iteration(cycle):
    for kernel in cycle:
        full=kernel.full()
        assert len(full)==20 and all(sum(row)==1 for row in full)
        pi,n=kernel.finite_informant()
        p=(Q(1,20),)*20
        for step in range(80):
            nxt=tuple(sum(p[i]*full[i][j] for i in range(20)) for j in range(20))
            assert sum(nxt)==1
            if max(abs(nxt[i]-p[i]) for i in range(20))<=Q(1,10**12):break
            p=nxt
        assert step+1==n
        assert nxt==(pi[0],)*5+(pi[1],)*5+(pi[2],)*10


def test_reduced_formulas_against_unmodified_source(cycle):
    for phase,kernel in enumerate(cycle):
        for b in (Q(3),Q(7),Q(12)):
            tb=tau_box(phase); tau=(tb.lo+tb.hi)/2
            e=evaluate_phase(kernel,phase,I(tau),I(b),informants(kernel))
            state=state_at(kernel,phase,tau,b)
            inf=refresh_informants(state,state.primitive_activity)
            lens=max(compute_p4_lenses(state,inf),key=lambda c:c['score'])
            package=max(compute_p5_packagings(state,inf,lens),key=lambda c:c['score'])
            assert lens['name']==LENSES[phase//4]
            assert package['name']==PACKS[phase//4]
            assert lens['score']==pytest.approx(float(e['lens'].lo),abs=1e-12)
            assert package['score']==pytest.approx(float(e['package'].lo),abs=1e-12)
            p1,_=apply_p1_rewrite(state,package,lens)
            pre,_=apply_p2_gating(state,p1,package,lens,inf)
            labels=(0,)*5+(1,)*5+(2,)*10
            for i,a in enumerate(labels):
                for j,c in enumerate(labels):
                    expected=e['base'][a][c]+e['excess'][a]*int(i==j)
                    assert pre[i][j]==pytest.approx(float(expected.lo),abs=1e-12)


def test_all_time_cycle_and_entry_interval_certificates():
    cert=certify_cycle(); entry=certify_entry_prefix()
    assert all(Q(p['noise_cap'])<Q(1,1000) for p in cert['phases']+entry['phases'])
    assert all(Q(p['income_floor'])>0 for p in cert['phases']+entry['phases'])
    assert Q(cert['recurring_entry_jump_floor'])>Q(1,50)
    assert cert['uncontrolled_noise_invariance'] is False
    assert cert['main_theorem_package_complete'] is False
    assert entry['length']==24


def test_fixed_half_target_and_initial_observable_identity():
    witness=construct_original_loop_extension()
    prefix=construct_entry_prefix()
    for c in (Q(79,100),Q(4,5)):
        join=exact_fixed_half_join(witness,c)
        assert join.maximum_noise<Q(6,10000)<Q(1,400)
        assert join.common_kernel==prefix[0][1].full()
        assert sum((join.common_kernel[i][j]-witness.kernels[0][i][j])**2 for i in range(20) for j in range(20)) \
            ==join.final_variation_squared
        assert join.common_kernel[0]==join.common_kernel[1]==join.common_kernel[2]


def test_six_knockouts_change_physical_outputs_with_same_noise(cycle):
    certificate=certify_six_role_dependence(cycle)
    assert all(Q(v)>0 for v in certificate['positive_scalar_gaps'].values())
    base=state_at(cycle[0],0,Q(3,5),3)
    inf=refresh_informants(base,base.primitive_activity)
    lens=max(compute_p4_lenses(base,inf),key=lambda c:c['score'])
    pack=max(compute_p5_packagings(base,inf,lens),key=lambda c:c['score'])
    p1,_=apply_p1_rewrite(base,pack,lens)
    pre,_=apply_p2_gating(base,p1,pack,lens,inf)
    target=cycle[1].full()
    innovations=[float(target[i][j])-pre[i][j] for i in range(20) for j in range(20)]
    step_substrate(base,Noise(innovations))
    sigma=.0025+.002*min(1,base.budget/6)
    standardized=[v/sigma for v in innovations]
    for role in ('P1','P2','P3','P4','P5','P6'):
        state=state_at(cycle[0],0,Q(3,5),3)
        step_substrate(state,UnitNoise(standardized),{role:False})
        if role=='P3':
            assert state.phase==0 and base.phase==1
            assert state.budget-base.budget==pytest.approx(float(Q(216,12500)),abs=1e-12)
        elif role=='P6':assert state.budget==3 and base.budget>3.18
        else:assert max(abs(state.kernel[i][j]-base.kernel[i][j]) for i in range(20) for j in range(20))>1e-5


def test_original_potential_periodic_pressure_separation(cycle):
    from contextual_cantor.controlled_pressure_separation import certify_pressure_separation
    cert=certify_pressure_separation(cycle)
    assert Q(cert['equal_weight_two_world_gap_floor'])>Q(1,2000)
    assert cert['paper_packaged_fiber_law_identified'] is False
    assert cert['within_same_full_scalar_history_base'] is False
    assert cert['main_theorem_package_complete'] is False
    # Independently replay each twelve-phase periodic regime through the
    # original implementation. Float comparison checks the semantic bridge;
    # the rational certificate supplies mathematical separation.
    from contextual_cantor.controlled_pressure_separation import mix_cycle
    from scripts.run_continuous_pressure_closure_checks import _observable
    from scripts.run_continuous_pressure_checks import _observable_value,_series_for_step
    for index,orbit in enumerate((cycle,mix_cycle(cycle,Q(1,100)))):
        state=state_at(orbit[0],0,Q(3,5),12)
        values=[]
        for step in range(36):
            phase=state.phase
            inf=refresh_informants(state,state.primitive_activity)
            lens=max(compute_p4_lenses(state,inf),key=lambda c:c['score'])
            pack=max(compute_p5_packagings(state,inf,lens),key=lambda c:c['score'])
            p1,_=apply_p1_rewrite(state,pack,lens)
            pre,_=apply_p2_gating(state,p1,pack,lens,inf)
            target=orbit[(phase+1)%12].full()
            innovations=[float(target[i][j])-pre[i][j] for i in range(20) for j in range(20)]
            record=step_substrate(state,Noise(innovations))
            if step>=24:values.append((_observable(record),_observable_value(_series_for_step(record))))
        for j,key in enumerate(('closure_pressure_at_one','operator_pressure_at_one')):
            assert -sum(v[j] for v in values)/12==pytest.approx(
                float(Q(cert['pressure_intervals'][index][key][0])),abs=1e-12)


def test_certificate_rejects_degenerate_or_unstable_carriers(cycle):
    with pytest.raises(ValueError):certify_cycle(())
    with pytest.raises(ValueError):certify_cycle(cycle,radius=Q(0))
    with pytest.raises(ValueError):certify_cycle(cycle,radius=Q(1,10**12))
    from contextual_cantor.controlled_shell import ClassKernel
    bad=ClassKernel(((Q(1),)*3,)*3,(Q(0),)*3)
    with pytest.raises(ValueError):certify_cycle((bad,)*12)
