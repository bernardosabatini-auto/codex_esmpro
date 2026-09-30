import unittest
import torch
from latentfold.geometry import robust_distance, signed_local, revised_geometry

class GeometryTests(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(3)
        self.ref = torch.randn(2, 12, 3)*3
        self.mask = torch.ones(2, 12, dtype=torch.bool)
        self.adj = torch.ones(2, 11, dtype=torch.bool)

    def test_rigid_motion_and_mirror(self):
        q, _ = torch.linalg.qr(torch.randn(3,3))
        q[:, 0] *= torch.linalg.det(q)
        pred = self.ref@q+4
        self.assertLess(float(revised_geometry(pred,self.ref,self.mask,self.adj)[0]), 1e-5)
        mirror = self.ref.clone(); mirror[...,0] *= -1
        self.assertLess(float(robust_distance(mirror,self.ref,self.mask)), 1e-6)
        self.assertGreater(float(signed_local(mirror,self.ref,self.mask,self.adj)[0]), .01)

    def test_mask_and_missing_maps(self):
        pred = self.ref+.2*torch.randn_like(self.ref)
        self.mask[:,8:] = False
        before = revised_geometry(pred,self.ref,self.mask,self.adj)[0]
        pred[:,8:] += 1000
        self.assertAlmostEqual(float(before), float(revised_geometry(pred,self.ref,self.mask,self.adj)[0]), places=6)
        loss, count = signed_local(pred,self.ref,self.mask,torch.zeros_like(self.adj))
        self.assertEqual(count,0); self.assertEqual(float(loss),0)

    def test_gradient_reduces_large_error(self):
        pred = (self.ref*10).requires_grad_()
        loss = robust_distance(pred,self.ref,self.mask)
        grad, = torch.autograd.grad(loss,pred)
        self.assertTrue(torch.isfinite(grad).all()); self.assertGreater(float(grad.norm()),0)
        self.assertLess(float(robust_distance(pred-.1*grad,self.ref,self.mask)),float(loss))
