import unittest
import numpy as np
from fragment_teacher_augmentation_core import qualifying_states,maximum_scaffold_difference


class TeacherEndpointTests(unittest.TestCase):
    def backbone(self):
        bb=np.zeros((16,4,3));bb[:,:,0]=np.arange(16)[:,None]*3.8;bb[:,0,0]-=1.3;bb[:,2,0]+=1.2;bb[:,3,1]=1.;return bb

    def test_bad_geometry_is_rejected_despite_exact_fragment(self):
        bb=self.backbone();decoded=np.stack([bb,bb]);decoded[1,0,:,1]+=10
        accepted,rows=qualifying_states(decoded,np.stack([bb,bb]),bb[5:11],5,[0,1])
        self.assertEqual(accepted,[0]);self.assertLess(rows[1]['motif_ca_rmsd'],1e-6);self.assertFalse(rows[1]['coarse_valid'])

    def test_rigid_pose_is_not_scaffold_diversity(self):
        bb=self.backbone();rotation=np.array([[0,-1,0],[1,0,0],[0,0,1]])
        pair=np.stack([bb,bb@rotation+7])
        self.assertLess(maximum_scaffold_difference(pair,[0,1],5,6),1e-6)
        self.assertIsNone(maximum_scaffold_difference(pair,[0],5,6))


if __name__=='__main__':unittest.main()
