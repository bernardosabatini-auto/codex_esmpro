import copy,hashlib,json,tempfile,unittest
from pathlib import Path
from compare_retrieved_context_refolds import gate
from retrieved_context_refolding import audit_worker
from context_flow_generation import identity
from prepare_overfit import sha


class RetrievalRefoldingTests(unittest.TestCase):
    def test_strict_gain_cannot_hide_designability_loss(self):
        totals=dict(parent6000=dict(strong=8,strong_families=7,designable=45),
                    random=dict(strong=0,strong_families=0,designable=50),
                    retrieved=dict(strong=12,strong_families=9,designable=49))
        self.assertFalse(gate(totals)['designability'])
        totals['retrieved']['designable']=50
        self.assertTrue(all(gate(totals).values()))
        totals['random']['strong']=12
        self.assertFalse(gate(totals)['strict'])

    def test_sparse_success_and_changed_baseline_fail(self):
        totals=dict(parent6000=dict(strong=8,strong_families=7,designable=45),
                    random=dict(strong=0,strong_families=0,designable=40),
                    retrieved=dict(strong=12,strong_families=6,designable=50))
        self.assertFalse(gate(totals)['families'])
        totals['parent6000']['designable']=44
        with self.assertRaises(ValueError):gate(totals)

    def test_worker_certificate_rejects_config_or_file_changes(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'input';p.write_text('original')
            c=dict(retrieved_context_refold=True,assay='fragment_preference_refold',sources=[dict(path=str(p),sha256=sha(p))],file_identity=[identity(p)])
            c['config_sha256']=hashlib.sha256(json.dumps(c,sort_keys=True).encode()).hexdigest()
            audit_worker(c)
            bad=copy.deepcopy(c);bad['arm']='changed'
            with self.assertRaises(ValueError):audit_worker(bad)
            p.write_text('different')
            with self.assertRaises(ValueError):audit_worker(c)


if __name__=='__main__':unittest.main()
