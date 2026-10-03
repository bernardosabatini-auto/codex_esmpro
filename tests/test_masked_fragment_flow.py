import unittest
import torch
from latentfold.masked_fragment_flow import MaskedFragmentFlow,editable_window,masked_flow_loss,sample_masked_fragment
from latentfold.fragment_conditioning import fragment_features
from latentfold.fragment_geometry_conditioning import fragment_coordinates


class MaskedFlowTests(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(51);self.model=MaskedFragmentFlow(width=16,layers=2,heads=2,max_length=32)
        self.mask=torch.ones(2,32,dtype=torch.bool);self.mask[1,29:]=False
        self.z=torch.nn.functional.layer_norm(torch.randn(2,32,8),(8,))*self.mask[...,None]
        f,k=fragment_features(torch.randn(5,8),'ACDEF',length=32,start=12)
        self.features=f[None].repeat(2,1,1);self.keep=k[None].repeat(2,1)
        c=fragment_coordinates(torch.randn(5,4,3),length=32,start=12)
        self.coords=c[None].repeat(2,1,1);self.noise=torch.randn_like(self.z)

    def sample(self,context=None,coordinates=None,drop=False):
        return sample_masked_fragment(self.model.eval(),self.z if context is None else context,self.features,self.keep,self.mask,self.coords if coordinates is None else coordinates,noise=self.noise,steps=3,flank=2,drop_fragment=drop)

    def test_editable_input_hidden_and_scaffold_exact(self):
        edit=editable_window(self.keep,self.mask,2);self.assertEqual(edit.sum(1).tolist(),[9,9])
        # Nonzero weights ensure this tests the active network, not zero outputs.
        for p in self.model.parameters():torch.nn.init.normal_(p,std=.03)
        before=self.sample();changed=self.z.clone();changed[edit]=99
        self.assertTrue(torch.equal(before,self.sample(changed)))
        self.assertTrue(torch.equal(before[~edit],self.z[~edit]))
        self.assertTrue(torch.equal(before[~self.mask],torch.zeros_like(before[~self.mask])))

    def test_finite_gradient_and_matched_rng(self):
        self.model.train();g=torch.Generator().manual_seed(9)
        loss,info=masked_flow_loss(self.model,self.z,self.features,self.keep,self.mask,self.coords,generator=g,flank=2);loss.backward()
        self.assertTrue(torch.isfinite(loss));self.assertGreater(float(self.model.output.weight.grad.norm()),0)
        other,ii=masked_flow_loss(self.model,self.z,self.features,self.keep,self.mask,self.coords,generator=torch.Generator().manual_seed(9),flank=2)
        self.assertEqual(float(loss.detach()),float(other.detach()))
        for key in ('noise','t','dropped'):self.assertTrue(torch.equal(info[key],ii[key]))

    def test_pose_and_null_condition_invariance(self):
        for p in self.model.parameters():torch.nn.init.normal_(p,std=.03)
        rotation=torch.tensor([[0.,-1,0],[1,0,0],[0,0,1]],dtype=torch.float64)
        posed=(self.coords.double()@rotation+11)*self.keep[...,None]
        torch.testing.assert_close(self.sample(),self.sample(coordinates=posed),rtol=0,atol=1e-5)
        original=self.sample(drop=True);self.features[:,:,:28]*=7;self.coords*=3
        self.assertTrue(torch.equal(original,self.sample(drop=True)))


if __name__=='__main__':unittest.main()
