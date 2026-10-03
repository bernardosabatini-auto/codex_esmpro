import copy
import unittest
import torch
from latentfold.anchored_preference import anchored_branch_loss


class AnchoredPreferenceTests(unittest.TestCase):
    def fields(self):
        p=torch.zeros(1,2,8,requires_grad=True);n=torch.zeros_like(p,requires_grad=True)
        ref=torch.zeros_like(p);target=torch.ones_like(p);mask=torch.tensor([[True,False]])
        return p,n,ref,target,mask

    def test_opposing_gradients_and_padding_exclusion(self):
        p,n,ref,target,mask=self.fields()
        loss,_=anchored_branch_loss(p,ref,target,n,ref,target,mask)
        self.assertEqual(float(loss.detach()),2.);loss.backward()
        torch.testing.assert_close(p.grad[0,0],torch.full((8,),-.125))
        torch.testing.assert_close(n.grad[0,0],torch.full((8,),.125))
        self.assertEqual(float(p.grad[0,1].abs().sum()+n.grad[0,1].abs().sum()),0.)

    def test_positive_only_retains_positive_gradient(self):
        p,n,ref,target,mask=self.fields()
        loss,_=anchored_branch_loss(p,ref,target,n,ref,target,mask,negative_weight=0.)
        self.assertEqual(float(loss.detach()),1.);loss.backward()
        torch.testing.assert_close(p.grad[0,0],torch.full((8,),-.125))
        self.assertEqual(float(n.grad.abs().sum()),0.)

    def test_nonnegative_even_for_large_current_field(self):
        p,n,ref,target,mask=self.fields()
        loss,_=anchored_branch_loss(p+1000,ref,target,n-1000,ref,target,mask)
        self.assertTrue(torch.isfinite(loss));self.assertGreaterEqual(float(loss.detach()),0.)

    def test_paired_draws_frozen_reference_and_unchanged_null(self):
        from latentfold.pair_model import PairFlowNet
        from latentfold.fragment_conditioning import fragment_features,sample_fragment
        from latentfold.fragment_geometry_conditioning import FragmentGeometryAdapter,fragment_coordinates
        from latentfold.anchored_preference import native_preference_flow_loss
        torch.manual_seed(15)
        net=PairFlowNet(d_model=16,n_layers=2,n_heads=2,d_cond=12,d_pair=4,n_pair_blocks=1,max_len=12)
        with torch.no_grad():
            for p in net.parameters():p.normal_(0,.1)
        net.requires_grad_(False);net.checkpoint_blocks=True
        adapter=FragmentGeometryAdapter(16,n_layers=2,n_heads=2,distance_precision='fp64')
        reference=copy.deepcopy(adapter).requires_grad_(False).eval()
        other=copy.deepcopy(adapter);f,k=fragment_features(torch.randn(3,8),'ACD',length=7,start=2)
        f,k=f[None],k[None];mask=torch.ones_like(k)
        coords=fragment_coordinates(torch.randn(3,4,3),length=7,start=2)[None]
        positive,negative=torch.randn(1,7,8),torch.randn(1,7,8)
        saved={k:v.clone() for k,v in reference.state_dict().items()}
        net.eval();adapter.eval();noise=torch.randn(1,7,8)
        before=sample_fragment(net,adapter,f,k,mask,noise=noise,coordinates=coords,drop_fragment=True,steps=4)
        net.train();adapter.train();other.train()
        loss,first=native_preference_flow_loss(net,adapter,reference,positive,negative,f,k,mask,coordinates=coords,generator=torch.Generator().manual_seed(31))
        control,second=native_preference_flow_loss(net,other,reference,positive,negative,f,k,mask,coordinates=coords,generator=torch.Generator().manual_seed(31),negative_weight=0.)
        for key in ('noise','t'):torch.testing.assert_close(first[key],second[key],rtol=0,atol=0)
        self.assertEqual(first['self_conditioned'],second['self_conditioned'])
        loss.backward()
        self.assertTrue(all(p.grad is None for p in net.parameters()))
        self.assertTrue(all(p.grad is None for p in reference.parameters()))
        self.assertGreater(float(adapter.output.weight.grad.norm()),0.)
        torch.optim.SGD(adapter.parameters(),lr=.01).step()
        for key,value in reference.state_dict().items():torch.testing.assert_close(value,saved[key],rtol=0,atol=0)
        net.eval();adapter.eval()
        after=sample_fragment(net,adapter,f,k,mask,noise=noise,coordinates=coords,drop_fragment=True,steps=4)
        torch.testing.assert_close(before,after,rtol=0,atol=0)

    def test_fixed_reference_and_valid_parameters(self):
        p,n,ref,target,mask=self.fields()
        with self.assertRaises(ValueError):anchored_branch_loss(p,ref.requires_grad_(),target,n,ref,target,mask)
        ref=ref.detach()
        for kwargs in (dict(beta=0),dict(negative_weight=-1),dict(beta=float('nan'))):
            with self.assertRaises(ValueError):anchored_branch_loss(p,ref,target,n,ref,target,mask,**kwargs)


if __name__=='__main__':unittest.main()
