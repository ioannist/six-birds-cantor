"""Genuine object-fiber conditioning under an explicit legal-input WORLD law.

This is a construction, not the original independent-noise experiment law.
The continuation is correlated with the actual current audit completion.
Current scalar descriptors agree, but full future pressure profiles do not.
The law pressure is not silently identified with a larger shell supremum.
"""
from dataclasses import dataclass
from fractions import Fraction as Q

from .original_loop_extension import construct_original_loop_extension
from .controlled_shell import load_cycle, certify_cycle, certify_entry_prefix
from .controlled_pressure_separation import mix_cycle, periodic_observable_pressure
from .rational_interval import Interval as I


def _exact_weight(w):
    if not isinstance(w, (int, Q)) or isinstance(w, bool) or not 0 < w < 1:
        raise ValueError('a fixed strictly positive exact binary probability is required')
    return Q(w)


@dataclass(frozen=True)
class PackagedWorldLaw:
    """Two atoms on worlds, with the completion VECTOR as the fiber map.

    Each atom includes its current kernel and prescribed future legal inputs.
    Conditional microscopic paths use that atom's kernels and start at its
    actual audit fixed vector. The continuation index is not the fiber map.
    """
    objects: tuple[tuple[Q, ...], tuple[Q, ...]]
    weight: Q = Q(1, 2)

    def __post_init__(self):
        _exact_weight(self.weight)
        if len(self.objects) != 2 or self.objects[0] == self.objects[1]:
            raise ValueError('two distinct actual completion outputs are required')
        for obj in self.objects:
            if len(obj) != 20 or any(not isinstance(x, (Q, int)) or isinstance(x, bool)
                    or x <= 0 for x in obj) or sum(obj) != 1:
                raise ValueError('objects must be exact positive 20-state probability vectors')

    @property
    def weights(self):
        return self.weight, 1-self.weight

    def fiber(self, obj):
        # An impossible event has no selected conditional law here.
        if obj not in self.objects:
            raise ValueError('conditioning object has zero reference mass')
        return tuple(i for i, actual in enumerate(self.objects) if actual == obj)

    def mass(self, obj):
        return sum(self.weights[i] for i in self.fiber(obj))

    def integral(self, values, obj):
        if len(values) != 2:
            raise ValueError('one integrand value per world is required')
        return sum(self.weights[i]*values[i] for i in self.fiber(obj))

    def conditional(self, values, obj):
        return self.integral(values, obj)/self.mass(obj)

    def expectation(self, values):
        if len(values) != 2:
            raise ValueError('one integrand value per world is required')
        return sum(w*v for w,v in zip(self.weights, values))


def construct_packaged_world_law(weight=Q(1, 2)):
    witness = construct_original_loop_extension()
    return PackagedWorldLaw(tuple(a.stationary for a in witness.audit), _exact_weight(weight))


def periodic_matrix_pressure(cycle, parameter, observable='operator', periodic=None):
    """Certified full 20-state history pressure via a three-cell invariant subspace.

    Row sums of every product are constant on the three physical classes.
    Its infinity row norm is EXACTLY that of the three-by-three aggregate,
    including the separate diagonal term. A positive rational test vector
    gives Collatz bounds for the aggregate twelve-step Perron eigenvalue.
    Power iteration only proposes the vector; no convergence is assumed.
    """
    if not isinstance(parameter, (int,Q)) or isinstance(parameter,bool) or parameter < 0:
        raise ValueError('an exact nonnegative pressure parameter is required')
    if observable not in ('closure','operator'):
        raise ValueError('choose an original source observable')
    periodic = periodic_observable_pressure(cycle) if periodic is None else periodic
    if parameter == 0:
        return I(20).log(), {'eigenvalue_interval':['4096000000000000']*2,
            'test_vector':['1']*3, 'parameter':'0'}
    sizes=(5,5,10)
    matrices=[]
    for kernel,row in zip(cycle,periodic['phase_observables']):
        q=I(*map(Q,row[observable+'_q']))
        base=kernel.base()
        matrix=[]
        for a in range(3):
            values=[]
            for b,n in enumerate(sizes):
                count=n-int(a==b)
                value=count*(parameter*(I(base[a][b]).log()-q)).exp()
                if a==b:
                    value=value+(parameter*(I(base[a][b]+kernel.excess[a]).log()-q)).exp()
                values.append(value)
            matrix.append(tuple(values))
        matrices.append(tuple(matrix))
    product=tuple(tuple(I(int(i==j)) for j in range(3)) for i in range(3))
    for matrix in matrices:
        product=tuple(tuple(sum(product[i][k]*matrix[k][j] for k in range(3))
                            for j in range(3)) for i in range(3))
    vector=(Q(1),)*3
    for _ in range(24):
        image=[sum(product[i][j]*vector[j] for j in range(3)) for i in range(3)]
        centers=[(x.lo+x.hi)/2 for x in image]
        scale=max(centers)
        vector=tuple(Q(round(x/scale*10**16),10**16) for x in centers)
        if min(vector)<=0:
            raise ValueError('positive Collatz vector could not be constructed')
    ratios=[sum(product[i][j]*vector[j] for j in range(3))/vector[i] for i in range(3)]
    eigenvalue=I(min(x.lo for x in ratios),max(x.hi for x in ratios))
    pressure=eigenvalue.log()/12
    return pressure, {'eigenvalue_interval':[str(eigenvalue.lo),str(eigenvalue.hi)],
        'test_vector':list(map(str,vector)), 'parameter':str(parameter)}


