#!/usr/bin/env python3
"""Export the actual rational warm witness for Lean's kernel to check.

The tables are candidate data, not trusted proofs. TwentyStateWitness.lean
checks their stochasticity, B Q U interpretation and stationary identities.
"""
from pathlib import Path
import sys


def render():
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / 'src'))
    from fractions import Fraction as Q
    from contextual_cantor.original_loop_extension import (
        construct_original_loop_extension, exact_fixed_half_join,
    )
    w = construct_original_loop_extension()
    special = [(i, j, v) for i, row in enumerate(w.kernels[0])
               for j, v in enumerate(row) if v != w.kernels[0][19][19]]
    lines = [
        'import LoopExtension', 'import PrimitiveCompletion', '',
        '/-! Generated rational candidate data; independently checked in',
        'TwentyStateWitness.lean. Regenerate with scripts/generate_twenty_state_data.py. -/',
        'namespace CantorAudit', '',
        'def warmForward (i j : Fin 20) : ℚ :=',
    ]
    lines += [f'  if i.val = {i} ∧ j.val = {j} then {v.numerator}/{v.denominator} else'
              for i, j, v in special]
    lines += ['  1/20', '',
              'def warmKernel (z : Bool) (i j : Fin 20) : ℚ :=',
              '  if z then warmForward j i else warmForward i j', '',
              'def warmAuditCore (i : Fin 20) : Prop :=',
              '  i.val = 0 ∨ i.val = 4 ∨ i.val = 5 ∨ i.val = 6 ∨ i.val = 7', '',
              'instance (i : Fin 20) : Decidable (warmAuditCore i) :=',
              '  inferInstanceAs (Decidable (_ ∨ _ ∨ _ ∨ _ ∨ _))', '',
              'def warmPrototype (j : Fin 20) : ℚ :=',
              '  (55/100)*(1/20)+(25/100)*((1/20+warmForward j j)/2)',
              '    +(20/100)*warmForward j j', '',
              'def warmCoreMass : ℚ := ∑ j, if warmAuditCore j then warmPrototype j else 0',
              'def warmOtherMass : ℚ := ∑ j, if warmAuditCore j then 0 else warmPrototype j', '',
              'def warmCoreCoefficient (z : Bool) : Fin 20 → ℚ :=', '  if z then']
    coefficients = [tuple(sum(row[j] for j in w.audit[z].groups[0])
                          for row in w.audit[z].transport) for z in (0, 1)]
    join = exact_fixed_half_join(w, Q(159, 200)).common_kernel
    inside, outside = join[0][0], join[0][10]
    if any(join[i][j] != (inside if (i < 10) == (j < 10) else outside)
           for i in range(20) for j in range(20)):
        raise ValueError('the source join is not the represented two-half matrix')
    lines += ['    ![' + ', '.join(str(x) for x in coefficients[1]) + ']', '  else',
              '    ![' + ', '.join(str(x) for x in coefficients[0]) + ']', '',
              'def warmAuditObject (z : Bool) : Fin 20 → ℚ :=', '  if z then',
              '    ![' + ', '.join(str(x) for x in w.audit[1].stationary) + ']', '  else',
              '    ![' + ', '.join(str(x) for x in w.audit[0].stationary) + ']', '',
              'def warmCompletion (z : Bool) (i j : Fin 20) : ℚ :=',
              '  if warmAuditCore j then warmCoreCoefficient z i*(warmPrototype j/warmCoreMass)',
              '  else (1-warmCoreCoefficient z i)*(warmPrototype j/warmOtherMass)', '',
              'def warmJoin (i j : Fin 20) : ℚ :=',
              f'  if (i.val < 10) = (j.val < 10) then {inside} else {outside}', '',
              'end CantorAudit', '']
    return '\n'.join(lines)


if __name__ == '__main__':
    path = Path(__file__).resolve().parents[1] / 'lean/TwentyStateData.lean'
    path.write_text(render())
    print(f'wrote {path}')
