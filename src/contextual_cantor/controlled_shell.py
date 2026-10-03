"""Validated controlled-shell construction for the unmodified 20-state loop.

This concerns legal real-valued innovation words, not seeded PRNG trajectories
or positive-probability events for independent noise. The three-class formulas
are the exact restriction of the source to exchangeable kernels with class
sizes (5,5,10). The stationary INFORMANT is the source's finite iteration,
including its stopping test; it is not replaced by an invariant distribution.
"""
from dataclasses import dataclass
from fractions import Fraction as Q
import json
from pathlib import Path

from .rational_interval import Interval as I, as_interval, maximum, minimum

SIZES=(5,5,10)


@dataclass(frozen=True)
class ClassKernel:
    mass: tuple[tuple[Q,...],...]
    excess: tuple[Q,...]

    def check_exact(self):
        if len(self.mass)!=3 or any(len(row)!=3 for row in self.mass) or len(self.excess)!=3:
            raise ValueError('three-class kernel dimensions are wrong')
        if any(not isinstance(v,(Q,int)) or isinstance(v,bool)
               for v in (*self.excess,*(v for row in self.mass for v in row))):
            raise ValueError('nominal kernel must have exact rational entries')
        if any(sum(row)!=1 for row in self.mass) or min(v for row in self.full() for v in row)<=0:
            raise ValueError('nominal kernel must be positive and stochastic')

    @classmethod
    def from_record(cls,record):
        off=record['off_diagonal_group_mass']
        mass=tuple(tuple(1-sum(Q(off[a][b]) for b in range(3) if b!=a)
                         if a==b else Q(off[a][b]) for b in range(3)) for a in range(3))
        result=cls(mass,tuple(Q(v) for v in record['diagonal_excess']))
        result.check_exact()
        return result

    def base(self):
        return tuple(tuple((self.mass[a][b]-self.excess[a]*int(a==b))/SIZES[b]
                           for b in range(3)) for a in range(3))

    def full(self):
        labels=(0,)*5+(1,)*5+(2,)*10
        c=self.base()
        return tuple(tuple(c[a][b]+self.excess[a]*int(i==j)
                           for j,b in enumerate(labels)) for i,a in enumerate(labels))

    def finite_informant(self):
        p=tuple(Q(n,20) for n in SIZES)
        for step in range(80):
            nxt=tuple(sum(p[a]*self.mass[a][b] for a in range(3)) for b in range(3))
            # Normalization is exactly the identity for a stochastic kernel.
            if sum(nxt)!=1:
                raise ArithmeticError('informant normalization failed')
            if max(abs(nxt[a]-p[a])/SIZES[a] for a in range(3))<=Q(1,10**12):
                return tuple(nxt[a]/SIZES[a] for a in range(3)),step+1
            p=nxt
        return tuple(p[a]/SIZES[a] for a in range(3)),80


def load_cycle(path=None):
    path=path or Path(__file__).resolve().parents[2]/'configs/mathematics/original_controlled_cycle.json'
    data=json.loads(Path(path).read_text())
    if tuple(data['class_sizes'])!=SIZES or [r['phase'] for r in data['phases']]!=list(range(12)):
        raise ValueError('wrong class sizes or phase ordering')
    return tuple(ClassKernel.from_record(r) for r in data['phases'])


def tau_box(phase):
    # Each joint selector switch resets tau to .6; between switches each
    # source P3 update can increase it by at most .11*.12=.0132.
    age=(phase-1)%4
    return I(Q(3,5),Q(3,5)+Q(33,2500)*age)


def _sin_twelve(phase):
    h=I(Q(1,2)); r=I(3).sqrt()/2
    return (I(0),h,r,I(1),r,h,I(0),-h,-r,I(-1),-r,-h)[phase%12]


def _sin_similarity(phase):
    a=I(2).sqrt()/2
    b=(I(6).sqrt()+I(2).sqrt())/4
    c=(I(6).sqrt()-I(2).sqrt())/4
    return (a,b,c,-a,-b,-c)[phase%6]


@dataclass(frozen=True)
class Informants:
    pi: tuple[I,...]
    support: tuple[I,...]
    entropy: I
    similarity: I
    flow: I
    diagonal_spread: I
    iterations: int
    return_core: tuple[bool,...]=(True,True,False)
    stopping_steps: tuple[int,...]=()


