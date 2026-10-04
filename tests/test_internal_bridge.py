import unittest
import numpy as np
import torch
from latentfold.internal_bridge import internal,place,InternalBridge
from latentfold.local_closure import geometry_audit


class InternalBridgeTests(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(7401)
        self.x=torch.randn(12,4,3,dtype=torch.float64)*3
        self.bridge=InternalBridge(self.x,2,10)
        self.zero=torch.zeros(self.bridge.n_torsions,dtype=torch.float64)

    def test_roundtrip_arbitrary_nondegenerate_coordinates(self):
        output,residual=self.bridge.assemble(self.x,self.zero)
        torch.testing.assert_close(output,self.x,rtol=0,atol=2e-12)
        torch.testing.assert_close(residual,torch.zeros_like(residual),rtol=0,atol=2e-12)

    def test_torsions_preserve_local_lengths_angles_omega_and_carbonyls(self):
        delta=torch.linspace(-.4,.3,len(self.zero),dtype=torch.float64)
        moving,endpoint=self.bridge.reconstruct(self.x,delta)
        spine=torch.cat((self.x[1:2,:3],moving[:,:3],endpoint[None])).reshape(-1,3)
        ref=self.x[1:11,:3].reshape(-1,3)
        out=internal(spine[:-3],spine[1:-2],spine[2:-1],spine[3:])
        target=internal(ref[:-3],ref[1:-2],ref[2:-1],ref[3:])
        for j in (0,1):torch.testing.assert_close(out[j],target[j],rtol=0,atol=2e-12)
        torch.testing.assert_close(torch.cos(out[2][1::3]),torch.cos(target[2][1::3]),rtol=0,atol=2e-12)
        torch.testing.assert_close(torch.sin(out[2][1::3]),torch.sin(target[2][1::3]),rtol=0,atol=2e-12)
        next_n=torch.cat((moving[1:,0],endpoint[:1]),dim=0)
        oxy=internal(next_n,moving[:,1],moving[:,2],moving[:,3])
        for j in (0,1):torch.testing.assert_close(oxy[j],self.bridge.oxygen[j],rtol=0,atol=2e-12)
        torch.testing.assert_close(torch.sin(oxy[2]),torch.sin(self.bridge.oxygen[2]),rtol=0,atol=2e-12)

    def test_fixed_atoms_exact_and_failed_endpoint_not_silently_closed(self):
        output,residual=self.bridge.assemble(self.x,self.zero+.2)
        self.assertTrue(torch.equal(output[:2],self.x[:2]))
        self.assertTrue(torch.equal(output[10:],self.x[10:]))
        self.assertGreater(float(residual.norm()),1)
        self.assertGreater(float((output[2:10]-self.x[2:10]).norm()),1)

    def test_independent_numpy_audit_including_oxygen_and_boundary_planes(self):
        moving,endpoint=self.bridge.reconstruct(self.x,self.zero+.23)
        right=torch.cat((endpoint,self.x[10,3:4]),dim=0)
        extended=torch.cat((self.x[1:2],moving,right[None]),dim=0)
        audit=geometry_audit(extended.numpy(),self.x[1:11].numpy(),9,1,width=8)
        self.assertLess(audit['max_bond_delta'],1e-10)
        self.assertLess(audit['max_angle_delta'],1e-9)
        self.assertLess(audit['max_torsion_delta'],1e-9)

    def test_proper_motion_covariance(self):
        q,_=torch.linalg.qr(torch.randn(3,3,dtype=torch.float64));q[:,0]*=torch.linalg.det(q)
        shift=torch.tensor([3.,-7.,4.],dtype=torch.float64);delta=self.zero+.17
        output,residual=self.bridge.assemble(self.x,delta)
        moved=self.x@q+shift
        other,error=InternalBridge(moved,2,10).assemble(moved,delta)
        torch.testing.assert_close(other,output@q+shift,rtol=0,atol=5e-12)
        torch.testing.assert_close(error,residual@q,rtol=0,atol=5e-12)

    def test_endpoint_and_backbone_finite_difference_gradients(self):
        delta=(self.zero+.03).requires_grad_()
        self.assertTrue(torch.autograd.gradcheck(lambda d: self.bridge.reconstruct(self.x,d),(delta,),atol=1e-5,rtol=1e-4))
        output,endpoint=self.bridge.reconstruct(self.x,delta)
        g=torch.autograd.grad(endpoint.square().sum()+output.square().sum(),delta)[0]
        self.assertTrue(torch.isfinite(g).all());self.assertGreater(float(g.norm()),0)

    def test_reject_degenerate_or_terminal_inputs(self):
        with self.assertRaises(ValueError):InternalBridge(torch.zeros_like(self.x),2,10)
        with self.assertRaises(ValueError):InternalBridge(self.x,0,10)
        with self.assertRaises(ValueError):InternalBridge(self.x,2,12)
        bad=self.zero.clone();bad[0]=np.nan
        with self.assertRaises(ValueError):self.bridge.assemble(self.x,bad)


if __name__=='__main__':unittest.main()
