import unittest
from prepare_local_geometry_ensemble import qualified,training_identity

class GeometryEnsembleTests(unittest.TestCase):
    def test_training_identity(self):
        c=dict(seed=2026100171,label_distribution='balanced',local_geometry={'weight':1.})
        training_identity(c,'seed2026100171_geometry')
        for changes in ({'seed':2026100181},{'local_geometry':None},{'trainable_tail_blocks':4},{'label_distribution':'empirical'}):
            with self.assertRaises(ValueError):training_identity(dict(c,**changes),'seed2026100171_geometry')
    def fixture(self):
        return (dict(step=500,matched=True,seeds=[2026100171,2026100181]),dict(step=500,geometry_effects={},summaries={f'seed{s}_geometry_cfg1':dict(quality_passed=True) for s in (2026100171,2026100181)}))
    def test_declared_native_gate_with_complete_paired_evidence(self):
        c,t=self.fixture()
        for seed in c['seeds']:self.assertEqual(qualified(c,t,f'seed{seed}_geometry',1),f'seed{seed}_geometry_cfg1')
    def test_incomplete_pair_quality_failure_wrong_setting_rejected(self):
        for mode in ('seed','quality','endpoint','head','guidance','scope'):
            c,t=self.fixture();head='seed2026100171_geometry';guidance=1
            if mode=='seed':c['seeds'].pop()
            if mode=='quality':t['summaries'][head+'_cfg1']['quality_passed']=False
            if mode=='endpoint':t['step']=2000
            if mode=='head':head='seed2026100171_full'
            if mode=='guidance':guidance=2
            if mode=='scope':t.pop('geometry_effects')
            with self.subTest(mode=mode),self.assertRaises(ValueError):qualified(c,t,head,guidance)

if __name__=='__main__':unittest.main()
