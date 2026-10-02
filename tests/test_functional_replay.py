import copy,unittest
import torch
from latentfold.pair_model import PairFlowNet
from functional_replay import replay_loss,state_digest,controlled_replay_backward


class FunctionalReplayTests(unittest.TestCase):
    def test_identical_field_zero_then_gradient_to_student_only(self):
        torch.manual_seed(42);model=PairFlowNet(d_model=16,n_layers=1,n_heads=2,d_pair=8,n_pair_blocks=1,d_cond=2560).train()
        with torch.no_grad():
            model.out_proj.weight.normal_(std=.1);model.out_ada[1].weight.normal_(std=.1);model.pair_bias.weight.normal_(std=.1)
            for block in model.blocks:block.ada[1].weight.normal_(std=.1)
        reference=copy.deepcopy(model).eval().requires_grad_(False);model.checkpoint_blocks=True;model.pair.checkpoint_blocks=True
        digest=state_digest(reference);mask=torch.tensor([[True,True,True,False],[True,True,False,False]])
        z=torch.randn(2,4,8);esm=torch.randn(2,4,2560)
        for seed in range(4):
            loss,stats=replay_loss(model,reference,z,esm,mask,generator=torch.Generator().manual_seed(seed));self.assertLessEqual(float(loss.detach()),1e-12);self.assertLessEqual(stats['max_velocity_error'],1e-6)
        with torch.no_grad():model.out_proj.weight.add_(.01)
        loss,stats=replay_loss(model,reference,z,esm,mask,generator=torch.Generator().manual_seed(7));self.assertGreater(stats['replay_loss'],0.);loss.backward()
        self.assertGreater(float(model.out_proj.weight.grad.norm()),0.);self.assertGreater(float(model.pair_bias.weight.grad.norm()),0.)
        self.assertTrue(all(p.grad is None for p in reference.parameters()));self.assertEqual(state_digest(reference),digest)

    def test_unfrozen_or_training_reference_rejected(self):
        model=PairFlowNet(d_model=16,n_layers=1,n_heads=2,d_pair=8,n_pair_blocks=1,d_cond=2560);mask=torch.ones(1,2,dtype=torch.bool)
        with self.assertRaisesRegex(ValueError,'frozen'):replay_loss(model,model,torch.zeros(1,2,8),torch.zeros(1,2,2560),mask,generator=torch.Generator())

    def test_auxiliary_gradient_capped_against_primary_before_combination(self):
        model=torch.nn.Linear(1,1,bias=False)
        with torch.no_grad():model.weight.fill_(1.)
        primary=(model.weight-3).square().sum()
        stats=controlled_replay_backward(model,primary,lambda:((model.weight+5).square().sum(),{}),weight=1.,max_ratio=.25)
        self.assertAlmostEqual(stats['primary_gradient_norm'],4.)
        self.assertAlmostEqual(stats['replay_gradient_norm'],12.)
        self.assertAlmostEqual(stats['replay_to_primary_ratio'],.25)
        self.assertAlmostEqual(float(model.weight.grad),-3.)


if __name__=='__main__':unittest.main()