def _build_informants(kernel,pi,iterations,uniform=False,stopping_steps=None):
    c=kernel.base(); t=kernel.excess
    diag=tuple(as_interval(c[a][a]+t[a]) for a in range(3))
    pi=tuple(as_interval(v) for v in pi)
    support=tuple((pi[a]+diag[a])/2 for a in range(3))
    if uniform:
        # This flag is supplied only after checking exact weighted column
        # masses and equal diagonals of the nominal rational kernel. Mixing
        # with J preserves both identities, so the source's first iterate
        # is exactly uniform and all supports tie. Stable sorting picks 0..4.
        if any(v.lo!=Q(1,20) or v.hi!=Q(1,20) for v in pi):
            raise ValueError('uniform informant premise failed')
        return_core=(True,True,True)
    else:
        if not (pi[0].lo>pi[1].hi and pi[1].lo>pi[2].hi and maximum(*diag).hi<Q(18,100)):
            raise ValueError('return core is not precisely the first ten states')
        if not support[0].lo>maximum(*support[1:]).hi:
            raise ValueError('budget core is not precisely the first five states')
        return_core=(True,True,False)
    ent=-sum(SIZES[a]*pi[a]*pi[a].log() for a in range(3))
    c=tuple(tuple(as_interval(v) for v in row) for row in c)
    t=tuple(as_interval(v) for v in t)
    norm=tuple(sum(SIZES[b]*c[a][b].square() for b in range(3))+2*c[a][a]*t[a]+t[a].square()
               for a in range(3))
    cos=[]
    for a in range(3):
        for b in range(a,3):
            dot=(sum(SIZES[h]*c[a][h]*c[b][h] for h in range(3))
                 +t[a]*c[b][a]+t[b]*c[a][b])
            cos.append(dot/(norm[a]*norm[b]).sqrt())
    # Each of the six pair types occurs at least ten times. Consequently
    # the average of the top ten pair similarities equals their maximum.
    similarity=maximum(*cos)
    imbalance=sum((SIZES[b]-sum(SIZES[a]*as_interval(kernel.mass[a][b]) for a in range(3))).abs()
                  for b in range(3))
    return Informants(pi,support,ent,similarity,1/(1+imbalance),maximum(*diag)-minimum(*diag),iterations,
                      return_core,tuple(stopping_steps or (iterations,)))


def informants(kernel):
    pi,iterations=kernel.finite_informant()
    return _build_informants(kernel,pi,iterations)


def thick_kernel(kernel,radius):
    """Enclose (1-lambda) K + lambda J, 0 <= lambda <= radius."""
    if not isinstance(radius,(int,Q)) or isinstance(radius,bool) or not 0<=radius<1:
        raise ValueError('exact radius in [0,1) required')
    lam=I(0,radius)
    return ClassKernel(tuple(tuple(kernel.mass[a][b]+lam*(Q(SIZES[b],20)-kernel.mass[a][b])
                                   for b in range(3)) for a in range(3)),
                       tuple(t-lam*t for t in kernel.excess))


def thick_informants(kernel):
    """Enclose all possible source early-stop outputs over a kernel box.

    A step whose stopping test may hold contributes its output to the hull.
    Iteration continues for the possibly nonstopped inputs until stopping is
    forced, or the source's 80-step cap is reached. Normalization is exactly
    the identity for EVERY represented stochastic kernel, including correlated
    coordinates whose interval endpoint rows need not sum to one.
    """
    p=tuple(I(Q(n,20)) for n in SIZES)
    candidates=[]; stops=[]
    for step in range(80):
        nxt=tuple(sum(p[a]*kernel.mass[a][b] for a in range(3)) for b in range(3))
        change=maximum(*((nxt[a]-p[a]).abs()/SIZES[a] for a in range(3)))
        if change.lo<=Q(1,10**12) or step==79:
            candidates.append(nxt)
            stops.append(step+1)
        if change.hi<=Q(1,10**12):
            break
        p=nxt
    pi=tuple(I(min(v[a].lo for v in candidates)/SIZES[a],
               max(v[a].hi for v in candidates)/SIZES[a]) for a in range(3))
    return _build_informants(kernel,pi,step+1,stopping_steps=stops)


