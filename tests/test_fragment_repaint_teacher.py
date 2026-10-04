import unittest
import torch
from test_generative import GenerativeTests
from latentfold.generative import sample_unconditional
from fragment_repaint_teacher_core import eligibility


class TeacherInputs(GenerativeTests):
    def test_scaffold_codes_do_not_enter_sampler(self):
        keep=torch.zeros_like(self.mask);keep[:,1:3]=True
        motif=torch.randn_like(self.noise);other=torch.where(keep[...,None],motif,torch.ones_like(motif)*100)
        eps=torch.randn_like(self.noise)
        kw=dict(noise=self.noise,steps=3,motif_noise=eps,repaint=3,fresh_noise=lambda i,j:eps*(i+j+1))
        a=sample_unconditional(self.net,self.esm,self.mask,fixed=(motif,keep),**kw)
        b=sample_unconditional(self.net,self.esm,self.mask,fixed=(other,keep),**kw)
        torch.testing.assert_close(a,b,rtol=0,atol=0)
        changed=motif.clone();changed[keep]=0
        d=sample_unconditional(self.net,self.esm,self.mask,fixed=(changed,keep),**kw)
        self.assertGreater(float((a-d).abs().max()),0)


class TeacherEligibility(unittest.TestCase):
    def test_logical_upperbounds_require_full_population(self):
        rows=[dict(target_id=str(i//4),generation_slot=i%4,raw_gate_passed=i<9,coarse_valid=i<45) for i in range(128)]
        self.assertTrue(eligibility(rows)['qualified'])
        rows[8]['raw_gate_passed']=False
        self.assertFalse(eligibility(rows)['qualified'])
        with self.assertRaises(ValueError):eligibility(rows[:-1])
        with self.assertRaises(ValueError):eligibility(rows[:-1]+[rows[0]])


if __name__=='__main__':unittest.main()
