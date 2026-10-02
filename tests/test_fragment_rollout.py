import unittest
import torch
from latentfold.pair_model import PairFlowNet
from latentfold.fragment_conditioning import FragmentAdapter,fragment_features,sample_fragment
from latentfold.fragment_rollout import differentiable_sample_fragment,rollout_fragment_objective
from latentfold.training import controlled_backward


class RolloutTests(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(43)
        self.net=PairFlowNet(d_model=16,n_layers=2,n_heads=2,d_cond=12,d_pair=4,n_pair_blocks=1,max_len=16).eval()
        with torch.no_grad():
            for p in self.net.parameters():p.normal_(0,.1)
        self.adapter=FragmentAdapter(16,12).eval()
        with torch.no_grad():self.adapter.output.weight.normal_(0,.1)
        features,keep=fragment_features(torch.randn(3,8),'ACD',length=7,start=2);self.features=features[None].repeat(2,1,1);self.keep=keep[None].repeat(2,1);self.mask=torch.arange(7)[None]<torch.tensor([7,5])[:,None];self.noise=torch.randn(2,7,8);self.probe=torch.randn_like(self.noise)

    def sample(self,checkpointed):
        return differentiable_sample_fragment(self.net,self.adapter,self.features,self.keep,self.mask,noise=self.noise,steps=4,checkpoint_velocity=checkpointed)

    def test_forward_parity_and_checkpointed_gradients(self):
        expected=sample_fragment(self.net,self.adapter,self.features,self.keep,self.mask,noise=self.noise,steps=4);parameters=list(self.net.parameters())+list(self.adapter.parameters());gradients=[]
        for cp in (False,True):
            # Grad-enabled attention can choose a different arithmetic kernel from
            # no-grad inference; retain the established 1e-5 latent tolerance.
            z=self.sample(cp);torch.testing.assert_close(z,expected,atol=1e-5,rtol=0);gradients.append(torch.autograd.grad((z*self.probe).sum(),parameters,allow_unused=True))
        nonzero=0
        for left,right in zip(*gradients):
            self.assertEqual(left is None,right is None)
            if left is not None:
                self.assertTrue(torch.isfinite(right).all());torch.testing.assert_close(left,right,atol=1e-6,rtol=1e-4);nonzero+=int(right.norm()>0)
        self.assertGreater(nonzero,0)

    def test_modes_and_rng_survive_backward(self):
        self.net.train();self.adapter.train();next(iter(self.net.children())).eval();states={m:m.training for root in (self.net,self.adapter) for m in root.modules()};before=torch.get_rng_state().clone();(self.sample(True)*self.probe).sum().backward()
        self.assertTrue(torch.equal(before,torch.get_rng_state()));self.assertTrue(all(m.training==was for m,was in states.items()))

    def test_directional_gradient_matches_finite_difference(self):
        parameter=self.adapter.output.bias;direction=torch.randn_like(parameter);z=self.sample(True);gradient=torch.autograd.grad((z*self.probe).sum(),parameter)[0];exact=float((gradient*direction).sum());original=parameter.detach().clone();values=[];eps=.002
        with torch.no_grad():
            for sign in (-1,1):parameter.copy_(original+sign*eps*direction);values.append(float((self.sample(False)*self.probe).sum()))
            parameter.copy_(original)
        self.assertAlmostEqual(exact,(values[1]-values[0])/(2*eps),delta=.005)

    def test_objective_uses_independent_noise_and_only_eligible_slots(self):
        from types import SimpleNamespace
        from latentfold.fragment_geometry_conditioning import FragmentGeometryAdapter
        self.adapter=FragmentGeometryAdapter(16,n_layers=2,n_heads=2,hidden=12,distance_precision="fp64").eval()
        class Decoder(torch.nn.Module):
            fm=SimpleNamespace(scale_ref=1.)
            def forward(self,z,mask,noise):
                assert noise.shape==(len(z),4*z.shape[1],3)
                return z[...,:3]*mask[...,None]
        coordinates=torch.randn(2,7,3)*self.keep[...,None];dropped=torch.tensor([True,False]);before=torch.get_rng_state().clone()
        loss,stats=rollout_fragment_objective(self.net,self.adapter,Decoder(),self.features,self.keep,self.mask,coordinates,['a','b'],[7,5],dropped,step=0)
        self.assertEqual(stats['chosen_slots'],[1]);self.assertEqual(stats['velocity_evaluations'],50);self.assertEqual(stats['lengths'],[5]);loss.backward();self.assertTrue(torch.equal(before,torch.get_rng_state()));self.assertTrue(torch.isfinite(self.adapter.output.bias.grad).all())
        loss,stats=rollout_fragment_objective(self.net,self.adapter,Decoder(),self.features,self.keep,self.mask,coordinates,['a','b'],[7,5],torch.ones(2,dtype=torch.bool),step=0)
        self.assertIsNone(loss);self.assertEqual(stats['motif_examples'],0)

    def test_independent_auxiliary_graph_can_release_primary(self):
        model=torch.nn.Linear(2,1,bias=False);x=torch.tensor([[1.,2.]]);flow=model(x).square().sum();aux=(model(x+1)-1).square().sum();stats=controlled_backward(model,flow,aux,weight=1.,max_ratio=.5,loss_scale=1.,shared_graph=False)
        self.assertTrue(torch.isfinite(model.weight.grad).all());self.assertLessEqual(stats['aux_to_flow_ratio'],.5+1e-7)


if __name__=='__main__':unittest.main()
