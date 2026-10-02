import unittest
import torch
from latentfold.pair_model import PairFlowNet
from latentfold.flow import FlowConfig,flow_loss
from latentfold.training_subset import configure_tail,frozen_digest

class TailTests(unittest.TestCase):
    def model(self):
        torch.manual_seed(7)
        m=PairFlowNet(d_model=32,n_layers=3,n_heads=4,d_cond=12,max_len=16,d_pair=8,n_pair_blocks=1)
        with torch.no_grad():
            for p in m.parameters():p.normal_(0,.1)
        m.checkpoint_blocks=True;m.pair.checkpoint_blocks=True
        return m

    def test_frozen_raw_and_ema_survive_real_loss_and_optimizer(self):
        m=self.model();before={k:v.clone() for k,v in m.state_dict().items()}
        subset=configure_tail(m,1);digest=frozen_digest(m)
        self.assertLess(subset['trainable_parameters'],subset['total_parameters'])
        for name,p in m.named_parameters():
            self.assertEqual(p.requires_grad,name.startswith(('blocks.2.','out_ada.','out_proj.')))
        opt=torch.optim.AdamW([p for p in m.parameters() if p.requires_grad],lr=.003,weight_decay=.01)
        loss,_=flow_loss(m,torch.randn(2,8,8),torch.randn(2,8,12),torch.ones(2,8,dtype=torch.bool),FlowConfig(self_condition_probability=1),generator=torch.Generator().manual_seed(11))
        loss.backward()
        self.assertTrue(all(p.grad is None for p in m.parameters() if not p.requires_grad))
        self.assertGreater(float(m.blocks[-1].attn.qkv.weight.grad.norm()),0)
        self.assertTrue(all(torch.isfinite(p.grad).all() for p in m.parameters() if p.grad is not None))
        opt.step();self.assertEqual(digest,frozen_digest(m))
        self.assertFalse(torch.equal(before['out_proj.weight'],m.out_proj.weight))
        ema={k:v.lerp(m.state_dict()[k],.01) for k,v in before.items()}
        self.assertEqual(digest,frozen_digest(m,ema))
        with torch.no_grad():m.in_proj.weight[0,0]+=1
        self.assertNotEqual(digest,frozen_digest(m))

    def test_bad_tail_depth_rejected_without_changing_parameters(self):
        m=self.model()
        for n in (0,-1,3,4,1.5,True):
            with self.assertRaises(ValueError):configure_tail(m,n)
        self.assertTrue(all(p.requires_grad for p in m.parameters()))

if __name__=='__main__':unittest.main()
