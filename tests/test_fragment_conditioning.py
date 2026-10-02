import copy,unittest
import torch
from latentfold.pair_model import PairFlowNet
from latentfold.generative import sample_unconditional
from latentfold.fragment_conditioning import FragmentAdapter,fragment_features,fragment_flow_loss,sample_fragment


class FragmentConditioningTests(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(11)
        self.net=PairFlowNet(d_model=16,n_layers=2,n_heads=2,d_cond=12,d_pair=4,n_pair_blocks=1,max_len=16).eval()
        with torch.no_grad():
            for p in self.net.parameters():p.copy_(torch.randn_like(p)*.1)
        self.adapter=FragmentAdapter(16,12).eval();f,k=fragment_features(torch.randn(3,8),'ACD',length=7,start=2)
        self.f=f[None].repeat(2,1,1);self.k=k[None].repeat(2,1);self.mask=torch.arange(7)[None]<torch.tensor([7,5])[:,None];self.noise=torch.randn(2,7,8)

    def test_zero_adapter_matches_original_and_padding(self):
        expected=sample_unconditional(self.net,torch.randn(2,7,12),self.mask,noise=self.noise,steps=4)
        actual=sample_fragment(self.net,self.adapter,self.f,self.k,self.mask,noise=self.noise,steps=4)
        torch.testing.assert_close(actual,expected,atol=0,rtol=0)
        self.assertTrue((actual[~self.mask]==0).all())

    def test_dropout_removes_all_fragment_information(self):
        with torch.no_grad():self.adapter.output.weight.normal_()
        other=self.f.clone();other[..., :8][self.k]+=100
        a=sample_fragment(self.net,self.adapter,self.f,self.k,self.mask,noise=self.noise,steps=4,drop_fragment=True)
        b=sample_fragment(self.net,self.adapter,other,self.k,self.mask,noise=self.noise,steps=4,drop_fragment=True)
        torch.testing.assert_close(a,b,atol=0,rtol=0)
        conditional=sample_fragment(self.net,self.adapter,self.f,self.k,self.mask,noise=self.noise,steps=4)
        self.assertGreater(float((conditional-a).abs().max()),1e-5)

    def test_scaffold_features_and_invalid_placements_rejected(self):
        f=self.f.clone();f[0,0,0]=1
        with self.assertRaises(ValueError):self.adapter(f,self.k,self.mask,torch.zeros(2,dtype=torch.bool))
        with self.assertRaises(ValueError):fragment_features(torch.randn(3,8),'ACD',length=4,start=2)
        with self.assertRaises(ValueError):fragment_features(torch.randn(3,8),'ACX',length=7,start=2)

    def test_frozen_base_has_adapter_gradient_and_matching_random_draws(self):
        target=torch.randn_like(self.noise);net=copy.deepcopy(self.net).train();adapter=copy.deepcopy(self.adapter).train();net.requires_grad_(False)
        loss,info=fragment_flow_loss(net,adapter,target,self.f,self.k,self.mask,generator=torch.Generator().manual_seed(31));loss.backward()
        self.assertTrue(all(p.grad is None for p in net.parameters()))
        self.assertTrue(torch.isfinite(adapter.output.weight.grad).all());self.assertGreater(float(adapter.output.weight.grad.norm()),0)
        net2=copy.deepcopy(self.net).train();adapter2=copy.deepcopy(self.adapter).train();other,draws=fragment_flow_loss(net2,adapter2,target,self.f,self.k,self.mask,generator=torch.Generator().manual_seed(31))
        torch.testing.assert_close(loss,other,atol=0,rtol=0)
        for k in ('noise','t','dropped'):torch.testing.assert_close(info[k],draws[k],atol=0,rtol=0)
        self.assertEqual(info['self_conditioned'],draws['self_conditioned'])


if __name__=='__main__':unittest.main()
