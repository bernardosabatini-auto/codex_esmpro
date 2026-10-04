import copy
from types import SimpleNamespace
import unittest
import torch
from latentfold.decoder import DifferentiableDecoder
from latentfold.fragment_conditioning import fragment_features
from latentfold.fragment_geometry_conditioning import fragment_coordinates
from latentfold.fragment_decoder_fm import (FragmentDenoisingDecoder, denoising_inputs,
    fragment_denoising_loss, region_fm_loss, sample_times)
from test_fragment_decoder import TinyDecoder


class DenoisingTests(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(23)
        ae=SimpleNamespace(decoder=TinyDecoder(),fm=SimpleNamespace(scale_ref=1.),cfg_exp=SimpleNamespace(model=SimpleNamespace(target_pred='v')))
        self.codec=DifferentiableDecoder(ae,n_steps=3)
        self.model=FragmentDenoisingDecoder(self.codec,seed=24,token_width=16,pair_width=8)
        self.z=torch.randn(2,8,8); self.mask=torch.ones(2,8,dtype=torch.bool)
        f,k=fragment_features(torch.randn(3,8),'ACD',length=8,start=2)
        self.features=f[None].repeat(2,1,1); self.keep=k[None].repeat(2,1)
        self.coords=fragment_coordinates(torch.randn(3,4,3),length=8,start=2)[None].repeat(2,1,1)
        self.target=torch.randn(2,8,4,3)*10; self.noise=torch.randn(2,32,3)
        self.t=torch.tensor([.4,.9]); self.dropped=torch.tensor([False,True])

    def loss(self,checkpointed=True):
        return fragment_denoising_loss(self.model,self.z,self.target,self.features,self.keep,self.mask,self.coords,
            noise=self.noise,t=self.t,dropped=self.dropped,checkpointed=checkpointed)

    def test_initial_state_only_wraps_top_level_feature_modules(self):
        from unittest.mock import patch
        from fragment_decoder_fm_core import initial_model_state
        nested={'pair_repr_builder.cond_factory.weight':torch.ones(1),'cond_factory.weight':torch.ones(2),'other.weight':torch.ones(3)}
        with patch('fragment_decoder_fm_core.expected_frozen_state',return_value=nested), patch('fragment_decoder_fm_core.initial_adapter',return_value={}):
            self.assertEqual(set(initial_model_state({})),{'decoder.pair_repr_builder.base.cond_factory.weight','decoder.cond_factory.base.weight','decoder.other.weight'})

    def test_zero_adapter_matches_original_and_copy_cannot_mutate_original(self):
        old=copy.deepcopy(self.codec.state_dict())
        z=torch.where(self.keep[...,None],torch.zeros_like(self.z),self.z)
        expected=self.codec(z,self.mask,noise=self.noise,return_backbone=True)[1]
        actual=self.model(self.z,self.features,self.keep,self.mask,self.coords,noise=self.noise)
        torch.testing.assert_close(actual,expected,rtol=0,atol=0)
        self.loss()[0].backward()
        self.assertGreater(float(self.model.decoder.latent.weight.grad.norm()),0)
        self.assertGreater(float(self.model.adapter.output.weight.grad.norm()),0)
        self.assertGreater(float(self.model.adapter.pair_output.weight.grad.norm()),0)
        torch.optim.SGD(self.model.parameters(),lr=.001).step()
        self.assertTrue(all(torch.equal(v,self.codec.state_dict()[k]) for k,v in old.items()))
        self.assertTrue(all(p.grad is None and not p.requires_grad for p in self.codec.parameters()))
        self.assertFalse(torch.equal(self.model.decoder.latent.weight,self.codec.decoder.latent.weight))

    def test_weighted_loss_reduces_to_original_coordinate_formula(self):
        clean,initial,noisy=denoising_inputs(self.target,self.noise,self.t)
        predicted=clean+torch.randn_like(clean)
        actual,_=region_fm_loss(predicted,clean,self.t,self.keep,motif_mass=3/8)
        expected=((predicted-clean).square().mean((1,2))/((1-self.t).square()+1e-5)).mean()
        torch.testing.assert_close(actual,expected)
        perfect=noisy+(1-self.t[:,None,None])*(clean-initial)
        self.assertLess(float(region_fm_loss(perfect,clean,self.t,self.keep)[0]),1e-10)

    def test_atoms_are_centered_in_nm_without_target_alignment(self):
        clean,initial,noisy=denoising_inputs(self.target,self.noise,self.t)
        torch.testing.assert_close(clean.mean(1),torch.zeros(2,3),atol=1e-7,rtol=0)
        torch.testing.assert_close(initial.mean(1),torch.zeros(2,3),atol=1e-7,rtol=0)
        shifted=denoising_inputs(self.target+20,self.noise+3,self.t)
        for a,b in zip((clean,initial,noisy),shifted): torch.testing.assert_close(a,b,atol=1e-6,rtol=0)

    def test_checkpoint_matches_all_decoder_and_adapter_gradients(self):
        results=[]
        for use in (False,True):
            self.model.zero_grad(set_to_none=True)
            loss,_,pred=self.loss(use); loss.backward()
            results.append((pred.detach(),{k:p.grad.clone() for k,p in self.model.named_parameters() if p.grad is not None}))
        torch.testing.assert_close(results[0][0],results[1][0],rtol=0,atol=0)
        self.assertEqual(set(results[0][1]),set(results[1][1]))
        for k in results[0][1]: torch.testing.assert_close(results[0][1][k],results[1][1][k],rtol=0,atol=1e-7)

    def test_hidden_motif_codes_and_dropped_fragment_cannot_leak(self):
        for p in self.model.adapter.parameters(): torch.nn.init.normal_(p,std=.05)
        loss,_,pred=self.loss(False)
        self.z[self.keep]=900
        torch.testing.assert_close(pred,self.loss(False)[2],rtol=0,atol=0)
        self.features[1,self.keep[1],:28]=7
        torch.testing.assert_close(pred[1],self.loss(False)[2][1],rtol=0,atol=0)

    def test_time_draws_match_mixture_and_are_reproducible(self):
        a=sample_times(100000,generator=torch.Generator().manual_seed(77),device='cpu')
        b=sample_times(100000,generator=torch.Generator().manual_seed(77),device='cpu')
        self.assertTrue(torch.equal(a,b)); self.assertTrue(((a>=0)&(a<1)).all())
        self.assertAlmostEqual(float(a.mean()),.98*1.9/2.9+.02*.5,delta=.003)
        self.assertAlmostEqual(float((a<.2).float().mean()),.98*.2**1.9+.02*.2,delta=.003)

    def test_padded_or_invalid_time_rejected(self):
        self.mask[1,-1]=False
        with self.assertRaises(ValueError): self.loss()
        self.mask[:]=True; self.t[0]=1
        with self.assertRaises(ValueError): self.loss()


if __name__=='__main__': unittest.main()