def uniform_informants(nominal,box=None):
    """Derive the tie-sensitive informant/core branch for a symmetric prefix."""
    if any(sum(SIZES[a]*nominal.mass[a][b] for a in range(3))!=SIZES[b] for b in range(3)):
        raise ValueError('prefix kernel is not exactly doubly stochastic')
    c=nominal.base()
    diagonal=[c[a][a]+nominal.excess[a] for a in range(3)]
    if len(set(diagonal))!=1 or diagonal[0]>=Q(18,100):
        raise ValueError('prefix diagonal tie or quantile branch failed')
    return _build_informants(box or nominal,(Q(1,20),)*3,1,uniform=True)


def evaluate_phase(kernel,phase,tau,budget,info=None):
    """Interval enclosure of original P4/P5/P1/P2/P3/P6 on a proved branch.

    Raises if branch guards are not certified. Returns the pre-noise kernel
    and income-cost enclosure. Timescale preservation uses a separate exact
    four-step estimate, avoiding an assumption that variation is zero.
    """
    info=info or informants(kernel)
    tau=I(tau) if isinstance(tau,(int,Q)) else tau
    budget=I(budget) if isinstance(budget,(int,Q)) else budget
    window=phase//4
    lens=[Q(78,100)*(1-info.entropy/I(20).log())*(Q(82,100)+Q(18,100)*(Q(1,2)+_sin_twelve(phase)/2))
          +Q(5,100)*(1-tau/4)+(Q(42,100) if window==0 else -Q(8,100)),
          Q(32,100)*info.similarity+Q(10,100)*(Q(1,2)+_sin_similarity(phase)/2)
          +Q(8,100)*(1-budget/12)+(Q(42,100) if window==1 else -Q(8,100)),
          Q(19,100)*(info.flow+info.diagonal_spread/20+Q(6,100)*tau/4+Q(5,100)*Q(phase%4,3))
          +(Q(42,100) if window==2 else -Q(8,100))]
    lm=minimum(*(lens[window]-lens[j] for j in range(3) if j!=window))
    if lm.lo<=Q(3,100):
        raise ValueError(f'uncertified lens branch at phase {phase}: {lm}')
    L=lens[window]
    protocol=(Q(1,4) if phase<3 else Q(55,100) if phase<6 else Q(85,100) if phase<9 else Q(2,5))
    package=[minimum(1,Q(28,100)+Q(32,100)*L+Q(18,1000)
                     +Q(14,100)*(Q(1,2)+_sin_twelve(phase+2)/2)+(Q(22,100) if window==0 else 0)),
             minimum(1,Q(32,100)+Q(42,100)*sum(SIZES[a]*info.pi[a] for a in range(3) if info.return_core[a])
                     /sum(SIZES[a] for a in range(3) if info.return_core[a])
                     +Q(12,100)*L+Q(12,100)*tau/4+(Q(22,100) if window==1 else 0)),
             minimum(1,Q(42,100)+Q(28,100)*info.support[0]+budget/200
                     +Q(10,100)*protocol+(Q(22,100) if window==2 else 0))]
    pm=minimum(*(package[window]-package[j] for j in range(3) if j!=window))
    if pm.lo<=Q(3,100):
        raise ValueError(f'uncertified packaging branch at phase {phase}: {pm}')
    C=package[window]; eta=(Q(8,100)+Q(5,100)*C+Q(2,100)*tau).clamp(Q(3,100),Q(18,100))
    core=(True,True,True) if window==0 else info.return_core if window==1 else (True,False,False)
    viability=[as_interval((Q(1,5)+Q(4,5)*info.support[a])*(Q(1,2)+info.pi[a]/2)
                 *(1 if core[a] else Q(2,5))).clamp(Q(8,100),1) for a in range(3)]
    if max(v.hi for v in viability)>=Q(18,100):
        raise ValueError('P2 fallback branch is not certified')
    m=kernel.mass; t=kernel.excess; target=[]; target_t=[]
    shift=(Q(2,100)*L if window==0 else Q(3,100)*C if window==1 else Q(1,100)*C)
    for a in range(3):
        if window==0:
            scales=[1 if (a<2)==(b<2) else Q(2,5) for b in range(3)]
            additions=[I(Q(1,10)*SIZES[b]) if (a<2)==(b<2) else I(0) for b in range(3)]
            diagonal=shift
        elif window==1:
            scales=[1 if core[b] else Q(35,100) for b in range(3)]
            additions=[I(Q(8 if core[a] else 12,100)*SIZES[b]) if core[b] else I(0) for b in range(3)]
            diagonal=shift
        else:
            scales=[1 if core[b] else Q(1,2) for b in range(3)]
            additions=[(Q(7,100)+Q(3,100)*C)*SIZES[b] if core[b] else I(0) for b in range(3)]
            diagonal=shift+(Q(5,100) if core[a] else 0)
        denominator=sum(scales[b]*m[a][b]+additions[b] for b in range(3))+diagonal
        target.append(tuple((scales[b]*m[a][b]+additions[b]+(diagonal if a==b else 0))/denominator
                            for b in range(3)))
        target_t.append((scales[a]*t[a]+diagonal)/denominator)
    mixed=[[m[a][b]+eta*(target[a][b]-m[a][b]) for b in range(3)] for a in range(3)]
    mixed_t=[t[a]+eta*(target_t[a]-t[a]) for a in range(3)]
    weights=[I(1) if core[b] else I(Q(55,100)).sqrt() for b in range(3)]
    fbden=sum(SIZES[b]*(4 if core[b] else 1) for b in range(3))
    new=[]; new_t=[]
    for a in range(3):
        den=sum(mixed[a][b]*weights[b] for b in range(3))
        new.append(tuple(Q(65,100)*mixed[a][b]*weights[b]/den
                         +Q(35,100)*Q(SIZES[b]*(4 if core[b] else 1),fbden) for b in range(3)))
        new_t.append(Q(65,100)*mixed_t[a]*weights[a]/den)
    base=tuple(tuple((new[a][b]-new_t[a]*int(a==b))/SIZES[b] for b in range(3)) for a in range(3))
    old=kernel.base()
    v2=sum(SIZES[a]*SIZES[b]*(base[a][b]-old[a][b]).square() for a in range(3) for b in range(3) if a!=b)
    v2=v2+sum(SIZES[a]*(SIZES[a]-1)*(base[a][a]-old[a][a]).square()
              +SIZES[a]*(base[a][a]+new_t[a]-old[a][a]-t[a]).square() for a in range(3))
    variation=v2.sqrt()
    switched=phase%4==0
    income=Q(108,100)*(Q(24,100)*C+Q(12,100)*L+Q(8,100)*maximum(0,1-variation))
    cost=Q(96,100)*(Q(6,100)+Q(18,1000)*((phase+1)%12)+Q(4,100)*variation)+(Q(6,100) if switched else 0)
    target_base=tuple(tuple((target[a][b]-target_t[a]*int(a==b))/SIZES[b] for b in range(3)) for a in range(3))
    distance2=sum(SIZES[a]*SIZES[b]*(target_base[a][b]-old[a][b]).square()
                  for a in range(3) for b in range(3) if a!=b)
    distance2=distance2+sum(SIZES[a]*(SIZES[a]-1)*(target_base[a][a]-old[a][a]).square()
        +SIZES[a]*(target_base[a][a]+target_t[a]-old[a][a]-t[a]).square() for a in range(3))
    return {'base':base,'excess':tuple(new_t),'variation':variation,'income_minus_cost':income-cost,
            'lens_margin':lm,'packaging_margin':pm,'eta':eta,'lens':L,'package':C,
            'viability_max':maximum(*viability),'viability_mean':sum(SIZES[a]*viability[a] for a in range(3))/20,
            'income':income,'p1_target_distance':distance2.sqrt()}


