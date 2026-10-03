from fractions import Fraction as Q
from itertools import product

import mpmath as mp
import pytest

from contextual_cantor.packaged_world_disintegration import (
    PackagedWorldLaw,construct_packaged_world_law,periodic_matrix_pressure,
)
from contextual_cantor.original_loop_extension import (
    construct_original_loop_extension,integer_moving_history_rows,exact_fixed_half_join,
)
from contextual_cantor.controlled_shell import load_cycle
from contextual_cantor.controlled_pressure_separation import mix_cycle,periodic_observable_pressure


@pytest.fixture(scope='module')
def data():
    c=load_cycle()
    orbits=(c,mix_cycle(c,Q(1,100)))
    return orbits,tuple(periodic_observable_pressure(x) for x in orbits)


def test_actual_objects_define_positive_fibers_and_exact_conditionals():
    w=construct_original_loop_extension()
    for weight in (Q(1,2),Q(1,7),Q(9,10)):
        law=construct_packaged_world_law(weight)
        assert law.objects==tuple(a.stationary for a in w.audit)
        values=(Q(2,7),Q(11,13))
        for i,obj in enumerate(law.objects):
            assert law.fiber(obj)==(i,)
            assert law.mass(obj)==law.weights[i]
            assert law.conditional(values,obj)==values[i]
        assert sum(law.mass(o)*law.conditional(values,o) for o in law.objects)==law.expectation(values)
        with pytest.raises(ValueError):law.conditional(values,w.spectral.stationary)


def test_actual_fiber_law_matches_same_potential_explicit_path_sum():
    w=construct_original_loop_extension()
    law=construct_packaged_world_law()
    values=[]
    joined=exact_fixed_half_join(w,Q(79,100)).common_kernel
    for z in (0,1):
        kernels=(w.kernels[z],joined)
        # Rational scalar weights exercise exact path-integral algebra.
        # The actual source q is enclosed separately in the pressure tests.
        scales=(Q(2,3),Q(3,5))
        rows=integer_moving_history_rows(kernels,2,scales)
        value=sum(p*r for p,r in zip(law.objects[z],rows))
        # Reference probability is the ORIGINAL K path law. The integrand
        # A_s/K cancels it, yielding the original matrix path partition.
        explicit=sum(law.objects[z][i]*kernels[0][i][j]*kernels[1][j][k]
                     *((scales[0]*kernels[0][i][j])**2/kernels[0][i][j])
                     *((scales[1]*kernels[1][j][k])**2/kernels[1][j][k])
                     for i,j,k in product(range(20),repeat=3))
        assert explicit==value
        values.append(value)
    assert law.expectation(values)==sum(law.mass(o)*law.conditional(values,o) for o in law.objects)


@pytest.mark.parametrize('s',[Q(0),Q(1,2),Q(3,4),Q(1),Q(5,4),Q(3,2)])
@pytest.mark.parametrize('observable',['closure','operator'])
def test_periodic_pressure_collatz_certificate_against_full_twenty_state_product(data,s,observable):
    orbits,periodic=data
    pressures=[]
    for orbit,p in zip(orbits,periodic):
        pressure,cert=periodic_matrix_pressure(orbit,s,observable,p)
        pressures.append(pressure)
        with mp.workdps(80):
            def exact(x):
                x=Q(x)
                return mp.mpf(x.numerator)/x.denominator
            vector=[exact(cert['test_vector'][0 if i<5 else 1 if i<10 else 2]) for i in range(20)]
            image=vector[:]
            for kernel,row in reversed(tuple(zip(orbit,p['phase_observables']))):
                qlo,qhi=map(Q,row[observable+'_q'])
                q=exact((qlo+qhi)/2)
                full=kernel.full()
                image=[sum(mp.exp(exact(s)*(mp.log(exact(full[i][j]))-q))*image[j]
                           for j in range(20)) for i in range(20)]
            ratios=[a/b for a,b in zip(image,vector)]
            lower,upper=map(exact,cert['eigenvalue_interval'])
            assert lower-mp.mpf('1e-60')<=min(ratios)<=max(ratios)<=upper+mp.mpf('1e-60')
        if s==1:
            anchor=p[observable+'_pressure_at_one']
            assert pressure.lo<=anchor.hi and anchor.lo<=pressure.hi
    gap=(pressures[1]-pressures[0]).abs()/2
    if s==0:
        assert pressures[0]==pressures[1]
        assert gap.lo==0
    else:
        assert gap.lo>0
    if s==1:
        assert gap.lo>Q(1,2000)


def test_strictness_does_not_force_gap_when_future_law_is_uncorrelated(data):
    law=construct_packaged_world_law()
    assert law.objects[0]!=law.objects[1]
    orbit=data[0][0]; p=data[1][0]
    pressure,_=periodic_matrix_pressure(orbit,Q(1),'operator',p)
    # Both ACTUAL completion outputs condition the same future in this control.
    left=law.conditional((pressure,pressure),law.objects[0])
    right=law.conditional((pressure,pressure),law.objects[1])
    assert left==right
    # Interval arithmetic can widen an enclosure even for multiplication
    # and division by the same fixed probability.
    assert left.lo<=pressure.lo and pressure.hi<=left.hi
    assert law.expectation((Q(7),Q(7)))==7


def test_zero_mass_merged_objects_and_inexact_inputs_are_rejected():
    law=construct_packaged_world_law()
    with pytest.raises(ValueError):PackagedWorldLaw((law.objects[0],law.objects[0]))
    for weight in (0,1,True,0.5,Q(-1)):
        with pytest.raises(ValueError):construct_packaged_world_law(weight)
    for s in (-1,0.5,True):
        with pytest.raises(ValueError):periodic_matrix_pressure(load_cycle(),s)
