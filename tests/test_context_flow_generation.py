import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from context_flow_generation import audit_worker,identity


class GenerationInputTests(unittest.TestCase):
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
