import unittest
import torch
from latentfold.motif_objective import motif_distance_mse

class MotifObjectiveTests(unittest.TestCase):
 def test_gradient_and_local_support(self):
  torch.manual_seed(72);x=torch.randn(2,12,4,3,dtype=torch.float64,requires_grad=True);ref=torch.randn(5,4,3,dtype=torch.float64);loss=motif_distance_mse(x,ref,3).sum();grad,=torch.autograd.grad(loss,x);direction=torch.randn_like(x);direction/=direction.norm();eps=1e-5
  with torch.no_grad():fd=(motif_distance_mse(x+eps*direction,ref,3).sum()-motif_distance_mse(x-eps*direction,ref,3).sum())/(2*eps)
  torch.testing.assert_close((grad*direction).sum(),fd,atol=1e-8,rtol=1e-6)
  self.assertEqual(float(grad[:,:3].abs().sum()+grad[:,8:].abs().sum()),0)
  self.assertEqual(float(grad[:,:,[0,2,3]].abs().sum()),0)
 def test_independent_rigid_pose_invariance(self):
  torch.manual_seed(73);x=torch.randn(2,12,4,3,dtype=torch.float64);ref=x[0,3:8].clone();rotation=torch.tensor([[0.,-1,0],[1,0,0],[0,0,1]],dtype=x.dtype);base=motif_distance_mse(x,ref,3)
  torch.testing.assert_close(base,motif_distance_mse(x@rotation+13,ref-7,3),atol=1e-12,rtol=1e-12);self.assertEqual(float(base[0]),0)
if __name__=='__main__':unittest.main()
