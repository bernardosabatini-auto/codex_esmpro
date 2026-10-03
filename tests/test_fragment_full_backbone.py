import tempfile,unittest
from pathlib import Path
import numpy as np
from designability_core import write_backbone_pdb,write_ca_pdb


class BackboneInterchangeTests(unittest.TestCase):
    def test_all_atoms_and_ca_coordinates_survive_pdb_interchange(self):
        bb=np.random.default_rng(4).normal(size=(11,4,3))*10+np.array([100,200,-50])
        with tempfile.TemporaryDirectory() as tmp:
            full=Path(tmp)/'full.pdb';ca=Path(tmp)/'ca.pdb';write_backbone_pdb(full,bb);write_ca_pdb(ca,bb[:,1])
            lines=[s for s in full.read_text().splitlines() if s.startswith('ATOM')]
            self.assertEqual(len(lines),44)
            self.assertEqual([s[12:16].strip() for s in lines],['N','CA','C','O']*11)
            self.assertEqual([int(s[22:26]) for s in lines],np.repeat(np.arange(1,12),4).tolist())
            self.assertTrue(all(s[17:20]=='ALA' and s[21]=='A' for s in lines))
            xyz=np.array([[float(s[k:k+8]) for k in (30,38,46)] for s in lines]).reshape(bb.shape)
            np.testing.assert_allclose(xyz,bb-bb[:,1].mean(0),rtol=0,atol=.00051)
            full_ca=[s[30:54] for s in lines if s[12:16].strip()=='CA']
            old_ca=[s[30:54] for s in ca.read_text().splitlines() if s.startswith('ATOM')]
            self.assertEqual(full_ca,old_ca)
            with self.assertRaises(ValueError):write_backbone_pdb(full,bb[:,:,:2])
            bb[0,0,0]=float('nan')
            with self.assertRaises(ValueError):write_backbone_pdb(full,bb)
