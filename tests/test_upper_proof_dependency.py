import json
import unittest
from pathlib import Path


class UpperProofDependencyTest(unittest.TestCase):
    def test_dependency_json_is_consistent(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        dep_path = repo_root / 'docs' / 'internal' / 'proof_dependency_upper_v1.json'
        assumptions_path = repo_root / 'docs' / 'internal' / 'theorem_assumptions_v1.json'
        self.assertTrue(dep_path.exists())
        self.assertTrue(assumptions_path.exists())

        dep = json.loads(dep_path.read_text(encoding='utf-8'))
        assumptions = json.loads(assumptions_path.read_text(encoding='utf-8'))
        assumption_ids = set(assumptions['assumption_catalog'].keys())

        self.assertEqual(dep['class_id'], assumptions['primary_class_id'])
        for aid in dep['assumptions_used']:
            self.assertIn(aid, assumption_ids)

        allowed_status = {'closed_in_note', 'standard_external', 'localized_gap'}
        lemmas = dep['lemmas']
        lemma_ids = {lemma['lemma_id'] for lemma in lemmas}
        for lemma in lemmas:
            self.assertIn(lemma['status'], allowed_status)
            for aid in lemma['assumptions_used']:
                self.assertIn(aid, assumption_ids)
            for dep_id in lemma['depends_on']:
                self.assertIn(dep_id, lemma_ids)

        theorem_node = next(lemma for lemma in lemmas if lemma['lemma_id'] == 'THM-UPPER-1')
        self.assertEqual(set(theorem_node['depends_on']), {'LEM-UPPER-1', 'LEM-UPPER-2', 'LEM-UPPER-3', 'LEM-UPPER-4'})
        self.assertTrue(dep['witness_families'])


if __name__ == '__main__':
    unittest.main()
