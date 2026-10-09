import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from context_flow_generation import audit_worker,identity


class GenerationInputTests(unittest.TestCase):
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
