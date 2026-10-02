import unittest
from unittest.mock import patch
import torch
from torch.nn import functional as F
from latentfold.fragment_conditioning import sample_fragment
from fragment_refinement_core import choose_refold


class ConstantNet(torch.nn.Module):
    self_cond=True
    def __init__(self,velocity):
        super().__init__();self.velocity=velocity;self.inputs=[];self.eval()
    def forward(self,x,t,esm,mask,x_sc=None,prepared=None):
        self.inputs.append((x.clone(),t.clone(),None if x_sc is None else x_sc.clone()))
        return self.velocity


class RefinementTests(unittest.TestCase):
    def test_partial_integration_analytic_and_padding(self):
        torch.manual_seed(4);noise=torch.randn(1,5,8);reference=torch.randn_like(noise);velocity=torch.randn_like(noise)
        mask=torch.tensor([[True,True,True,False,False]]);net=ConstantNet(velocity);adapter=torch.nn.Identity().eval()
        with patch('latentfold.fragment_conditioning.prepare_fragment_condition',return_value=(None,None)):
            got=sample_fragment(net,adapter,None,None,mask,noise=noise,steps=4,reference=reference,start_time=.8)
        initial=.8*reference+.2*noise
        torch.testing.assert_close(net.inputs[0][0],initial,atol=0,rtol=0)
        self.assertIsNone(net.inputs[0][2]);self.assertEqual(len(net.inputs),4)
        torch.testing.assert_close(got,F.layer_norm(initial+.2*velocity,(8,))*mask[...,None],atol=1e-6,rtol=1e-6)
        self.assertTrue((got[~mask]==0).all())

    def test_zero_time_matches_previous_arithmetic_and_rng(self):
        torch.manual_seed(2);noise=torch.randn(1,5,8);v=torch.randn_like(noise);net=ConstantNet(v);mask=torch.ones(1,5,dtype=torch.bool);state=torch.get_rng_state()
        with patch('latentfold.fragment_conditioning.prepare_fragment_condition',return_value=(None,None)):
            got=sample_fragment(net,torch.nn.Identity().eval(),None,None,mask,noise=noise,steps=7,reference=noise*3,start_time=0.)
        x=noise.clone();ts=torch.linspace(0,1,8)
        for i in range(7):x=x+(ts[i+1]-ts[i])*v
        torch.testing.assert_close(got,F.layer_norm(x,(8,)),atol=0,rtol=0)
        self.assertTrue(torch.equal(state,torch.get_rng_state()))
        for kwargs in ({'start_time':1.},{'start_time':float('nan')},{'start_time':.8},{'reference':noise[:,:,:7]}):
            with self.assertRaises(ValueError):sample_fragment(net,torch.nn.Identity().eval(),None,None,mask,noise=noise,**kwargs)

    def test_selection_uses_only_valid_supplied_motif_metrics(self):
        def row(k,rmsd,tm,valid=True):return dict(sequence_index=k,motif_ca_rmsd=rmsd,motif_drms=.5,sc_tm=tm,coarse_valid=valid)
        rows=[row(0,.1,.9,False),row(1,.7,.6),row(2,.8,.95),row(3,.7,.7)]
        self.assertEqual(choose_refold(rows),3)
        self.assertIsNone(choose_refold([rows[0]]))
