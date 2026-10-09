import unittest
from unittest.mock import patch
import torch
from torch import nn
from latentfold.trajectory_guidance import sample


class Dummy(nn.Module):
    self_cond=True


class TrajectoryGuidanceTests(unittest.TestCase):
    def run_sample(self,strength):
        torch.manual_seed(6);noise=torch.randn(2,7,8,dtype=torch.float64);mask=torch.ones(2,7,dtype=torch.bool);mask[1,-1]=False
        model=Dummy().eval();rows=[]
        def velocity(net,adapter,x,t,*args,**kw):return .2*x+.1 if kw['x_sc'] is None else .2*x+.05*kw['x_sc']+.1
        with patch('latentfold.trajectory_guidance.prepare_fragment_condition',return_value=(None,None)),patch('latentfold.trajectory_guidance.fragment_velocity',side_effect=velocity):
            out=sample(model,model,None,None,mask,noise=noise,coordinates=None,objective=lambda z:z[:,:,0].square().mean(1),strength=strength,steps=8,first=3,stop=6,observe=lambda *args:rows.append(args))
        return noise,mask,out,rows

    def test_zero_guidance_matches_prior_and_history_detaches(self):
        noise,mask,out,rows=self.run_sample(0);x=noise;history=None;ts=torch.linspace(0,1,9,dtype=noise.dtype)
        for i in range(8):
            v=(.2*x+.1 if history is None else .2*x+.05*history+.1).float()
            history=x+(1-ts[i])*v;x=x+(ts[i+1]-ts[i])*v
        self.assertTrue(torch.equal(out,torch.nn.functional.layer_norm(x,(8,))*mask[...,None]))
        self.assertTrue(all(not r[1].requires_grad and not r[4].requires_grad for r in rows))

    def test_only_declared_steps_have_masked_unit_gradient(self):
        _,mask,out,rows=self.run_sample(.5)
        for i,x,v,d,y,loss,w,t,dt in rows:
            self.assertTrue(torch.equal(y,x+dt*(v-w*d)))
            if 3<=i<6:
                torch.testing.assert_close((d.square().sum((1,2))/(8*mask.sum(1))).sqrt(),torch.ones(2,dtype=d.dtype))
                self.assertEqual(float(d[~mask].abs().max()),0.)
            else:self.assertEqual(w,0.);self.assertIsNone(loss)
        self.assertTrue(torch.isfinite(out).all())
