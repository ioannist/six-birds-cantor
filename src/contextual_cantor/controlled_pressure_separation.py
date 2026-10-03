"""Same-potential pressure separation between lawful controlled continuations.

This constructs a missing thermodynamic ingredient, not the paper's undefined
disintegration law. A two-world law has a genuine positive gap ONLY IF its
fibers are these two continuations. Their full history profiles differ; they
cannot belong to one fiber of a base that retains those profiles.
"""
from fractions import Fraction as Q

from .rational_interval import Interval as I,as_interval,maximum
from .controlled_shell import (
    ClassKernel,load_cycle,informants,evaluate_phase,noise_bound,thick_kernel,thick_informants,
)


def mix_cycle(cycle,parameter):
    if not isinstance(parameter,(int,Q)) or isinstance(parameter,bool) or not 0<=parameter<1:
        raise ValueError('exact mixing parameter in [0,1) required')
    return tuple(ClassKernel(tuple(tuple(m+parameter*(Q(n,20)-m)
                         for m,n in zip(row,(5,5,10))) for row in k.mass),
                         tuple(t*(1-parameter) for t in k.excess)) for k in cycle)


def timescale_after(phase,tau,variation):
    penalty=Q(3,25) if phase%4==0 else 0
    return (tau+Q(11,100)*maximum(0,Q(3,25)-variation)-Q(3,50)*variation-penalty).clamp(Q(3,5),4)


def _final_variation(kernel,target):
    old=kernel.base(); new=target.base()
    square=sum((5,5,10)[a]*(5,5,10)[b]*(as_interval(new[a][b]-old[a][b])).square()
               for a in range(3) for b in range(3) if a!=b)
    square=square+sum((5,5,10)[a]*((5,5,10)[a]-1)*as_interval(new[a][a]-old[a][a]).square()
        +(5,5,10)[a]*as_interval(new[a][a]+target.excess[a]-old[a][a]-kernel.excess[a]).square() for a in range(3))
    return square.sqrt()


def periodic_observable_pressure(cycle):
    """Exact interval evaluation after all four-phase timescale resets.

    b=12 remains capped because income exceeds cost. At s=1 the actual
    stochastic-history norm is exp(-sum q), hence pressure is -mean q over
    the twelve-cycle. Both ORIGINAL source q definitions are kept separate.
    """
    if len(cycle)!=12:
        raise ValueError('a twelve-phase orbit is required')
    for kernel in cycle:
        kernel.check_exact()
    infos=[informants(k) for k in cycle]
    return _periodic_observables(cycle,infos)


def periodic_observable_box(cycle,radius):
    """Uniform original-q enclosure for arbitrary input words in [0,radius].

    Each current and next K_k(lambda) has an independent parameter. Exact
    resets bound the intervening tau history, so the same phase boxes enclose
    every return block. Stochasticity follows from the kernel constructor,
    not interval endpoint row sums. Fixed finite-informant stopping and
    strict selector guards give continuity of the actual q family.
    """
    if len(cycle)!=12 or not isinstance(radius,(Q,int)) or isinstance(radius,bool) or not 0<radius<1:
        raise ValueError('twelve exact kernels and a positive exact radius are required')
    for kernel in cycle:
        kernel.check_exact()
    boxes=tuple(thick_kernel(k,radius) for k in cycle)
    infos=[thick_informants(k) for k in boxes]
    if any(len(info.stopping_steps)!=1 for info in infos):
        raise ValueError('continuous input family requires stable informant stopping')
    return _periodic_observables(boxes,infos)


