import json
from fractions import Fraction as Q
from pathlib import Path
import random

import pytest

from contextual_cantor.original_loop_extension import (
    construct_original_loop_extension, exact_pre_noise, integer_moving_history_rows,
)
from contextual_cantor.continuous_kernel_substrate import (
    KernelSubstrateState, PilotParameters, refresh_informants, compute_p4_lenses,
    compute_p5_packagings, apply_p1_rewrite, apply_p2_gating, step_substrate,
)
from scripts.run_continuous_pressure_closure_checks import _observable
from scripts.run_continuous_pressure_checks import _observable_value, _series_for_step


@pytest.fixture(scope="module")
def witness():
    return construct_original_loop_extension()


def test_exact_original_dimension_completion_split_and_forcing(witness):
    assert witness.audit_groups[0] == (0,4,5,6,7)
    assert witness.audit[0].reinstatement == witness.audit[1].reinstatement
    assert witness.audit[0].stationary[0]-witness.audit[1].stationary[0] == \
        Q(390467997745347846870000,120131948909489644812213124707327077)
    assert len({witness.audit[0].stationary,witness.audit[1].stationary,
                witness.spectral.stationary,witness.cluster.stationary}) == 4
    assert {witness.audit[0].stationary,witness.spectral.stationary,witness.cluster.stationary} != \
        {witness.audit[1].stationary,witness.spectral.stationary,witness.cluster.stationary}
    assert witness.audit[0].lumpability_defect == Q(101,3906250)
    assert all(a.minorization > 0 for a in witness.audit)


def test_affine_endpoint_noise_and_budget_bounds(witness):
    for c in (Q(79,100),Q(4,5)):
        outputs=exact_pre_noise(witness,c)
        assert max(abs(x-Q(1,20)) for m in outputs for row in m for x in row) < Q(39,10000)
        assert all(sum(row)==1 for m in outputs for row in m)
    # These bound the REAL irrational package score and Frobenius variation.
    income_floor=Q(108,100)*(Q(24,100)*Q(79,100)+Q(12,100)*Q(37,80)+Q(8,100)*Q(92,100))
    cost_cap=Q(96,100)*(Q(6,100)+Q(18,1000)+Q(4,100)*Q(8,100))+Q(6,100)
    assert income_floor > cost_cap
    assert Q(3,5)+Q(11,100)*Q(12,100)-Q(12,100) < Q(3,5)


def test_full_moving_history_readouts_after_rank_one_join(witness):
    tail=tuple(tuple(Q(3,4)*int(i==j)+Q(1,80) for j in range(20)) for i in range(20))
    for s in (0,1,2,3):
        for suffix in ((),(witness.shared_next_kernel,),
                       (witness.shared_next_kernel,tail),
                       (witness.shared_next_kernel,tail,witness.kernels[0])):
            scales=(Q(2,3),)*(1+len(suffix))
            left=integer_moving_history_rows((witness.kernels[0],*suffix),s,scales)
            right=integer_moving_history_rows((witness.kernels[1],*suffix),s,scales)
            assert left==right


class _PrescribedNoise:
    """One legal source random-input word, not a seeded PRNG reachability claim."""
    def __init__(self, noise):
        self.noise=iter(noise)
        self.count=0

    def random(self):
        return 0.5

    def uniform(self,lower,upper):
        value=next(self.noise)
        assert lower <= value <= upper
        self.count+=1
        return value


def test_unmodified_source_original_parameter_noise_join(witness):
    root=Path(__file__).resolve().parents[1]
    config=json.loads((root/'configs/experiments/generated/continuous_full_loop_kernel_shell.json').read_text())
    params=PilotParameters(**config['parameters']['pilot_parameters'])
    assert params.kernel_minorization==0
    states=[]
    steps=[]
    for k in witness.kernels:
        state=KernelSubstrateState([[float(x) for x in row] for row in k],0.6,12.0,0.0,0,
            'refresh','audit_flow_quantile_lens','budget_audit_packaging',[1.0]*6,
            pilot_parameters=params,lens_history=['audit_flow_quantile_lens'],
            packaging_history=['budget_audit_packaging'])
        informants=refresh_informants(state,state.primitive_activity)
        lens=max(compute_p4_lenses(state,informants),key=lambda x:x['score'])
        package=max(compute_p5_packagings(state,informants,lens),key=lambda x:x['score'])
        p1,_=apply_p1_rewrite(state,package,lens)
        pre,_=apply_p2_gating(state,p1,package,lens,informants)
        rng=_PrescribedNoise([0.05-x for row in pre for x in row])
        step=step_substrate(state,rng)
        assert rng.count==400
        assert step['selector_diagnostics']['lens_margin']>0.03
        assert step['selector_diagnostics']['packaging_margin']>0.03
        assert state.tau==0.6 and state.budget==12.0 and state.phase==1
        assert step['packaging']['core_indices']==list(range(20))
        assert step['p1']['eta']==pytest.approx(float(Q(92,1000))+0.05*step['packaging']['score'])
        states.append(state)
        steps.append(step)
    assert states[0].kernel==states[1].kernel
    assert states[0].action_weights==pytest.approx(states[1].action_weights,abs=1e-15)
    assert _observable(steps[0])==pytest.approx(_observable(steps[1]),abs=1e-15)
    assert _observable_value(_series_for_step(steps[0]))==pytest.approx(
        _observable_value(_series_for_step(steps[1])),abs=1e-15)
    # Auxiliary old-kernel bookkeeping is not treated as physical coalescence.
    assert states[0].previous_kernel != states[1].previous_kernel
    future=[step_substrate(state,random.Random(1701)) for state in states]
    assert states[0].kernel==states[1].kernel
    assert states[0].previous_kernel==states[1].previous_kernel
    assert _observable(future[0])==pytest.approx(_observable(future[1]),abs=1e-15)


@pytest.mark.parametrize('score',[0.795,Q(0),Q(1),True])
def test_noise_certificate_rejects_inexact_or_out_of_branch_input(witness,score):
    with pytest.raises(ValueError):
        exact_pre_noise(witness,score)
