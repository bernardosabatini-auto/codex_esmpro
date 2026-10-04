import unittest
from types import SimpleNamespace
import torch
from latentfold.decoder import DifferentiableDecoder
from latentfold.fragment_conditioning import fragment_features
from latentfold.fragment_geometry_conditioning import fragment_coordinates
from latentfold.fragment_inpainting import place_fragment,context_mask,denoising_state
from latentfold.scaffold_bridge import coordinate_known,scaffold_anchors,bridge_weights,bridge_loss,ScaffoldBridgeDecoder
from test_fragment_decoder import TinyDecoder


class ScaffoldBridgeTests(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(61);self.target=torch.randn(2,60,4,3)*10;self.keep=torch.zeros(2,60,dtype=torch.bool);self.keep[:,20:40]=True
        ae=SimpleNamespace(decoder=TinyDecoder(),fm=SimpleNamespace(scale_ref=1.),cfg_exp=SimpleNamespace(model=SimpleNamespace(target_pred='v')))
        self.codec=DifferentiableDecoder(ae,n_steps=3);self.model=ScaffoldBridgeDecoder(self.codec,seed=24,token_width=16,pair_width=8)
        feat,_=fragment_features(torch.randn(20,8),'A'*20,length=60,start=20)
        self.features=feat[None].expand(2,-1,-1);self.coords=fragment_coordinates(self.target[0,20:40],length=60,start=20)[None].expand(2,-1,-1)
        self.z=torch.randn(2,60,8);self.mask=torch.ones(2,60,dtype=torch.bool);self.noise=torch.randn(2,240,3)
        motif=place_fragment(self.target[0,20:40],self.target,20);self.anchors=scaffold_anchors(self.target,motif,self.keep)

    def forward(self,**kwargs):
        values=dict(context=self.z,features=self.features,keep=self.keep,mask=self.mask,coordinates=self.coords,anchors=self.anchors,noise=self.noise)
        values.update(kwargs);return self.model(**values)

    def test_condition_and_dropout_fix_different_coordinates(self):
        known=coordinate_known(self.keep,torch.tensor([False,True]));self.assertEqual((~known).sum(1).tolist(),[16,36])
        self.assertTrue(known[0,self.keep[0]].all());self.assertFalse(known[1,self.keep[1]].any())
        self.assertTrue((known|context_mask(self.keep,8)).all())
        weights=bridge_weights(self.keep,torch.tensor([False,True])).reshape(2,60,4)
        torch.testing.assert_close(weights.sum((1,2)),torch.ones(2),rtol=0,atol=1e-7)
        self.assertTrue((weights[known]==0).all())
        near=(context_mask(self.keep,4)&~self.keep)[0]
        self.assertAlmostEqual(float(weights[0,near].sum()),.5)
        self.assertAlmostEqual(float(weights[0,~known[0]&~near].sum()),.5)
        self.assertEqual(torch.unique(weights[1,~known[1]]).numel(),1)

    def test_far_atoms_and_motif_are_fixed_at_every_actual_network_call(self):
        seen=[];hook=self.model.decoder.register_forward_pre_hook(lambda module,args:seen.append(args[0]['x_t'].clone()))
        out=self.forward();hook.remove();known=coordinate_known(self.keep,torch.zeros(2,dtype=torch.bool))
        for x in seen:torch.testing.assert_close(x.reshape(2,60,4,3)[known],self.anchors[known]/10,rtol=0,atol=0)
        self.assertEqual(len(seen),3);torch.testing.assert_close(out[known],self.anchors[known],rtol=0,atol=2e-6)
        torch.testing.assert_close(out.mean((1,2)),torch.zeros(2,3),rtol=0,atol=2e-6)
        self.assertEqual(len(self.model.state_audits),1)

    def test_hidden_context_and_every_fixed_atom_noise_cannot_leak(self):
        a=self.forward();z=self.z.clone();z[context_mask(self.keep,8)]+=73
        known=coordinate_known(self.keep,torch.zeros(2,dtype=torch.bool));noise=self.noise.clone();noise[known.repeat_interleave(4,1)]+=101
        torch.testing.assert_close(a,self.forward(context=z,noise=noise),rtol=0,atol=0)

    def test_dropout_removes_motif_but_retains_far_scaffold(self):
        a=self.forward(drop_fragment=True);f=self.features.clone();f[self.keep,:28]+=31
        xyz=self.coords.clone();xyz[self.keep]+=29;anchors=self.anchors.clone();anchors[self.keep]+=17
        z=self.z.clone();z[context_mask(self.keep,8)]+=13
        b=self.forward(drop_fragment=True,features=f,coordinates=xyz,anchors=anchors,context=z)
        torch.testing.assert_close(a,b,rtol=0,atol=0)
        known=coordinate_known(self.keep,torch.ones(2,dtype=torch.bool));torch.testing.assert_close(a[known],self.anchors[known],rtol=0,atol=2e-6)

    def test_affine_training_path_and_checkpoint_gradients(self):
        dropped=torch.tensor([False,True]);t=torch.tensor([.2,.8]);known=coordinate_known(self.keep,dropped)
        clean,noisy,anchors,atoms=denoising_state(self.target,self.noise,t,known,torch.zeros_like(dropped))
        torch.testing.assert_close(noisy[atoms],anchors[atoms],rtol=0,atol=0)
        torch.testing.assert_close(noisy.mean(1),torch.zeros(2,3),rtol=0,atol=1e-6)
        saved=[]
        for cp in (False,True):
            self.model.zero_grad(set_to_none=True)
            loss,_,pred=bridge_loss(self.model,self.z,self.target,self.features,self.keep,self.mask,self.coords,noise=self.noise,t=t,dropped=dropped,checkpointed=cp)
            loss.backward();saved.append((loss.detach(),pred.detach(),{k:p.grad.clone() for k,p in self.model.named_parameters() if p.grad is not None}))
            torch.testing.assert_close(pred[atoms],clean[atoms],rtol=0,atol=0)
        for x,y in zip(saved[0][:2],saved[1][:2]):torch.testing.assert_close(x,y,rtol=0,atol=0)
        for k in saved[0][2]:torch.testing.assert_close(saved[0][2][k],saved[1][2][k],rtol=0,atol=1e-6)
        self.assertGreater(float(saved[0][2]['decoder.token.weight'].norm()),0)
        # The pointwise tiny decoder cannot propagate a far latent into an
        # unknown position; its zero latent-weight gradient is expected here.
        noise=self.noise.clone().requires_grad_()
        loss,_,_=bridge_loss(self.model,self.z,self.target,self.features,self.keep,self.mask,self.coords,noise=noise,t=t,dropped=dropped,checkpointed=False)
        loss.backward();self.assertTrue((noise.grad[atoms]==0).all());self.assertGreater(float(noise.grad[~atoms].abs().sum()),0)
        self.assertTrue(all(p.grad is None for p in self.codec.parameters()))

    def test_anchor_assembly_copies_only_far_scaffold_and_supplied_fragment(self):
        far=~context_mask(self.keep,8);centered=self.target-self.target.mean((1,2),keepdim=True)
        torch.testing.assert_close(self.anchors[far],centered[far],rtol=0,atol=0)
        self.assertTrue((self.anchors[context_mask(self.keep,8)&~self.keep]==0).all())
        rotation=torch.tensor([[0.,-1,0],[1.,0,0],[0,0,1]],dtype=torch.float64)
        motif=place_fragment(self.target[0,20:40].double()@rotation+11,self.target,20)
        torch.testing.assert_close(scaffold_anchors(self.target,motif,self.keep),self.anchors,rtol=0,atol=1e-5)
        with self.assertRaises(ValueError):self.forward(anchors=self.anchors+1)


if __name__=='__main__':unittest.main()
