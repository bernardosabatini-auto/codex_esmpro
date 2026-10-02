import unittest
import torch
from summary_adapter import SummaryAdapter
from latentfold.flow import FlowConfig,flow_loss
from latentfold.pair_model import PairFlowNet


class SummaryAdapterTests(unittest.TestCase):
    def test_initial_identity_and_learned_masked_residual(self):
        torch.manual_seed(1);adapter=SummaryAdapter(8,.1);mask=torch.tensor([[True,True,False],[True,False,False]])
        final=torch.randn(2,3,2560)*mask[...,None];feature=torch.randn(2,3,256)
        self.assertTrue(torch.equal(adapter(final,feature,mask),final))
        value=adapter(final,feature,mask);value.square().sum().backward()
        self.assertGreater(float(adapter.up.weight.grad.norm()),0.)
        with torch.no_grad():adapter.up.weight.add_(adapter.up.weight.grad,alpha=-.001)
        changed=adapter(final,feature,mask);self.assertTrue(torch.isfinite(changed).all());self.assertLessEqual(float((changed-final).detach().abs().max()),.100001)
        self.assertEqual(float(changed[~mask].detach().abs().sum()),0.)
        feature[~mask]=1e5;self.assertTrue(torch.equal(changed,adapter(final,feature,mask)))

    def test_flow_training_reaches_adapter_through_checkpointed_pair_and_single(self):
        torch.manual_seed(5)
        net=PairFlowNet(d_model=16,n_layers=1,n_heads=2,d_pair=8,n_pair_blocks=1,d_cond=2560).train()
        # Inherited heads are nonzero; a freshly initialized head is zero.
        with torch.no_grad():
            net.out_proj.weight.normal_(std=.1)
            net.out_ada[1].weight.normal_(std=.1)
            net.pair_bias.weight.normal_(std=.1)
            for block in net.blocks:block.ada[1].weight.normal_(std=.1)
        net.checkpoint_blocks=True;net.pair.checkpoint_blocks=True
        adapter=SummaryAdapter(8);mask=torch.ones(2,5,dtype=torch.bool);final=torch.randn(2,5,2560);feature=torch.randn(2,5,256);z=torch.randn(2,5,8)
        c=FlowConfig();a,_=flow_loss(net,z,final,mask,c,generator=torch.Generator().manual_seed(8))
        b,_=flow_loss(net,z,adapter(final,feature,mask),mask,c,generator=torch.Generator().manual_seed(8))
        self.assertTrue(torch.equal(a,b));b.backward();self.assertGreater(float(adapter.up.weight.grad.norm()),0.)


if __name__=='__main__':unittest.main()
