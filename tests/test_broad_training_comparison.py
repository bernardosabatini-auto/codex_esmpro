import copy
import unittest
from compare_broad_fragment_training import compare_traces


class BroadTraceTests(unittest.TestCase):
    def test_only_between_corpus_ids_may_differ(self):
        row = dict(step=1, length=128, batch=64, learning_rate_factor=.1, self_conditioned=True,
                   noise_sha256='n', time_sha256='t', drop_sha256='d', rng_sha256='r', global_rng_sha256='g',
                   ids=['a'], conditions=['c20_center'])
        models = {}
        for corpus in ('control512', 'broad'):
            for obj in ('weighted', 'balanced'):
                trace = copy.deepcopy(row)
                if corpus == 'broad':
                    trace['ids'] = ['b']
                models[corpus + obj] = dict(config=dict(corpus=corpus), training=[trace])
        self.assertEqual(compare_traces(models), 1)
        for key in ('ids', 'conditions', 'noise_sha256'):
            changed = copy.deepcopy(models)
            changed['broadbalanced']['training'][0][key] = ['other'] if key != 'noise_sha256' else 'other'
            with self.assertRaises(ValueError):
                compare_traces(changed)
