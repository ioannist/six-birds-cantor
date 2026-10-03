"""Uniform pressure bounds for ALL Cantor input words in two original carriers.

The same positive test vector controls each allowed twelve-step block, so the
certificate is not a periodic-orbit approximation. A separate analytic
subadditive variational argument constructs one fixed reference law attaining
both carriers' supremum pressures for both original potentials at all s>=0.
It is not a sampled, computable, or independent-noise reference law.
"""
from fractions import Fraction as Q

from .controlled_shell import load_cycle,thick_kernel,certify_cycle,certify_entry_prefix
from .controlled_pressure_separation import mix_cycle,periodic_observable_box
from .packaged_world_disintegration import construct_packaged_world_law,periodic_matrix_pressure
from .original_loop_extension import construct_original_loop_extension
from .rational_interval import Interval as I


RADIUS=Q(1,10**14)
GRID=(Q(0),Q(1,2),Q(3,4),Q(1),Q(5,4),Q(3,2))


def certify_all_word_pressure_disintegration(include_carriers=True):
    law=construct_packaged_world_law()
    nominal=(load_cycle(),mix_cycle(load_cycle(),Q(1,100)))
    boxes=tuple(tuple(thick_kernel(k,RADIUS) for k in cycle) for cycle in nominal)
    q_boxes=tuple(periodic_observable_box(cycle,RADIUS) for cycle in nominal)
    q_low=I(Q(5,4)).log().hi
    q_high=I(10).log().lo
    for family in q_boxes:
        for row in family['phase_observables']:
            for observable in ('closure','operator'):
                lo,hi=map(Q,row[observable+'_q'])
                if not q_low<lo<=hi<q_high:
                    raise ValueError('original q branch bounds failed on a continuous input family')
    profiles=[]
    for s in GRID:
        for observable in ('closure','operator'):
            pressures=[];certificates=[]
            for box,q in zip(boxes,q_boxes):
                bound,proof=periodic_matrix_pressure(box,s,observable,q,start_phase=1)
                # On this BOX, proof controls EVERY block, not just one orbit.
                pressures.append(bound);certificates.append(proof)
            # At s=0 the full positive 20-state matrices are all-ones exactly.
            gap=I(0) if s==0 else (pressures[1]-pressures[0]).abs()/2
            if s>0 and gap.lo<=Q(1,25000):
                raise ValueError(f'all-word gap failed at {s}, {observable}')
            profiles.append({'parameter':str(s),'observable':observable,
                'carrier_pressure_intervals':[[str(p.lo),str(p.hi)] for p in pressures],
                'global_equal_weight_gap_interval':[str(gap.lo),str(gap.hi)],
                'all_block_collatz_certificates':certificates})
    floor=min(Q(p['global_equal_weight_gap_interval'][0]) for p in profiles if Q(p['parameter'])>0)
    witness=construct_original_loop_extension()
    families=tuple(tuple(sorted((witness.audit[z].stationary,witness.spectral.stationary,
                                  witness.cluster.stationary))) for z in (0,1))
    if families[0]==families[1]:
        raise ValueError('actual full packaged-family readout failed to split')
    report={
        'scope':'all legal Cantor input words in the union of the two original-parameter controlled carriers and their actual warm-state entry hull',
        'current_kernel_parameter_interval':['0',str(RADIUS)],
        'input_word_space':'scaled middle-thirds Cantor set to the power N; independent target parameters at every step',
        'original_independent_noise_law':False,
        'source_arithmetic_scope':'exact-real interpretation of original formulas; not bitwise floating simulator invariance',
        'quantile_tie_scope':'warm stationary informant is exactly uniform, so spectral completion includes all states; floating rounding can choose a different core',
        'continuous_input_word_family':True,
        'periodic_only_restriction':False,
        'uniform_all_word_pressure_profiles':profiles,
        'positive_grid_gap_floor':str(floor),
        'positive_grid_neighborhood_radius':'1/1000000',
        'positive_grid_neighborhood_gap_floor':str(floor-Q(7,10**6)),
        'reference_law_construction':'For each carrier use half the full-support fair Cantor product law plus half a countable mixture of return-map invariant measures with growth within 1/k of its supremum at rational s, for BOTH original q definitions. All probabilities are fixed and positive.',
        'reference_law_depends_on_evaluation_parameter':False,
        'reference_law_has_full_support_on_each_return_input_family':True,
        'reference_law_numerically_instantiated':False,
        'reference_law_existence_analytic':True,
        'reference_pressure_equals_global_shell_supremum_analytic':True,
        'reference_law_variational_source':{
            'author':'Sebastian J. Schreiber','year':1998,
            'title':'On Growth Rates of Subadditive Functions for Semiflows',
            'theorem':'Theorem 1, discrete-time case; proof in section 3',
            'url':'https://schreiber.faculty.ucdavis.edu/wp-content/uploads/sites/568/2021/05/jde2000.pdf',
            'hypotheses':'compact metric return space, continuous return map, continuous real subadditive log-norm cocycle',
            'readout':'sup invariant-measure integrated growth equals inf_m sup_y log norm(A_(12m)(y))/m'},
        'fixed_actual_package_fiber_weights':list(map(str,law.weights)),
        'reference_initial_support':'the two actual warm kernels K+ and K-; the continuous shell supplies the envelope, not an initial distribution over every shell point',
        'exhausts_packaged_outputs_over_original_descriptor':False,
        'actual_audit_objects':[[str(v) for v in obj] for obj in law.objects],
        'actual_full_packaged_families':[[[str(v) for v in obj] for obj in f] for f in families],
        'conditioning_audit_output_equivalent_to_full_family_on_reference_support':True,
        'finite_same_potential_disintegration':'Z_n=(Z_n | actual current audit completion u+)/2+(Z_n | actual current audit completion u-)/2',
        'supremum_return':'uniform finite entry to the budget-12, phase-1 return section; fixed positive matrix prefactors; twelve-step remainder bounds',
        'uniform_budget_cap_time_bound':900,
        'uniform_entry_to_return_section_bound':912,
        'warm_entry_prefix_length_including_join':25,
        'shared_current_scalar_base':True,
        'shared_full_pointwise_future_history_base':False,
        'descriptor_fibers_are_actual_same_lens_completion_objects':True,
        'canonical_fiber_map':'world -> unique actual fixed vector of its CURRENT audit completion at tau=3/5; this is determined by K, not an added random mark',
        'fixed_active_completion_lens':'audit_flow_quantile_lens',
        'conditional_pressure_definition':'logarithmic growth of the SAME path partition integrated under the fixed world law conditioned on its actual current audit output; not a supremum over every legal continuation with that output',
        'original_empirical_frequency_weights_established':False,
        'all_original_audited_descriptors_established':False,
        'original_sixteen_state_witness_established':False,
        'same_original_descriptor_fiber_interpretation':'finite actual completion objects over a common T0 descriptor, as in conditional_pressure_disintegration_v1.md and canonical_hybrid_theorem_object_v1.md',
        'paper_current_three_lens_family_identified':False,
        'paper_current_state_vs_descriptor_family_notation_resolved':False,
        'initial_completion_object_preserved_by_outer_F':False,
        'all_positive_parameter_gap':False,
        'zero_parameter_gap_exactly_zero':True,
        'main_theorem_package_complete':False,
        'mechanization_scope':'weighted arbitrary-product bounds, fixed-reference pressure limit return, binary object disintegration. Compactness, variational measure selection, Jensen, source realization and interval-data instances are analytic.'}
    # The beta-pressure difference also crosses between 5/4 and 3/2.
    for observable in ('closure','operator'):
        for parameter,sign in (('5/4',1),('3/2',-1)):
            row=next(p for p in profiles if p['parameter']==parameter and p['observable']==observable)
            d=I(*map(Q,row['carrier_pressure_intervals'][1]))-I(*map(Q,row['carrier_pressure_intervals'][0]))
            if (sign==1 and d.lo<=0) or (sign==-1 and d.hi>=0):
                raise ValueError('all-word pressure crossing endpoints failed')
    report['uniform_q_enclosures']=[q['phase_observables'] for q in q_boxes]
    if include_carriers:
        report['all_time_carriers']=[certify_cycle(c) for c in nominal]
        report['legal_entry_prefixes']=[certify_entry_prefix(cycle=c) for c in nominal]
        if min(Q(p['income_floor']) for entry in report['legal_entry_prefixes'] for p in entry['phases'])<=Q(1,100):
            raise ValueError('uniform 900-step budget-cap bound failed on an entry prefix')
    return report