def noise_bound(evaluation,target):
    """Maximum entrywise innovation needed to reach the exact target kernel."""
    c=target.base(); t=target.excess
    errors=[]
    for a in range(3):
        for b in range(3):
            errors.append((evaluation['base'][a][b]-c[a][b]).abs())
        errors.append((evaluation['base'][a][a]+evaluation['excess'][a]-c[a][a]-t[a]).abs())
    return maximum(*errors)


def _round_center(interval):
    midpoint=(interval.lo+interval.hi)/2
    grid=10**12
    return Q(round(midpoint*grid),grid)


def _uniform_center(evaluation):
    # Preserve EXACT double stochasticity and equal diagonal ties before
    # the first budget phase. Independent entry rounding would destroy them.
    h=_round_center(evaluation['excess'][0])
    cross=_round_center(evaluation['base'][0][2])
    g=1-h-20*cross
    labels=(0,0,1)
    mass=tuple(tuple(SIZES[b]*(cross+(g/10 if labels[a]==labels[b] else 0))
                     +h*int(a==b) for b in range(3)) for a in range(3))
    result=ClassKernel(mass,(h,)*3)
    uniform_informants(result)
    return result


def _class_center(evaluation):
    mass=[]
    for a in range(3):
        row=[_round_center((evaluation['base'][a][b]*SIZES[b])+
                          evaluation['excess'][a]*int(a==b)) for b in range(3)]
        row[a]=1-sum(row[b] for b in range(3) if b!=a)
        mass.append(tuple(row))
    return ClassKernel(tuple(mass),tuple(_round_center(v) for v in evaluation['excess']))


