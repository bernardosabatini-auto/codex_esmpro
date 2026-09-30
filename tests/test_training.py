import unittest
from copy import deepcopy
import torch
from latentfold.pair_model import PairFlowNet
from latentfold.flow import FlowConfig
from latentfold.training import objective

class Decoder(torch.nn.Module):
    def forward(self,z,mask,*,noise):
        return z[...,:3]*3*mask[...,None]

class TrainingTests(unittest.TestCase):
    def test_checkpoint_gradient_and_matched_rng(self):
        torch.manual_seed(17)
        net=PairFlowNet(d_model=32,n_layers=2,n_heads=4,d_cond=16,d_pair=8,n_pair_blocks=1,max_len=16)
        # Production checkpoints have nonzero output weights; avoid trivial zero-gradient initialization.
        torch.nn.init.normal_(net.out_proj.weight,std=.05)
        other=deepcopy(net);other.checkpoint_blocks=True;other.pair.checkpoint_blocks=True
        batch=dict(z=torch.randn(4,12,8),esm=torch.randn(4,12,16),ca=torch.randn(4,12,3)*3,
                   mask=torch.ones(4,12,dtype=torch.bool),adjacent=torch.ones(4,11,dtype=torch.bool),
                   ids=['a','b','c','d'],lengths=[12]*4)
        config=FlowConfig(condition_dropout=0,self_condition_probability=1,time_mean=2,time_std=.1)
        generators=[torch.Generator().manual_seed(31) for _ in range(3)]
        plain,pinfo=objective(net,Decoder(),batch,config,generator=generators[0])
        joint,info=objective(other,Decoder(),batch,config,generator=generators[1],geometry_weight=.1)
        self.assertEqual(pinfo['flow_loss'],info['flow_loss'])
        self.assertTrue(torch.equal(generators[0].get_state(),generators[1].get_state()))
        self.assertGreater(info['geometry_count'],0)
        joint.backward()
        plain.backward()
        uncheckpointed=deepcopy(net);uncheckpointed.zero_grad(set_to_none=True)
        check,_=objective(uncheckpointed,Decoder(),batch,config,generator=generators[2],geometry_weight=.1)
        check.backward()
        for (name,p),(othername,q) in zip(other.named_parameters(),uncheckpointed.named_parameters()):
            self.assertEqual(name,othername)
            if p.grad is not None:torch.testing.assert_close(p.grad,q.grad,atol=1e-6,rtol=1e-5)
