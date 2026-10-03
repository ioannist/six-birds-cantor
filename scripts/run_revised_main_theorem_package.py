#!/usr/bin/env python3
"""Bind the adopted revised target to its mathematical evidence.

This manifest records scope and proof dependencies. It does not infer a
theorem from boolean flags, or upgrade analytic proofs to full mechanizations.
"""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys


def check_lean(root):
    """Run the current build and inspect every requested transitive axiom list."""
    build = subprocess.run(['lake', 'build'], cwd=root/'lean',
                           capture_output=True, text=True, check=True)
    audit = subprocess.run(['lake', 'env', 'lean', 'AxiomAudit.lean'], cwd=root/'lean',
                           capture_output=True, text=True, check=True)
    requested = re.findall(r'^#print axioms (\S+)$',
                           (root/'lean/AxiomAudit.lean').read_text(), re.MULTILINE)
    observed = re.findall(r"^'([^']+)' (?:does not depend on any axioms|depends on axioms:\s*\[([^\]]*)\])",
                          audit.stdout, re.MULTILINE)
    if [name for name, _ in observed] != requested:
        raise ValueError('axiom audit does not cover exactly the requested declarations')
    allowed = {'propext', 'Classical.choice', 'Quot.sound'}
    dependencies = {}
    for name, raw in observed:
        axioms = sorted(a.strip() for a in raw.split(',') if a.strip())
        if set(axioms)-allowed:
            raise ValueError(f'unapproved transitive axioms in {name}: {axioms}')
        dependencies[name] = axioms
    return {'build_command': ['lake', 'build'], 'build_exit_code': build.returncode,
            'audit_command': ['lake', 'env', 'lean', 'AxiomAudit.lean'],
            'audit_exit_code': audit.returncode,
            'audited_declaration_count': len(observed),
            'transitive_axioms': dependencies,
            'allowed_foundations': sorted(allowed),
            'full_physical_source_formalization_inferred': False}


def run():
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / 'src'))
    sys.path.insert(0, str(root))
    from scripts.run_common_input_disintegration_obstruction import current_receipt, exact_warm_checks
    from scripts.generate_twenty_state_data import render
    if (root / 'lean/TwentyStateData.lean').read_text() != render():
        raise ValueError('Lean candidate data do not match the current original constructor')
    receipt_paths = ('results/controlled_original_shell/report.json',
                     'results/all_word_pressure_disintegration/report.json',
                     'results/common_input_disintegration_obstruction/report.json')
    bound = {}
    for path in receipt_paths:
        _, digest = current_receipt(root, path)
        bound[path] = digest
    _, warm = exact_warm_checks()
    validation = check_lean(root)
    report = {
        'revision': 'adopted_revised_main_package_2026_10_03',
        'manuscript_edited': False,
        'definition_source': 'docs/internal/revised_main_theorem_package_2026_10_03.md',
        'main_claim': 'a lawful controlled growth theory has a strict retentive completion-object extension even through its complete stated finite-horizon growth observations',
        'theorems': [
            {'id': 'R1', 'statement': 'explicit lawful continuous controlled shell',
             'proof': 'original-formula analytic return plus exact outward interval coverage and induction',
             'lean_scope': 'normalization, timescale, budget and iteration return lemmas',
             'instance_receipt': receipt_paths[0]},
            {'id': 'R2', 'statement': 'multiplicative history pressure exists, is Lipschitz and strictly decreasing, with unique root in (1/3,1)',
             'proof': 'source branch bounds, invariant-domain submultiplicativity and derived secants/anchors',
             'lean_scope': 'matrix_pressure_exists, pressure comparison/regularity and controlled_shell_pressure_root',
             'instance_receipt': receipt_paths[0]},
            {'id': 'R3', 'statement': 'actual current completion object does not factor through the specified complete growth description',
             'proof': 'exact twenty-state B Q U stationary objects plus legal all-time warm-state realization and identical base observations',
             'lean_scope': 'TwentyStateWitness checks the concrete rational completion and the matrix observation split; source realization remains analytic',
             'instance_receipt': receipt_paths[1]},
            {'id': 'R4', 'statement': 'distinct completion objects have identical history norms for every horizon and original pressure parameter under common lawful continuations',
             'proof': 'labelled row permutations, supported first-matrix difference, common second-matrix rows and arbitrary suffix multiplication',
             'lean_scope': 'concrete twenty-state weighted-row/history return and nonfactorization',
             'instance_receipt': receipt_paths[2]},
        ],
        'secondary_positive_gap_example': {
            'status': 'constructed fixed-reference-law existence example',
            'receipt': receipt_paths[1],
            'strictness_alone_entails_gap': False,
            'same_main_complete_growth_base_fiber': False,
            'independent_original_noise_law_identified': False,
        },
        'supporting_finite_pressure_formula': {
            'lean_source': 'lean/FiniteDisintegration.lean',
            'formula': 'P_reference=max_i P_i; gap=sum_i w_i(max_j P_j-P_i)',
            'scope': 'one fixed finite positive-mass fiber family, one law, one potential, existing conditional limits',
            'interpretation': 'growth-rate dispersion, not complete predictive sufficiency',
        },
        'completion_meaning': 'unique stationary vector and all-start convergence under each fixed E; not outer-F preservation',
        'retained_base': 'configuration, current controls/lens, diagonal/support/U, both entire finite-horizon growth-norm profiles',
        'forgotten_base_information': 'labelled off-diagonal K and raw innovation word',
        'old_manuscript_universal_pressure_implication_retained': False,
        'old_rounded_multifiber_interpretation_retained': False,
        'seeded_reachability_or_uncontrolled_noise_invariance_claimed': False,
        'hausdorff_dimension_identity_claimed': False,
        'full_lean_source_model_formalized': False,
        'scope_revision_is_user_adopted': True,
        'source_data_regeneration_matches': True,
        'warm_exact_checks': warm,
        'receipt_sha256': bound,
        'fresh_lean_validation': validation,
    }
    inputs = ['scripts/run_revised_main_theorem_package.py',
              'scripts/generate_twenty_state_data.py',
              'docs/internal/revised_main_theorem_package_2026_10_03.md',
              'lean/TwentyStateData.lean', 'lean/TwentyStateWitness.lean',
              'lean/README.md', 'lean/lakefile.lean', 'lean/lean-toolchain',
              'lean/lake-manifest.json']
    inputs = sorted(set(inputs) | {str(p.relative_to(root)) for p in (root/'lean').glob('*.lean')})
    report['input_sha256'] = {p: hashlib.sha256((root/p).read_bytes()).hexdigest() for p in inputs}
    out = root / 'docs/internal/revised_main_theorem_package_2026_10_03.json'
    out.write_text(json.dumps(report, indent=2, sort_keys=True)+'\n')
    print('wrote', out.relative_to(root))


if __name__ == '__main__':
    run()
