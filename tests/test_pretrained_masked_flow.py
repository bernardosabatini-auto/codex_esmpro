import unittest
from unittest.mock import patch
import torch
from latentfold.pair_model import PairFlowNet
from latentfold.fragment_geometry_conditioning import FragmentGeometryAdapter,fragment_coordinates
from latentfold.fragment_conditioning import fragment_features,sample_fragment
from latentfold.masked_fragment_flow import editable_window
from latentfold.pretrained_masked_flow import PretrainedMaskedFlow,pretrained_masked_loss,sample_pretrained_masked


class PretrainedMaskedTests(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(52)
        net=PairFlowNet(d_model=16,n_layers=2,n_heads=2,d_cond=12,d_pair=4,n_pair_blocks=1,max_len=32)
        adapter=FragmentGeometryAdapter(16,n_layers=2,n_heads=2,hidden=8,pair_hidden=4,distance_precision='fp64')
        for p in list(net.parameters())+list(adapter.parameters()):torch.nn.init.normal_(p,std=.03)
        self.model=PretrainedMaskedFlow(net,adapter,53).eval();self.mask=torch.ones(2,32,dtype=torch.bool);self.mask[1,30:]=False
        self.z=torch.randn(2,32,8)*self.mask[...,None];self.noise=torch.randn_like(self.z)
        f,k=fragment_features(torch.randn(5,8),'ACDEF',length=32,start=10);self.features=f[None].repeat(2,1,1);self.keep=k[None].repeat(2,1)
        self.coords=fragment_coordinates(torch.randn(5,4,3),length=32,start=10)[None].repeat(2,1,1)

    def sample(self,context=None,**kwargs):
        return sample_pretrained_masked(self.model.eval(),self.z if context is None else context,self.features,self.keep,self.mask,self.coords,noise=self.noise,steps=3,flank=2,**kwargs)

    def test_initial_all_edit_matches_parent_exactly(self):
        expected=sample_fragment(self.model.net,self.model.fragment,self.features,self.keep,self.mask,noise=self.noise,steps=3,coordinates=self.coords)
        self.assertTrue(torch.equal(self.sample(edit_override=self.mask),expected))

    def test_no_editable_endpoint_leak_with_live_context_adapter(self):
        for p in self.model.context.parameters():torch.nn.init.normal_(p,std=.03)
        edit=editable_window(self.keep,self.mask,2);first=self.sample();other=self.z.clone();other[edit]=88
        self.assertTrue(torch.equal(first,self.sample(other)))
        self.assertTrue(torch.equal(first[~edit],self.z[~edit]))
        posed=(self.coords.double()@torch.tensor([[0.,-1,0],[1,0,0],[0,0,1]],dtype=torch.float64)+11)*self.keep[...,None]
        z=sample_pretrained_masked(self.model,self.z,self.features,self.keep,self.mask,posed,noise=self.noise,steps=3,flank=2)
        torch.testing.assert_close(first,z,rtol=0,atol=1e-5)

    def test_training_updates_context_and_keeps_unused_parameters_frozen(self):
        self.model.train();loss,info=pretrained_masked_loss(self.model,self.z,self.features,self.keep,self.mask,self.coords,generator=torch.Generator().manual_seed(4),flank=2);loss.backward()
        self.assertTrue(torch.isfinite(loss));self.assertGreater(float(self.model.context.output.weight.grad.norm()),0)
        for k,p in self.model.named_parameters():
            if k in self.model.frozen_names:self.assertIsNone(p.grad)
        self.assertIsInstance(info['self_conditioned'],bool)

    def test_self_conditioning_history_keeps_clean_scaffold(self):
        self.model.train();edit=editable_window(self.keep,self.mask,2);seen=False
        for seed in range(8):
            with patch.object(self.model,'forward',wraps=self.model.forward) as calls:
                _,info=pretrained_masked_loss(self.model,self.z,self.features,self.keep,self.mask,self.coords,generator=torch.Generator().manual_seed(seed),flank=2)
            if info['self_conditioned']:
                history=calls.call_args.args[5]
                self.assertTrue(torch.equal(history[~edit],self.z[~edit]));seen=True;break
        self.assertTrue(seen)


if __name__=='__main__':unittest.main()