def certify_packaged_world_disintegration(include_carrier=True):
    law=construct_packaged_world_law()
    cycle=load_cycle()
    other=mix_cycle(cycle,Q(1,100))
    orbits=(cycle,other)
    periodic=tuple(periodic_observable_pressure(c) for c in orbits)
    profiles=[]
    # Both historical source grids, with zero as a mandatory false-target control.
    for s in (Q(0),Q(1,2),Q(3,4),Q(1),Q(5,4),Q(3,2)):
        for observable in ('closure','operator'):
            values=[]; proofs=[]
            for c,p in zip(orbits,periodic):
                value,proof=periodic_matrix_pressure(c,s,observable,p)
                values.append(value);proofs.append(proof)
            difference=(values[1]-values[0]).abs()
            # Equal-weight gap = abs(P1-P0)/2, independently of ordering.
            gap=difference/2
            if s>0 and gap.lo<=0:
                raise ValueError(f'gap not certified on original grid at {s}, {observable}')
            profiles.append({'parameter':str(s),'observable':observable,
                'conditional_pressure_intervals':[[str(v.lo),str(v.hi)] for v in values],
                'gap_interval':[str(gap.lo),str(gap.hi)],'collatz_certificates':proofs})
    report={'scope':'actual current audit-completion fibers under a constructed package-correlated legal-input world law',
        'fiber_map':'world -> actual current audit stationary probability vector',
        'objects':[[str(x) for x in obj] for obj in law.objects],
        'fixed_fiber_weights':list(map(str,law.weights)),
        'object_recognition':'compare coordinate zero to the midpoint of the two exact audit outputs',
        'continuation_assignment':['original cycle','one-percent uniform mixture of original cycle'],
        'finite_disintegration':'Z_n = (Z_n | actual object 0)/2 + (Z_n | actual object 1)/2, exactly',
        'path_reference':'world atom, then initial law = its actual completion, then original K_t Markov transitions',
        'path_integrand':'product over t of A_s(i_t,i_{t+1})/K_t(i_t,i_{t+1}); same original A_s',
        'law_pressure':'max of the two conditional pressures; finite prefixes do not affect limits',
        'pressure_profiles':profiles,
        'genuine_actual_object_fiber_law_constructed':True,
        'original_independent_noise_law':False,
        'shared_current_scalar_descriptors':True,
        'shared_full_future_scalar_history_base':False,
        'identification_with_two_world_forward_orbit_carrier':True,
        'identification_with_original_global_shell_supremum':False,
        'paper_current_three_lens_family_identified':False,
        'main_theorem_package_complete':False,
        'zero_parameter_gap_exactly_zero':True,
        'all_historical_positive_grid_gaps_certified':True}
    report['positive_grid_gap_floor']=str(min(Q(p['gap_interval'][0])
        for p in profiles if Q(p['parameter'])>0))
    radius=Q(1,10**6)
    neighborhood_floor=Q(report['positive_grid_gap_floor'])-7*radius
    if neighborhood_floor<=0:
        raise ValueError('positive grid neighborhood failed the Lipschitz bound')
    report['positive_grid_neighborhood_radius']=str(radius)
    report['positive_grid_neighborhood_gap_floor']=str(neighborhood_floor)
    report['neighborhood_derivation']=('Original branch weights are in [1/1000,4/5], '
        'so each pressure is 7-Lipschitz and the equal-weight gap is 7-Lipschitz.')
    for observable in ('closure','operator'):
        for parameter,sign in (('5/4',1),('3/2',-1)):
            row=next(p for p in profiles if p['parameter']==parameter and p['observable']==observable)
            d=I(*map(Q,row['conditional_pressure_intervals'][1]))-I(*map(Q,row['conditional_pressure_intervals'][0]))
            if (sign==1 and d.lo<=0) or (sign==-1 and d.hi>=0):
                raise ValueError('pressure crossing endpoints did not have certified opposite signs')
    report['gap_positive_for_all_positive_parameters']=False
    report['pressure_crossing_obstruction']=('For each original observable, P1-P0 is positive at 5/4 '
        'and negative at 3/2. Continuity forces a zero gap somewhere between them. '
        'Positivity is a finite-grid and neighborhood claim, not an all-parameter claim.')
    if include_carrier:
        report['alternate_all_time_carrier']=certify_cycle(other)
        report['alternate_entry_prefix']=certify_entry_prefix(cycle=other)
    return report
