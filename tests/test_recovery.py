import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from summarize_recovery import validate_pair


class RecoveryContractTests(unittest.TestCase):
    def setUp(self):
        self.control=dict(status='complete',steps=500,config=dict(learning_rate=1e-5),
            task=dict(seed=7919,arm='flow'),rows=[dict(step=1,bucket=128,batch=128,flow_rng_sha256='rng',input_ids_sha256='ids')])
        self.trained=copy.deepcopy(self.control)
        self.trained['task'].update(name='optimizer_beta',overrides={'optimizer_betas':[.9,.95]})
        self.trained['config']['optimizer_betas']=[.9,.95]
        self.trained['gradient_controls']=[dict(passed=True) for _ in range(4)]

    def test_single_factor_and_matched_rng(self):
        validate_pair(self.trained,self.control)
        self.trained['rows'][0]['flow_rng_sha256']='different'
        with self.assertRaises(ValueError):validate_pair(self.trained,self.control)

    def test_unrecorded_learning_rate_change_rejected(self):
        self.trained['config']['learning_rate']=1e-4
        with self.assertRaises(ValueError):validate_pair(self.trained,self.control)

    def test_broader_pool_allows_new_ids_but_not_new_draws(self):
        t=copy.deepcopy(self.control);t['gradient_controls']=[dict(passed=True) for _ in range(4)]
        changes=dict(training_manifest='expanded',training_manifest_sha256='hash')
        t['task'].update(name='broader_training_pool',overrides=changes);t['config'].update(changes)
        t['rows'][0]['input_ids_sha256']='new ids'
        validate_pair(t,self.control)
        t['rows'][0]['batch']=64
        with self.assertRaises(ValueError):validate_pair(t,self.control)
