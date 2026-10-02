import unittest
import torch
from latentfold.pair_model import PairFlowNet
from latentfold.unconditional_training import freeze_unused_conditioning,unconditional_loss

class UnconditionalTrainingTests(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(21);self.net=PairFlowNet(d_model=16,n_layers=2,n_heads=2,d_cond=12,d_pair=4,n_pair_blocks=1,max_len=16).train()
        with torch.no_grad():
            for p in self.net.parameters():p.copy_(torch.randn_like(p)*.1)
        self.mask=torch.arange(7)[None]<torch.tensor([7,5])[:,None];self.z=torch.randn(2,7,8);self.noise=torch.randn_like(self.z)
    def test_rng_and_time_match_while_coupling_changes(self):
        g1=torch.Generator().manual_seed(5);g2=torch.Generator().manual_seed(5)
        one,a=unconditional_loss(self.net,self.z,self.mask,recorded_noise=self.noise,paired=True,generator=g1)
        two,b=unconditional_loss(self.net,self.z,self.mask,recorded_noise=self.noise,paired=False,generator=g2)
        self.assertTrue(torch.equal(g1.get_state(),g2.get_state()));self.assertTrue(torch.equal(a['t'],b['t']));self.assertEqual(a['self_conditioned'],b['self_conditioned']);self.assertNotEqual(float(one.detach()),float(two.detach()))
    def test_unused_parameters_frozen_null_and_trunk_train(self):
        names=freeze_unused_conditioning(self.net);self.assertTrue(names)
        before={n:p.clone() for n,p in self.net.named_parameters() if n in names};opt=torch.optim.AdamW([p for p in self.net.parameters() if p.requires_grad],lr=.01)
        loss,_=unconditional_loss(self.net,self.z,self.mask,recorded_noise=self.noise,paired=True,generator=torch.Generator().manual_seed(4));loss.backward()
        for n,p in self.net.named_parameters():
            if n in names:self.assertIsNone(p.grad)
        self.assertGreater(float(self.net.null_cond.grad.abs().sum()),0);self.assertGreater(float(self.net.null_pair.grad.abs().sum()),0);self.assertGreater(float(self.net.out_proj.weight.grad.abs().sum()),0)
        opt.step()
        for n,p in self.net.named_parameters():
            if n in names:torch.testing.assert_close(p,before[n],rtol=0,atol=0)

if __name__=='__main__':unittest.main()
