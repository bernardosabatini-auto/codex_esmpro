import json
from pathlib import Path
import unittest
import numpy as np
from latent_repair import accept,repair


class LatentRepairTests(unittest.TestCase):
    def setUp(self):
        self.p=json.loads((Path(__file__).resolve().parents[1]/'configs/latent_repair_protocol.json').read_text())
        self.bb=np.zeros((12,4,3),dtype=np.float32)
        self.bb[:,:,0]=np.arange(12)[:,None]*3.8+np.array([-1.2,0,1.26,2.0])

    def test_small_rigid_shift_preserves_geometry_but_large_shift_fails_bound(self):
        candidate=self.bb.copy();candidate[:,:,1]+=.03
        self.assertTrue(accept(self.bb,candidate,self.p['acceptance'])[0])
        candidate[:,:,1]+=.5
        passed,details=accept(self.bb,candidate,self.p['acceptance'])
        self.assertFalse(passed);self.assertFalse(details['gates']['bounded'])

    def test_atom_distortion_and_nonfinite_output_rejected(self):
        candidate=self.bb.copy();candidate[4,3,0]+=.08
        passed,details=accept(self.bb,candidate,self.p['acceptance'])
        self.assertFalse(passed);self.assertFalse(details['gates']['intraresidue_preserved'])
        candidate[0,0,0]=np.nan
        self.assertFalse(accept(self.bb,candidate,self.p['acceptance'])[0])

    def test_valid_input_is_bitwise_unchanged_without_decoder_or_noise_access(self):
        output,diag=repair(None,None,None,None,self.bb,self.p)
        self.assertTrue(np.array_equal(output,self.bb));self.assertIsNot(output,self.bb)
        self.assertEqual(diag['status'],'unchanged_valid')


if __name__=='__main__':unittest.main()
