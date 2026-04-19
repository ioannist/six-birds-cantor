import json
import unittest
from pathlib import Path


def mechanically_compatible(profile: dict, values: dict) -> bool:
    required = profile.get('required_assumptions', {})
    forbidden = profile.get('forbidden_assumptions', {})
    permitted_unknowns = set(profile.get('permitted_unknowns', []))

    for aid, expected in required.items():
        actual = values.get(aid)
        if actual == 'unknown' and aid in permitted_unknowns:
            continue
        if actual != expected:
            return False
    for aid, forbidden_value in forbidden.items():
        if values.get(aid) == forbidden_value:
            return False
    return True


class TheoremAssumptionsTest(unittest.TestCase):
    def test_assumption_pack_is_consistent(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        assumptions_path = repo_root / 'docs' / 'internal' / 'theorem_assumptions_v1.json'
        shortlist_path = repo_root / 'docs' / 'internal' / 'theorem_class_shortlist_v1.json'
        self.assertTrue(assumptions_path.exists())
        self.assertTrue(shortlist_path.exists())

        assumptions = json.loads(assumptions_path.read_text(encoding='utf-8'))
        shortlist = json.loads(shortlist_path.read_text(encoding='utf-8'))

        self.assertEqual(assumptions['primary_class_id'], 'safe_finite_memory_local_subclass')
        self.assertEqual(assumptions['stretch_class_id'], 'quasi_multiplicative_local_cantor_class')
        self.assertEqual(assumptions['primary_class_id'], shortlist['primary_class_id'])
        self.assertEqual(assumptions['stretch_class_id'], shortlist['stretch_class_id'])

        catalog = assumptions['assumption_catalog']
        allowed_values = {'yes', 'no', 'unknown'}
        profiles = {p['class_id']: p for p in assumptions['class_profiles']}
        for profile in profiles.values():
            for mapping_name in ['required_assumptions', 'forbidden_assumptions']:
                for aid, value in profile.get(mapping_name, {}).items():
                    self.assertIn(aid, catalog)
                    self.assertIn(value, allowed_values)
            for aid in profile.get('permitted_unknowns', []):
                self.assertIn(aid, catalog)

        family_tags = assumptions['family_assumption_tags']
        by_family = {entry['family_id']: entry for entry in family_tags}
        config_family_ids = set()
        for path in sorted((repo_root / 'configs' / 'experiments').rglob('*.json')):
            data = json.loads(path.read_text(encoding='utf-8'))
            config_family_ids.add(data['family_id'])
        self.assertEqual(set(by_family.keys()), config_family_ids)

        contextual_primary_ok = 0
        primary_profile = profiles[assumptions['primary_class_id']]
        for entry in family_tags:
            values = entry['assumption_values']
            for aid, value in values.items():
                self.assertIn(aid, catalog)
                self.assertIn(value, allowed_values)
            if entry['family_id'].startswith('contextual_local.') or entry['family_id'].startswith('toy.local_ifs.'):
                if mechanically_compatible(primary_profile, values):
                    contextual_primary_ok += 1
        self.assertGreaterEqual(contextual_primary_ok, 1)

        stage_dep = by_family['contextual_local.stage_dependent_alternating_removal']
        self.assertFalse(mechanically_compatible(primary_profile, stage_dep['assumption_values']))


if __name__ == '__main__':
    unittest.main()
