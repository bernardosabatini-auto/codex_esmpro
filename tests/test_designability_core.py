import tempfile,unittest
from pathlib import Path
import numpy as np
from designability_core import design_sequences,write_ca_pdb

class DesignTests(unittest.TestCase):
    def test_requires_all_sequences_and_skips_native(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'x.fa';p.write_text('>native\nAAAA\n'+''.join(f'>T=.1, sample={i}\nACDE\n' for i in range(8)))
            self.assertEqual(design_sequences(p,4),['ACDE']*8)
            p.write_text(p.read_text().rsplit('>T=',1)[0])
            with self.assertRaises(ValueError):design_sequences(p,4)
    def test_ca_pdb_roundtrip_and_nonfinite_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'x.pdb';x=np.arange(12).reshape(4,3).astype(float);write_ca_pdb(p,x)
            y=np.array([[float(s[a:a+8]) for a in (30,38,46)] for s in p.read_text().splitlines() if s.startswith('ATOM')]);np.testing.assert_allclose(y,x-x.mean(0))
            x[0,0]=float('nan')
            with self.assertRaises(ValueError):write_ca_pdb(p,x)

if __name__=='__main__':unittest.main()
