import unittest
import torch
from latentfold.pair_model import PairFlowNet
from latentfold.generative import sample_unconditional
from latentfold.noise_guidance import unconditional_endpoint,normalized_gradient,project_radius

class NoiseGuidanceTests(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(31);self.net=PairFlowNet(d_model=16,n_layers=2,n_heads=2,d_cond=12,d_pair=4,n_pair_blocks=1,max_len=16).eval()
        with torch.no_grad():
            for p in self.net.parameters():p.copy_(torch.randn_like(p)*.1)
        self.net.requires_grad_(False);self.mask=torch.arange(7)[None]<torch.tensor([7,5])[:,None];self.x=torch.randn(2,7,8)
    def test_checkpointed_value_and_gradient_match_direct(self):
        x=self.x.clone().requires_grad_();y=unconditional_endpoint(self.net,x,self.mask,steps=4);direct=unconditional_endpoint(self.net,x,self.mask,steps=4,checkpoint_steps=False);baseline=sample_unconditional(self.net,torch.zeros(2,7,12),self.mask,noise=x.detach(),steps=4)
        torch.testing.assert_close(y,baseline,atol=0,rtol=0);weights=torch.randn_like(y)
        g1,=torch.autograd.grad((y*weights).sum(),x);g2,=torch.autograd.grad((direct*weights).sum(),x)
        torch.testing.assert_close(g1,g2,atol=1e-6,rtol=1e-6)
    def test_gradient_matches_finite_difference(self):
        x=self.x.clone().requires_grad_();weights=torch.randn_like(x);direction=torch.randn_like(x);direction/=direction.norm();y=unconditional_endpoint(self.net,x,self.mask,steps=4);g,=torch.autograd.grad((y*weights).sum(),x);eps=.002
        with torch.no_grad():
            plus=unconditional_endpoint(self.net,x+eps*direction,self.mask,steps=4);minus=unconditional_endpoint(self.net,x-eps*direction,self.mask,steps=4)
        fd=((plus-minus)*weights).sum()/(2*eps);torch.testing.assert_close((g*direction).sum(),fd,atol=.002,rtol=.01)
    def test_gradient_scale_and_radius_preserved(self):
        g=torch.randn_like(self.x);one=normalized_gradient(g,self.mask);two=normalized_gradient(10*g,self.mask);torch.testing.assert_close(one,two,atol=1e-6,rtol=1e-6)
        new=project_radius(self.x-.05*one,self.x,self.mask);torch.testing.assert_close((new.square()*self.mask[...,None]).sum((1,2)),(self.x.square()*self.mask[...,None]).sum((1,2)),atol=1e-5,rtol=1e-6);self.assertTrue((new[~self.mask]==0).all())

if __name__=='__main__':unittest.main()
