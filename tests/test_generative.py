import unittest
import torch
from latentfold.pair_model import PairFlowNet
from latentfold.flow import SampleConfig, sample
from latentfold.generative import sample_unconditional

class GenerativeTests(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(7)
        self.net=PairFlowNet(d_model=16,n_layers=2,n_heads=2,d_cond=12,d_pair=4,n_pair_blocks=1,max_len=16).eval()
        with torch.no_grad():
            for p in self.net.parameters(): p.copy_(torch.randn_like(p)*.1)
        self.esm=torch.randn(2,7,12);self.mask=torch.arange(7)[None]<torch.tensor([7,5])[:,None];self.noise=torch.randn(2,7,8)
    def test_unconditional_matches_generic_with_nontrivial_pair_weights(self):
        generic=sample(self.net,self.esm,self.mask,SampleConfig(steps=4,guidance=0),noise=self.noise)
        fast=sample_unconditional(self.net,self.esm,self.mask,noise=self.noise,steps=4)
        torch.testing.assert_close(fast,generic,atol=1e-6,rtol=1e-6)
        changed=sample_unconditional(self.net,self.esm+100,self.mask,noise=self.noise,steps=4)
        torch.testing.assert_close(fast,changed,atol=0,rtol=0)
    def test_motif_noise_is_explicit_and_reproducible(self):
        keep=torch.zeros_like(self.mask);keep[:,1:3]=True;target=torch.randn_like(self.noise);eps=torch.randn_like(self.noise);calls=[]
        def fresh(i,j):calls.append((i,j));return eps*(1+i+j)
        kw=dict(noise=self.noise,steps=3,fixed=(target,keep),motif_noise=eps,repaint=3,fresh_noise=fresh)
        one=sample_unconditional(self.net,self.esm,self.mask,**kw)
        self.assertEqual(calls,[(0,0),(0,1),(1,0),(1,1)])
        two=sample_unconditional(self.net,self.esm,self.mask,**kw)
        torch.testing.assert_close(one,two,atol=0,rtol=0)
        self.assertTrue((one[~self.mask]==0).all())
        keep[1,-1]=True
        with self.assertRaises(ValueError):sample_unconditional(self.net,self.esm,self.mask,**kw)

if __name__=='__main__':unittest.main()
