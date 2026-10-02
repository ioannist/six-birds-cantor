import json
import math
from pathlib import Path
import random

import pytest

from contextual_cantor.continuous_kernel_substrate import (
    KernelSubstrateState,PilotParameters,step_substrate,refresh_informants,
    compute_p4_lenses,compute_p5_packagings,
)
from contextual_cantor.cocycle_pressure import KernelHistoryStep,history_log_norm
from scripts.run_continuous_pressure_checks import _observable_value,_series_for_step
from scripts.run_continuous_pressure_closure_checks import _observable


@pytest.mark.parametrize('config', ['continuous_full_loop_kernel.json','continuous_full_loop_kernel_shell.json'])
@pytest.mark.parametrize('kind',['uniform','identity','cycle','dense'])
def test_original_selector_observable_bounds_on_boundary_kernels(config,kind):
    root=Path(__file__).resolve().parents[1]
    cfg=json.loads((root/'configs/experiments/generated'/config).read_text())['parameters']
    params=PilotParameters(**cfg['pilot_parameters'])
    d=cfg['kernel_dim']
    generator=random.Random(203)
    if kind=='uniform':
        kernel=[[1/d]*d for _ in range(d)]
    elif kind=='identity':
        kernel=[[float(i==j) for j in range(d)] for i in range(d)]
    elif kind=='cycle':
        kernel=[[float((i+1)%d==j) for j in range(d)] for i in range(d)]
    else:
        kernel=[[generator.random() for _ in range(d)] for _ in range(d)]
        kernel=[[v/sum(row) for v in row] for row in kernel]
    for phase in range(12):
        for budget in (0.0,12.0):
            for tau in (0.6,4.0):
                state=KernelSubstrateState([row[:] for row in kernel],tau,budget,0.0,phase,'refresh',
                    'audit_flow_quantile_lens','budget_audit_packaging',[1]*6,pilot_parameters=params)
                step=step_substrate(state,random.Random(321))
                assert step['lens']['score'] >= 0.39-1e-14
                assert step['lens']['score'] <= 1.25+1e-14
                assert step['packaging']['score'] >= 0.412-1e-14
                for q in (_observable(step),_observable_value(_series_for_step(step))):
                    assert math.log(1.25)<=q<=math.log(10)
                    assert max(0.05,min(10.0,q))==q


def test_sparse_moving_history_bounds_convexity_and_parameter_decrease():
    permutation=[[0.,1.,0.],[0.,0.,1.],[1.,0.,0.]]
    partial=[[0.5,0.5,0.],[0.,1.,0.],[0.5,0.,0.5]]
    rank_one=[[0.,0.25,0.75]]*3
    steps=[KernelHistoryStep(k,q) for k,q in
           ((permutation,0.4),(partial,0.7),(rank_one,0.3))]*4
    n=len(steps)
    qsum=sum(step.observable for step in steps)
    for s in (0.,0.5,1.,3.):
        z=history_log_norm(steps,s)
        assert -s*qsum-s*n*math.log(3)-1e-12<=z<=n*math.log(3)-s*qsum+1e-12
        for t in (s+0.3,s+1.7):
            assert history_log_norm(steps,t)-z<=-(t-s)*qsum+1e-12
    theta,s,t=0.4,0.0,2.7
    assert history_log_norm(steps,theta*s+(1-theta)*t)<= \
        theta*history_log_norm(steps,s)+(1-theta)*history_log_norm(steps,t)+1e-12
    assert history_log_norm(steps,1)==pytest.approx(-qsum,abs=1e-12)


def test_absent_edges_are_not_reintroduced_at_parameter_zero():
    k=[[0.,1.],[1.,0.]]
    steps=[KernelHistoryStep(k,0.5)]*20
    assert history_log_norm(steps,0)==0.0
    assert history_log_norm(steps,0.5)==pytest.approx(-5)


class _AdversarialCoreNoise:
    def __init__(self,d,core):
        self.d,self.core,self.index=d,set(core),0

    def random(self):
        return 0.5

    def uniform(self,lower,upper):
        j=self.index%self.d
        self.index+=1
        return lower if j in self.core else upper


@pytest.mark.parametrize('config',['continuous_full_loop_kernel.json','continuous_full_loop_kernel_shell.json'])
def test_original_phase_eight_forces_budget_and_survives_adversarial_noise(config):
    root=Path(__file__).resolve().parents[1]
    cfg=json.loads((root/'configs/experiments/generated'/config).read_text())['parameters']
    d=cfg['kernel_dim']
    params=PilotParameters(**cfg['pilot_parameters'])
    kernels=[[[float(i==j) for j in range(d)] for i in range(d)],
             [[float(j==0) for j in range(d)] for _ in range(d)],
             [[1/d]*d for _ in range(d)]]
    for k in kernels:
        for budget in (0.0,12.0):
            for tau in (0.6,4.0):
                state=KernelSubstrateState([row[:] for row in k],tau,budget,0.0,8,'refresh',
                    'spectral_lens','return_core_packaging',[1]*6,pilot_parameters=params)
                inf=refresh_informants(state,state.primitive_activity)
                lenses=compute_p4_lenses(state,inf)
                # Actual P4 may retain/draw a near-best challenger. Every
                # phase-8 candidate still has the .75 cap used in the proof.
                assert max(l['score'] for l in lenses)<=0.75+1e-14
                lens=max(lenses,key=lambda x:x['score'])
                budget_pack=next(p for p in compute_p5_packagings(state,inf,lens)
                                 if p['name']=='budget_audit_packaging')
                rng=_AdversarialCoreNoise(d,budget_pack['core_indices'])
                step=step_substrate(state,rng)
                assert step['packaging']['name']=='budget_audit_packaging'
                assert step['packaging']['score']>=0.665-1e-14
                core=step['packaging']['core_indices']
                assert len(core)>=4 and rng.index==d*d
                assert min(row[j] for row in state.kernel for j in core)>1/10000
