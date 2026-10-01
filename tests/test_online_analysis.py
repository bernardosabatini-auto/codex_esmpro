import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from online_analysis import validate_online_pair
from summarize_pilot import geometry_by_target


class OnlineAnalysisTests(unittest.TestCase):
    def test_explicit_batch_change_preserves_all_other_provenance(self):
        reference = {k: k for k in ('checkpoint', 'decoder_checkpoint', 'dataset',
                    'embedding_artifacts', 'resident_parameters', 'timing_scope', 'precision')}
        reference['config'] = dict(seed=0, samples=3, target_ids=['a'], flow_steps=[25],
            guidance=[2], batches={'128':126, '256':63, '384':30, '512':30})
        candidate = copy.deepcopy(reference)
        candidate['config']['batches']['128'] = 189
        with self.assertRaisesRegex(ValueError, 'batches'):
            validate_online_pair(candidate, reference)
        validate_online_pair(candidate, reference, same_batches=False, same_precision=True)
        for scope, key in [('config', 'seed'), ('config', 'samples'), ('config', 'target_ids'),
                           (None, 'dataset'), (None, 'checkpoint'), (None, 'precision')]:
            broken = copy.deepcopy(candidate)
            (broken[scope] if scope else broken)[key] = 'changed'
            with self.assertRaises(ValueError):
                validate_online_pair(broken, reference, same_batches=False, same_precision=True)

    def test_geometry_never_mixes_sampling_settings(self):
        row = dict(target_id='a', setting='steps25_cfg2', reference_adjacent_short_count=10, gaps=2)
        self.assertEqual(geometry_by_target([row], 'gaps'), {'a':.2})
        with self.assertRaisesRegex(ValueError, 'one sampling setting'):
            geometry_by_target([row, dict(row, setting='steps10_cfg2', gaps=10)], 'gaps')


if __name__ == '__main__':
    unittest.main()
