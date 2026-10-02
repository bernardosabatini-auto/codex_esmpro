import unittest
import numpy as np
from latentfold.fragment_designability import motif_fit,same_refold_success


class SameRefoldTests(unittest.TestCase):
    def test_separate_successful_sequences_do_not_combine(self):
        raw=dict(coarse_valid=True,motif_drms=.2,motif_ca_rmsd=.2)
        rows=[dict(coarse_valid=True,sc_tm=.8,motif_drms=2.,motif_ca_rmsd=2.),dict(coarse_valid=True,sc_tm=.3,motif_drms=.2,motif_ca_rmsd=.2)]
        result=same_refold_success(raw,rows)
        self.assertFalse(result['strict_joint_success']);self.assertTrue(result['valid_designable']);self.assertEqual(result['successful_refold_indices'],[])
        rows.append(dict(coarse_valid=True,sc_tm=.8,motif_drms=.2,motif_ca_rmsd=.2));result=same_refold_success(raw,rows)
        self.assertTrue(result['strict_joint_success']);self.assertEqual(result['successful_refold_indices'],[2])
        raw['coarse_valid']=False;self.assertFalse(same_refold_success(raw,rows)['strict_joint_success'])

    def test_mirror_does_not_pass_proper_rotation_motif_check(self):
        rng=np.random.default_rng(31);ref=rng.normal(size=(20,4,3))*5;mirror=ref.copy();mirror[...,0]*=-1;fit=motif_fit(mirror,ref,0)
        self.assertLess(fit['motif_drms'],1e-12);self.assertGreater(fit['motif_ca_rmsd'],1)
        raw=dict(coarse_valid=True,motif_drms=0.,motif_ca_rmsd=0.);r=dict(coarse_valid=True,sc_tm=.8,**fit);result=same_refold_success(raw,[r]);self.assertFalse(result['strict_joint_success']);self.assertTrue(result['legacy_drms_joint_success'])
        rot=np.array([[0,-1,0],[1,0,0],[0,0,1]]);fit=motif_fit(ref@rot+11,ref,0);self.assertLess(fit['motif_ca_rmsd'],1e-10)

    def test_invalid_measurements_fail(self):
        raw=dict(coarse_valid=True,motif_drms=0.,motif_ca_rmsd=0.)
        with self.assertRaises(ValueError):same_refold_success(raw,[])
        with self.assertRaises(ValueError):same_refold_success(raw,[dict(raw,sc_tm=float('nan'))])

if __name__=='__main__':unittest.main()