def _periodic_observables(cycle,infos):
    tau=I(Q(3,5))
    # Phase 8 resets tau, so the pre-phase-9 value is exactly .6. Build
    # pre-phase-0 from the audit window, rather than assuming tau is constant.
    for phase in (9,10,11):
        e=evaluate_phase(cycle[phase],phase,tau,I(12),infos[phase])
        tau=timescale_after(phase,tau,e['variation'])
    rows=[]; q_closure=[]; q_operator=[]
    initial_tau=tau
    for phase,kernel in enumerate(cycle):
        e=evaluate_phase(kernel,phase,tau,I(12),infos[phase])
        if e['income_minus_cost'].lo<=0 or noise_bound(e,cycle[(phase+1)%12]).hi>=Q(1,1000):
            raise ValueError('periodic continuation is not certified lawful')
        if e['lens_margin'].lo<=Q(3,100) or e['packaging_margin'].lo<=Q(3,100):
            raise ValueError('periodic selector branch lacks a strict uniform guard')
        next_tau=timescale_after(phase,tau,e['variation'])
        if phase%4==0 and (next_tau.lo!=Q(3,5) or next_tau.hi!=Q(3,5)):
            raise ValueError('joint selector switch did not reset the timescale')
        # Original lens temperature clamps to .08 at b=12 and tau<.64.
        if tau.hi>=Q(16,25):
            raise ValueError('action temperature clamp not certified')
        scores=(e['p1_target_distance'],e['viability_mean'],next_tau,e['lens'],e['package'],e['income'])
        scaled=[s/Q(19,40) for s in scores]
        weights=[s.exp() for s in scaled]
        total=sum(weights)
        # H(softmax(scores/temp)) = log(sum exp) - sum(p*score/temp).
        entropy=total.log()-sum(w*s/total for w,s in zip(weights,scaled))
        final_variation=_final_variation(kernel,cycle[(phase+1)%12])
        closure=(1+final_variation+Q(25,100)*e['lens']+Q(30,100)*e['package']
                 +Q(5,100)+Q(5,100)*next_tau+Q(5,100)*entropy).log()
        operator=(1+final_variation+Q(28,100)*e['lens']+Q(32,100)*e['package']
                  +Q(10,100)+Q(8,100)*next_tau+Q(5,100)*entropy).log()
        q_closure.append(closure);q_operator.append(operator)
        rows.append({'phase':phase,'pre_tau':[str(tau.lo),str(tau.hi)],
            'post_tau':[str(next_tau.lo),str(next_tau.hi)],
            'closure_q':[str(closure.lo),str(closure.hi)],
            'operator_q':[str(operator.lo),str(operator.hi)],
            'noise_cap':str(noise_bound(e,cycle[(phase+1)%12]).hi)})
        tau=next_tau
    # The fixed reset makes the repeated interval expression close. For boxes
    # this is an enclosure of all words, not equality of their actual tau values.
    if tau!=initial_tau:
        raise ValueError('timescale period failed to close')
    return {'phase_observables':rows,
            'closure_pressure_at_one':-sum(q_closure)/12,
            'operator_pressure_at_one':-sum(q_operator)/12}


def certify_pressure_separation(cycle=None):
    cycle=load_cycle() if cycle is None else cycle
    other=mix_cycle(cycle,Q(1,100))
    p0=periodic_observable_pressure(cycle)
    p1=periodic_observable_pressure(other)
    gaps={name:p1[name]-p0[name] for name in ('closure_pressure_at_one','operator_pressure_at_one')}
    if min(g.lo for g in gaps.values())<=Q(1,1000):
        raise ValueError('original-potential pressure separation was not certified')
    return {'scope':'two legal controlled periodic continuations; actual original potentials at s=1',
        'continuation_mixing_parameters':['0','1/100'],
        'pressure_intervals':[{key:[str(value.lo),str(value.hi)] for key,value in p.items()
                               if key.endswith('_at_one')} for p in (p0,p1)],
        'pressure_difference_intervals':{key:[str(v.lo),str(v.hi)] for key,v in gaps.items()},
        'equal_weight_two_world_gap_floor':str(min(g.lo for g in gaps.values())/2),
        'conditional_statement':'a fixed positive two-world disintegration over THESE continuations has a positive weighted gap',
        'paper_packaged_fiber_law_identified':False,
        'within_same_full_scalar_history_base':False,
        'main_theorem_package_complete':False,
        'phase_observables':[p0['phase_observables'],p1['phase_observables']]}