def construct_entry_prefix(length=24):
    """Construct rational control targets; every transition needs certification.

    The first target is the fixed half join at score 159/200. Scores in the
    original irrational [.79,.80] branch are NOT replaced with this value:
    their actual pre-noise rows are corrected to this one fixed target.
    """
    if length<12 or length%12:
        raise ValueError('prefix length must be a positive multiple of twelve')
    from .original_loop_extension import construct_original_loop_extension,exact_half_join
    r=exact_half_join(construct_original_loop_extension(),Q(159,200)).common_kernel
    starts=(0,5,10)
    m=tuple(tuple(sum(r[i][j] for j in range(sum(SIZES[:b]),sum(SIZES[:b+1])))
                  for b in range(3)) for i in starts)
    current=ClassKernel(m,(Q(0),)*3)
    if current.full()!=r:
        raise ArithmeticError('entry target does not equal the exact shared half kernel')
    prefix=[]
    for step in range(length):
        phase=(step+1)%12
        uniform=step<8
        info=uniform_informants(current) if uniform else informants(current)
        prefix.append((phase,current,uniform))
        e=evaluate_phase(current,phase,I(Q(3,5)),I(12),info)
        current=_uniform_center(e) if step<7 else _class_center(e)
    return tuple(prefix)


def certify_entry_prefix(prefix=None,cycle=None,radius=Q(1,10**14)):
    prefix=construct_entry_prefix() if prefix is None else prefix
    cycle=load_cycle() if cycle is None else cycle
    if not prefix or len(prefix)%12 or any(phase!=(step+1)%12 for step,(phase,_,_) in enumerate(prefix)):
        raise ValueError('entry prefix has an inconsistent phase schedule')
    for _,kernel,_ in prefix:
        kernel.check_exact()
    rows=[]
    prefix_floor=min(v for _,k,_ in prefix for row in k.full() for v in row)
    if prefix_floor<Q(1,100):
        raise ValueError('entry prefix lost the derived positive kernel floor')
    for step,(phase,kernel,uniform) in enumerate(prefix):
        info=uniform_informants(kernel) if uniform else informants(kernel)
        target=prefix[step+1][1] if step+1<len(prefix) else thick_kernel(cycle[1],radius)
        tb=tau_box(phase)
        worst={'noise_cap':Q(0),'income_floor':Q(1),'lens_margin_floor':Q(1),'packaging_margin_floor':Q(1)}
        for bi in range(18):
            b=I(Q(3)+Q(bi,2),Q(3)+Q(bi+1,2))
            for ti in range(4):
                tau=I(tb.lo+(tb.hi-tb.lo)*Q(ti,4),tb.lo+(tb.hi-tb.lo)*Q(ti+1,4))
                e=evaluate_phase(kernel,phase,tau,b,info)
                worst['noise_cap']=max(worst['noise_cap'],noise_bound(e,target).hi)
                worst['income_floor']=min(worst['income_floor'],e['income_minus_cost'].lo)
                worst['lens_margin_floor']=min(worst['lens_margin_floor'],e['lens_margin'].lo)
                worst['packaging_margin_floor']=min(worst['packaging_margin_floor'],e['packaging_margin'].lo)
        if worst['noise_cap']>=Q(1,1000) or worst['income_floor']<=0:
            raise ValueError(f'entry step {step} failed: {worst}')
        rows.append({'step':step,'phase':phase,'informant_uniform':uniform,
                     **{key:str(value) for key,value in worst.items()}})
    # Returning the target data makes the control word reviewable and repeatable.
    return {'length':len(prefix),'derived_kernel_floor':str(prefix_floor),'phases':rows,
            'targets':[{'phase':phase,'mass':[[str(v) for v in row] for row in kernel.mass],
                        'excess':[str(v) for v in kernel.excess]} for phase,kernel,_ in prefix]}


