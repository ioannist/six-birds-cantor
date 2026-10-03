from fractions import Fraction as Q
import json
from pathlib import Path

import mpmath as mp
import pytest

from contextual_cantor.all_word_pressure_disintegration import (
    certify_all_word_pressure_disintegration,RADIUS,
)
from contextual_cantor.packaged_world_disintegration import construct_packaged_world_law
from contextual_cantor.original_loop_extension import construct_original_loop_extension
from contextual_cantor.controlled_shell import load_cycle
from contextual_cantor.controlled_pressure_separation import mix_cycle
from contextual_cantor.continuous_kernel_substrate import (
    KernelSubstrateState,PilotParameters,refresh_informants,compute_p4_lenses,
    compute_p5_packagings,apply_p1_rewrite,apply_p2_gating,step_substrate,
)
from scripts.run_continuous_pressure_closure_checks import _observable
from scripts.run_continuous_pressure_checks import _observable_value,_series_for_step


ROOT=Path(__file__).resolve().parents[1]


@pytest.fixture(scope='module')
def certificate():
    return certify_all_word_pressure_disintegration(False)


def test_exact_same_lens_objects_and_finite_disintegration():
    w=construct_original_loop_extension()
    values=(Q(5,7),Q(13,17))
    law=construct_packaged_world_law()
    assert law.objects==tuple(a.stationary for a in w.audit)
    assert len(set(law.objects))==2
    assert law.weights==(Q(1,2),)*2
    assert sum(law.mass(obj)*law.conditional(values,obj) for obj in law.objects)==law.expectation(values)
    # Another candidate lens is not another fiber of this retained active lens.
    with pytest.raises(ValueError):law.mass(w.spectral.stationary)


def test_uniform_gap_for_actual_current_objects_and_no_scope_smuggling(certificate):
    assert certificate['periodic_only_restriction'] is False
    assert certificate['reference_pressure_equals_global_shell_supremum_analytic'] is True
    assert certificate['reference_law_numerically_instantiated'] is False
    assert certificate['reference_law_depends_on_evaluation_parameter'] is False
    assert certificate['original_independent_noise_law'] is False
    assert certificate['initial_completion_object_preserved_by_outer_F'] is False
    assert certificate['shared_full_pointwise_future_history_base'] is False
    assert certificate['main_theorem_package_complete'] is False
    assert certificate['descriptor_fibers_are_actual_same_lens_completion_objects'] is True
    assert certificate['fixed_active_completion_lens']=='audit_flow_quantile_lens'
    assert certificate['paper_current_three_lens_family_identified'] is False
    assert certificate['original_empirical_frequency_weights_established'] is False
    assert certificate['all_original_audited_descriptors_established'] is False
    assert certificate['exhausts_packaged_outputs_over_original_descriptor'] is False
    assert certificate['original_sixteen_state_witness_established'] is False
    assert certificate['reference_law_has_full_support_on_each_return_input_family'] is True
    assert Q(certificate['positive_grid_neighborhood_gap_floor'])>Q(1,25000)
    for row in certificate['uniform_all_word_pressure_profiles']:
        if Q(row['parameter'])==0:
            assert tuple(map(Q,row['global_equal_weight_gap_interval']))==(Q(0),Q(0))
        else:
            assert Q(row['global_equal_weight_gap_interval'][0])>0
            assert all(c['start_phase']==1 for c in row['all_block_collatz_certificates'])


@pytest.mark.parametrize('s',[Q(1,2),Q(1),Q(3,2)])
@pytest.mark.parametrize('observable',['closure','operator'])
def test_independent_full_twenty_state_nonconstant_block_bounds(certificate,s,observable):
    nominal=(load_cycle(),mix_cycle(load_cycle(),Q(1,100)))
    row=next(p for p in certificate['uniform_all_word_pressure_profiles']
             if Q(p['parameter'])==s and p['observable']==observable)
    with mp.workdps(80):
        def exact(x):
            x=Q(x)
            return mp.mpf(x.numerator)/x.denominator
        for z,cycle in enumerate(nominal):
            proof=row['all_block_collatz_certificates'][z]
            vector=[exact(proof['test_vector'][0 if i<5 else 1 if i<10 else 2]) for i in range(20)]
            image=vector[:]
            # Alternate Cantor endpoints: the twelve matrices do NOT have
            # one common mixing parameter. Choose q inside its certified box;
            # the bound holds even for these independent over-enclosed choices.
            phases=(*range(1,12),0)
            for position,phase in reversed(tuple(enumerate(phases))):
                kernel=mix_cycle(cycle,RADIUS if position%2 else Q(0))[phase].full()
                lo,hi=map(Q,certificate['uniform_q_enclosures'][z][phase][observable+'_q'])
                q=lo if position%3 else hi
                image=[sum(mp.exp(exact(s)*(mp.log(exact(kernel[i][j]))-exact(q)))*image[j]
                           for j in range(20)) for i in range(20)]
            ratios=[a/b for a,b in zip(image,vector)]
            lower,upper=map(exact,proof['eigenvalue_interval'])
            assert lower<=min(ratios)<=max(ratios)<=upper


class Noise:
    def __init__(self,values):self.values=iter(values)
    def random(self):return .5
    def uniform(self,a,b):
        x=next(self.values)
        assert a<=x<=b
        return x


def test_actual_original_source_observables_on_aperiodic_input_word(certificate):
    params=PilotParameters(**json.loads((ROOT/'configs/experiments/generated/continuous_full_loop_kernel_shell.json')
        .read_text())['parameters']['pilot_parameters'])
    nominal=(load_cycle(),mix_cycle(load_cycle(),Q(1,100)))
    # Nonconstant Cantor endpoint coordinates; each is in C_r exactly.
    lambdas=tuple(RADIUS if (i*i+3*i+1)%7<3 else Q(0) for i in range(37))
    for z,cycle in enumerate(nominal):
        first=mix_cycle(cycle,lambdas[0])[1].full()
        state=KernelSubstrateState([[float(x) for x in row] for row in first],.6,12.,0.,1,
            'refresh','spectral_lens','partition_cluster_packaging',[1.]*6,
            pilot_parameters=params,lens_history=['spectral_lens'],
            packaging_history=['partition_cluster_packaging'])
        for step in range(36):
            phase=state.phase
            info=refresh_informants(state,state.primitive_activity)
            lens=max(compute_p4_lenses(state,info),key=lambda x:x['score'])
            package=max(compute_p5_packagings(state,info,lens),key=lambda x:x['score'])
            p1,_=apply_p1_rewrite(state,package,lens)
            pre,_=apply_p2_gating(state,p1,package,lens,info)
            target=mix_cycle(cycle,lambdas[step+1])[(phase+1)%12].full()
            record=step_substrate(state,Noise([float(target[i][j])-pre[i][j] for i in range(20) for j in range(20)]))
            for observable,value in (('closure',_observable(record)),('operator',_observable_value(_series_for_step(record)))):
                lo,hi=map(Q,certificate['uniform_q_enclosures'][z][phase][observable+'_q'])
                # Numerical source-semantic return, separate from exact
                # interval proof. This permits ordinary floating roundoff.
                assert float(lo)-1e-12<=value<=float(hi)+1e-12
