import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from context_flow_generation import audit_worker,identity


class GenerationInputTests(unittest.TestCase):
    def test_local_staging_checks_bytes_and_sidecar(self):
        from local_checkpoint import stage_checkpoint
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);p=root/'model.pt';p.write_bytes(b'checkpoint')
            sidecar=Path(str(p)+'.meta.json');sidecar.write_text('{}')
            sources=[dict(path=str(x),sha256=hashlib.sha256(x.read_bytes()).hexdigest()) for x in (p,sidecar)]
            staged=stage_checkpoint(p,sources,root/'local')
            self.assertEqual(staged.read_bytes(),p.read_bytes())
            self.assertEqual(Path(str(staged)+'.meta.json').read_bytes(),sidecar.read_bytes())
            with self.assertRaises(ValueError):stage_checkpoint(p,sources[:1],root/'unbound')
            p.write_bytes(b'changed')
            with self.assertRaises(ValueError):stage_checkpoint(p,sources,root/'changed')

    def test_random_retrieval_ignores_geometry_and_keeps_families_distinct(self):
        from retrieved_context_profile import random_donors
        rows=[dict(id=str(i),family=str(i//2),length=100,bucket=128) for i in range(16)]
        a=random_donors(rows,dict(id='query',bucket=128),3)
        b=random_donors(list(reversed(rows)),dict(id='query',bucket=128,geometry='ignored'),3)
        self.assertEqual(a,b);self.assertEqual(len({r['family'] for r in a}),4)
        self.assertTrue(all(0<=r['start']<=80 for r in a))

    def test_window_search_bound_matches_bruteforce(self):
        import numpy as np
        from diagnose_context_retrieval import proper_distances
        from diagnose_context_windows import PAIR,rank,update_neighbors
        rng=np.random.default_rng(12);query=rng.normal(size=(20,3))
        qd=np.linalg.norm(query[PAIR[0]]-query[PAIR[1]],axis=-1);top={};exhaustive={}
        for i in range(12):
            family=str(i%6);donor=dict(id=str(i),family=family,length=24,bucket=128)
            ca=rng.normal(size=(24,3));windows=np.lib.stride_tricks.sliding_window_view(ca,20,axis=0).transpose(0,2,1)
            distances=np.linalg.norm(windows[:,PAIR[0]]-windows[:,PAIR[1]],axis=-1)
            top=update_neighbors(top,windows,distances,donor,query,qd)
            rms=proper_distances(windows,query);drms=np.sqrt(np.mean((distances-qd)**2,axis=1)*.95)
            candidate=min([dict(**donor,start=j,ca_rmsd=float(rms[j]),drms=float(drms[j]),score=float(max(rms[j],drms[j]))) for j in range(5)],key=rank)
            if family not in exhaustive or rank(candidate)<rank(exhaustive[family]):exhaustive[family]=candidate
        self.assertEqual(sorted(top.values(),key=rank),sorted(exhaustive.values(),key=rank)[:4])

    def test_retrieval_alignment_is_proper(self):
        import numpy as np
        from diagnose_context_retrieval import proper_distances
        x=np.random.default_rng(9).normal(size=(20,3))
        q,_=np.linalg.qr(np.random.default_rng(8).normal(size=(3,3)))
        q[:,0]*=np.linalg.det(q)
        moved=x@q+5;mirror=x.copy();mirror[:,0]*=-1
        d=proper_distances(np.stack([x,moved,mirror]),x)
        self.assertLess(float(d[:2].max()),1e-12)
        self.assertGreater(d[2],.1)

    def test_projection_matches_independent_population_normalization(self):
        import numpy as np
        import torch
        from context_normalization_profile import project
        x=np.random.default_rng(5).normal(size=(4,20,8)).astype(np.float32)
        expected=(x-x.mean(-1,keepdims=True))/np.sqrt(x.var(-1,keepdims=True)+1e-5)
        actual=project(torch.from_numpy(x)).numpy()
        np.testing.assert_allclose(actual,expected,atol=5e-7,rtol=5e-7)
        with self.assertRaises(ValueError):project(torch.zeros(4,20,8))
        broken=x.copy();broken[0,0,0]=float('nan')
        with self.assertRaises(ValueError):project(torch.from_numpy(broken))

    def config(self,p):
        c=dict(sources=[dict(path=str(p))],file_identity=[identity(p)],seed=2026100405)
        c['config_sha256']=hashlib.sha256(json.dumps(c,sort_keys=True).encode()).hexdigest()
        return c

    def test_configuration_and_input_mutations_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'weights';p.write_bytes(b'original')
            c=self.config(p);audit_worker(c)
            altered=dict(c,seed=2)
            with self.assertRaises(ValueError):audit_worker(altered)
            p.write_bytes(b'replaced contents')
            with self.assertRaises(ValueError):audit_worker(c)


if __name__=='__main__':unittest.main()