def certify_six_role_dependence(cycle=None):
    """Actual counterfactual changes at one lawful phase-0 state.

    Use the SAME standardized random-input word for P1/P2/P4/P5 knockouts, rather
    than recomputing a controller that would cancel the changed primitive.
    Row-zero innovation and positivity preserve the displayed scalar gaps.
    P3 changes the phase; P6 changes budget at b=3 before saturation.
    """
    k=(cycle or load_cycle())[0]; info=informants(k)
    e=evaluate_phase(k,0,I(Q(3,5)),I(3),info)
    cross=k.base()[0][2]
    p1off=Q(65,100)*cross+Q(35,2000)
    p2off=(e['base'][0][2]-Q(35,2000))/Q(65,100)
    p1gap=I(p1off)-e['base'][0][2]
    p2gap=e['base'][0][2]-p2off
    # P4 knockout: refresh halves support, the incumbent audit lens has
    # score zero, and cluster remains the isolated actual P5 winner.
    c4=Q(28,100)+Q(18,1000)+Q(14,100)*(Q(1,2)+_sin_twelve(2)/2)+Q(22,100)
    return4=I(Q(32,100))+Q(42,100)*(info.pi[0]+info.pi[1])/2+Q(12,100)*Q(3,20)
    budget4=I(Q(42,100))+Q(28,100)*info.support[0]/2+Q(3,200)+Q(1,40)
    if minimum(c4-return4,c4-budget4).lo<=Q(3,100):
        raise ValueError('P4 knockout packaging branch not certified')
    eta4=Q(8,100)+Q(5,100)*c4+Q(2,100)*Q(3,5)
    den4=sum(k.mass[0][b]*(1 if b<2 else Q(2,5)) for b in range(3))+1+Q(1,100)*c4
    p4off=Q(65,100)*(cross+eta4*(Q(2,5)*cross/den4-cross))+Q(35,2000)
    p4gap=p4off-e['base'][0][2]
    # P5 knockout uses the actual fallback packaging (first five states),
    # score zero, with the selected spectral lens's unchanged score/shift.
    m=k.mass[2][0]
    den5=I(Q(1,2)+m/2+Q(35,100))+Q(2,100)*e['lens']
    target5=(m+Q(35,100))/den5
    if target5.lo<=m:
        raise ValueError('P5 knockout core-mass increase not certified')
    # Row class C has clamped viability .08, so its fallback is used;
    # gating cannot reduce its core mass. This bound needs no new selector.
    p5lower=Q(65,100)*m+Q(35,100)*Q(4,7)
    p5gap=I(p5lower)-5*e['base'][2][0]
    target=(cycle or load_cycle())[1]
    control_cap=noise_bound(e,target).hi
    # z=N/sigma is the fixed standardized innovation, |z|<=cap/.0025.
    # A knockout can change P6's sigma within [.0025,.0045]. Therefore
    # its innovation changes by at most .002*cap/.0025=.8*cap. The
    # coordinate word still has row sum zero after a common rescaling.
    noise_change_cap=Q(4,5)*control_cap
    gaps={'P1_kernel_entry':p1gap.lo-noise_change_cap,
          'P2_kernel_entry':p2gap.lo-noise_change_cap,
          'P4_kernel_entry':p4gap.lo-noise_change_cap,
          'P5_core_mass':p5gap.lo-5*noise_change_cap,
          'P3_phase':Q(1),'P3_budget':Q(216,12500),'P6_budget':e['income_minus_cost'].lo}
    if min(gaps.values())<=0:
        raise ValueError('a primitive failed the scalar nonredundancy check')
    # The shared correction is row zero and is below .001. All relevant
    # counterfactual rows stay positive after it, so no clipping can mask a gap.
    if noise_bound(e,target).hi>=Q(1,1000) or min(v for row in k.full() for v in row)<=Q(1,100):
        raise ValueError('counterfactual clipping margin not certified')
    return {'state':{'phase':0,'tau':'3/5','budget':'3'},
            'same_standardized_random_word_under_knockouts':True,
            'budget_dependent_innovation_change_cap':str(noise_change_cap),
            'positive_scalar_gaps':{name:str(value) for name,value in gaps.items()},
            'scope':'each role changes the physical law somewhere on the controlled shell; not every coordinate at every state'}


