import unittest
import numpy as np
from latentfold.fragment_frame import anchor_backbone


class FragmentFrameTests(unittest.TestCase):
    def setUp(self):
        rng=np.random.default_rng(17);self.bb=rng.normal(size=(12,4,3));q,_=np.linalg.qr(rng.normal(size=(3,3)))
        if np.linalg.det(q)<0:q[:,0]*=-1
        self.expected=self.bb@q+np.array([3,7,-1]);self.fragment=self.expected[3:9].copy()

    def test_one_global_transform_preserves_scaffold_and_fragment(self):
        actual=anchor_backbone(self.bb,self.fragment,3);np.testing.assert_allclose(actual,self.expected,atol=1e-6)
        rot=np.array([[0,-1,0],[1,0,0],[0,0,1]]);other=anchor_backbone(self.bb@rot+11,self.fragment,3);np.testing.assert_array_equal(actual,other)

    def test_reflection_and_changed_backbone_atom_rejected(self):
        mirrored=self.fragment.copy();mirrored[...,0]*=-1
        with self.assertRaises(ValueError):anchor_backbone(self.bb,mirrored,3)
        changed=self.fragment.copy();changed[0,0,0]+=.1
        with self.assertRaises(ValueError):anchor_backbone(self.bb,changed,3)

    def test_invalid_placement_rejected(self):
        with self.assertRaises(ValueError):anchor_backbone(self.bb,self.fragment,9)


if __name__=='__main__':unittest.main()
