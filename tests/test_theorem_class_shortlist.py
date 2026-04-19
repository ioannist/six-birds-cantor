import json
import unittest
from pathlib import Path


class TheoremClassShortlistTest(unittest.TestCase):
    def test_shortlist_is_complete_and_valid(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        shortlist_path = repo_root / 'docs' / 'internal' / 'theorem_class_shortlist_v1.json'
        self.assertTrue(shortlist_path.exists())
        shortlist = json.loads(shortlist_path.read_text(encoding='utf-8'))

        candidate_classes = shortlist.get('candidate_classes', [])
        primary = [c for c in candidate_classes if c.get('selection_status') == 'primary']
        stretch = [c for c in candidate_classes if c.get('selection_status') == 'stretch']
        self.assertEqual(len(primary), 1)
        self.assertEqual(len(stretch), 1)

        allowed = {'in', 'out', 'unknown'}
        memberships = shortlist.get('family_membership', [])
        self.assertTrue(memberships)
        by_family = {entry['family_id']: entry for entry in memberships}

        config_family_ids = set()
        for path in sorted((repo_root / 'configs' / 'experiments').rglob('*.json')):
            data = json.loads(path.read_text(encoding='utf-8'))
            config_family_ids.add(data['family_id'])
        self.assertEqual(set(by_family.keys()), config_family_ids)

        primary_id = shortlist['primary_class_id']
        contextual_primary_in = 0
        for family_id, entry in by_family.items():
            membership = entry.get('candidate_membership', {})
            for value in membership.values():
                self.assertIn(value, allowed)
            if family_id.startswith('contextual_local.') or family_id.startswith('toy.local_ifs.'):
                if membership.get(primary_id) == 'in':
                    contextual_primary_in += 1
        self.assertGreaterEqual(contextual_primary_in, 1)


if __name__ == '__main__':
    unittest.main()
