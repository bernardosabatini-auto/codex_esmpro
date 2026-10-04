import unittest
import torch
from test_fragment_inpainting import InpaintingTests
from latentfold.inpainting_integrator import decode_steps


class IntegratorTests(unittest.TestCase):
    setUp=InpaintingTests.setUp
    model_inputs=InpaintingTests.model_inputs
    def test_three_step_exact_and_ten_step_keeps_anchors(self):
        _,model,z,features,mask,coords,anchors=self.model_inputs();model.eval()
        expected=model(z,features,self.keep,mask,coords,anchors=anchors,noise=self.noise)
        actual=decode_steps(model,z,features,self.keep,mask,coords,anchors=anchors,noise=self.noise,steps=3)
        torch.testing.assert_close(expected,actual,rtol=0,atol=0)
        ten=decode_steps(model,z,features,self.keep,mask,coords,anchors=anchors,noise=self.noise,steps=10)
        torch.testing.assert_close(ten[self.keep],anchors[self.keep],rtol=0,atol=2e-6)
        torch.testing.assert_close(ten.mean((1,2)),torch.zeros(2,3),rtol=0,atol=2e-6)
        with self.assertRaises(ValueError):decode_steps(model,z,features,self.keep,mask,coords,anchors=anchors,noise=self.noise,steps=20)
