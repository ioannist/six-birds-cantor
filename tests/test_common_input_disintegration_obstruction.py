from fractions import Fraction as Q
from itertools import product
from pathlib import Path
import json

import pytest

from contextual_cantor.original_loop_extension import exact_fixed_half_join
from contextual_cantor.packaged_world_disintegration import construct_packaged_world_law
from scripts.run_common_input_disintegration_obstruction import exact_warm_checks,current_receipt


def test_actual_finite_conditional_paths_differ_despite_common_history_norm():
    w,proof=exact_warm_checks()
    r=exact_fixed_half_join(w,Q(79,100)).common_kernel
    values=[]
    for z,k in enumerate(w.kernels):
        # Factor out the SAME original exp(-2*(q0+q1)) scalar. The remaining
        # literal original-K path integral has this exact rational coefficient.
        value=sum(w.audit[z].stationary[i]*k[i][j]*r[j][h]
                  *(k[i][j]**2/k[i][j])*(r[j][h]**2/r[j][h])
                  for i,j,h in product(range(20),repeat=3))
        assert value==Q(proof['two_step_unscaled_partitions'][z])
        values.append(value)
    assert values[0]!=values[1]
    for weight in (Q(1,7),Q(5,8)):
        law=construct_packaged_world_law(weight)
        assert law.conditional(values,law.objects[0])!=law.conditional(values,law.objects[1])
        assert sum(law.mass(o)*law.conditional(values,o) for o in law.objects)==law.expectation(values)
    assert values[0]-values[1]==Q(proof['two_step_unscaled_partition_difference'])


def test_source_receipt_binding_rejects_changed_inputs(tmp_path):
    root=Path(__file__).resolve().parents[1]
    _,digest=current_receipt(root,'results/all_word_pressure_disintegration/report.json')
    assert len(digest)==64
    source=tmp_path/'source.txt'
    source.write_text('changed source')
    receipt=tmp_path/'receipt.json'
    receipt.write_text(json.dumps({'input_sha256':{'source.txt':'0'*64}}))
    with pytest.raises(ValueError,match='stale input receipt'):
        current_receipt(tmp_path,'receipt.json')
