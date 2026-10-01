import unittest
import torch
from latentfold.conditioning import ResidualConditioner


class ConditioningTests(unittest.TestCase):
    def test_zero_initialization_is_exact_and_residual_bounded(self):
        torch.manual_seed(1);mask=torch.tensor([[True,True,False]]);layers={k:torch.randn(1,3,2560)*mask[...,None] for k in (20,40,60,80)}
        for arm in ('final','layer60','mixture'):
            model=ResidualConditioner(arm,width=4)
            self.assertTrue(torch.equal(model(layers,mask),layers[80]))
            model.up.weight.data.normal_()
            value,residual=model(layers,mask,return_residual=True)
            self.assertLessEqual(float(residual.detach().abs().max()),.100001)
            self.assertTrue(torch.equal(value[:,2],torch.zeros_like(value[:,2])))
            loss=value.square().mean();loss.backward()
            self.assertGreater(float(model.down.weight.grad.norm()),0)
            if model.logits is not None:self.assertGreater(float(model.logits.grad.norm()),0)


if __name__=='__main__':unittest.main()