def certify_cycle(cycle=None,radius=Q(1,10**14)):
    """Exhaustive rational interval certificate over all phase boxes.

    The 18 budget cells and four timescale cells cover [3,12] and the exact
    phasewise timescale intervals. Current and next kernel parameters are
    independent in [0,radius]; no endpoint sampling is used. Every tested
    inequality is strict, leaving room for the Cantor parameter family.
    """
    cycle=load_cycle() if cycle is None else cycle
    if len(cycle)!=12 or not isinstance(radius,(Q,int)) or isinstance(radius,bool) or not 0<radius<1:
        raise ValueError('twelve exact kernels and a strictly positive exact radius are required')
    for kernel in cycle:
        kernel.check_exact()
    boxes=tuple(thick_kernel(c,radius) for c in cycle)
    kernel_floor=min(v.lo for k in boxes for row in k.full() for v in row)
    if kernel_floor<Q(1,100):
        raise ValueError('derived original-shell positive kernel floor failed')
    rows=[]
    for phase,kernel in enumerate(boxes):
        info=thick_informants(kernel)
        if len(info.stopping_steps)!=1:
            raise ValueError('continuous shell requires one fixed informant stopping count per phase')
        tb=tau_box(phase)
        worst={'noise_cap':Q(0),'income_floor':Q(1),'lens_margin_floor':Q(1),
               'packaging_margin_floor':Q(1),'viability_cap':Q(0)}
        for bi in range(18):
            b=I(Q(3)+Q(bi,2),Q(3)+Q(bi+1,2))
            for ti in range(4):
                tau=I(tb.lo+(tb.hi-tb.lo)*Q(ti,4),tb.lo+(tb.hi-tb.lo)*Q(ti+1,4))
                e=evaluate_phase(kernel,phase,tau,b,info)
                worst['noise_cap']=max(worst['noise_cap'],noise_bound(e,boxes[(phase+1)%12]).hi)
                worst['income_floor']=min(worst['income_floor'],e['income_minus_cost'].lo)
                worst['lens_margin_floor']=min(worst['lens_margin_floor'],e['lens_margin'].lo)
                worst['packaging_margin_floor']=min(worst['packaging_margin_floor'],e['packaging_margin'].lo)
                worst['viability_cap']=max(worst['viability_cap'],e['viability_max'].hi)
        if not (worst['noise_cap']<Q(1,1000)<Q(1,400)
                and worst['income_floor']>Q(1,100)
                and worst['lens_margin_floor']>Q(3,100)
                and worst['packaging_margin_floor']>Q(3,100)
                and worst['viability_cap']<Q(18,100)):
            raise ValueError(f'phase {phase} does not meet the shell certificate inequalities')
        rows.append({'phase':phase,'tau_lower':str(tb.lo),'tau_upper':str(tb.hi),
                     'finite_informant_iteration_cap':info.iterations,
                     'finite_informant_stopping_steps':info.stopping_steps,
                     **{key:str(value) for key,value in worst.items()}})
    # A phase 8 -> 9 jump recurs once every twelve steps. One entry is
    # enough for a Frobenius lower bound, including independent parameters.
    before=boxes[8].full()[0][0]; after=boxes[9].full()[0][0]
    jump=after-before
    if jump.lo<=Q(1,50):
        raise ValueError('recurring jump is not certified')
    return {'scope':'controlled legal innovation words for original 20-state pilot parameters',
            'kernel_parameter_radius':str(radius),'budget_interval':['3','12'],
            'derived_kernel_floor':str(kernel_floor),
            'original_potential_branch_weight_bounds':['1/1000','4/5'],
            'pressure_at_zero':'log(20)',
            'unique_pressure_root_interval':['1/3','1'],
            'selector_schedule':['spectral/cluster']*4+['similarity/return']*4+['audit/budget']*4,
            'recurring_entry_jump_floor':str(jump.lo),'phases':rows,
            'informant_stopping_guards_stable':True,
            'uncontrolled_noise_invariance':False,'seeded_reachability_established':False,
            'original_extension_pair_joined_to_this_shell':False,
            'six_role_nonredundancy_certified':False,
            'main_theorem_package_complete':False}
