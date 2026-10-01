import unittest
import torch
from latentfold.backbone import canonical_backbone_frame


class FrameTests(unittest.TestCase):
    def test_rigid_invariance_and_geometry(self):
        generator=torch.Generator().manual_seed(8)
        x=torch.randn(2,20,4,3,generator=generator,dtype=torch.float64)
        q,_=torch.linalg.qr(torch.randn(3,3,generator=generator,dtype=torch.float64))
        q[:,2]*=torch.linalg.det(q)
        a=canonical_backbone_frame(x)
        b=canonical_backbone_frame(x@q+13)
        self.assertTrue(torch.allclose(a,b,atol=1e-10))
        def distances(z):
            return torch.cdist(z.flatten(1,2),z.flatten(1,2),compute_mode='donot_use_mm_for_euclid_dist')
        self.assertTrue(torch.allclose(distances(x),distances(a),atol=1e-10))
        def volume(z):
            v=z[:,0,1:]-z[:,0,:1]
            return torch.linalg.det(v)
        self.assertTrue(torch.allclose(volume(x),volume(a),atol=1e-10))

    def test_degenerate_anchor_rejected(self):
        with self.assertRaises(ValueError):
            canonical_backbone_frame(torch.zeros(1,10,4,3))
