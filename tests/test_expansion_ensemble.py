import unittest
from prepare_expansion_ensemble import qualified,training_identity


class ExpansionEnsembleTests(unittest.TestCase):
    def test_training_identity_keeps_data_only_scope(self):
        c=dict(seed=2026100171,label_distribution='balanced',corpus_kind='expansion')
        training_identity(c,'seed2026100171_expansion')
        for changes in ({'seed':2026100181},{'corpus_kind':'old'},{'local_geometry':{'weight':1}},{'trainable_tail_blocks':4},{'label_distribution':'empirical'}):
            with self.assertRaises(ValueError):training_identity(dict(c,**changes),'seed2026100171_expansion')

    def test_quality_gate_requires_complete_both_seed_evidence(self):
        capacity=dict(step=500,matched=True,seeds=[2026100171,2026100181],training_targets=450)
        transfer=dict(step=500,training_targets=450,summaries={f'seed{s}_expansion_cfg1':dict(quality_passed=True) for s in capacity['seeds']})
        for s in capacity['seeds']:self.assertEqual(qualified(capacity,transfer,f'seed{s}_expansion',1),f'seed{s}_expansion_cfg1')
        transfer['summaries']['seed2026100171_expansion_cfg1']['quality_passed']=False
        with self.assertRaises(ValueError):qualified(capacity,transfer,'seed2026100171_expansion',1)
        with self.assertRaises(ValueError):qualified(dict(capacity,seeds=[2026100181]),transfer,'seed2026100181_expansion',1)
        with self.assertRaises(ValueError):qualified(capacity,dict(transfer,training_targets=122),'seed2026100181_expansion',1)


if __name__=='__main__':unittest.main()
