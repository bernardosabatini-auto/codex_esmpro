import unittest
import torch
from test_fragment_decoder_fm import DenoisingTests
from latentfold.fragment_decoder_integrator import decode_steps


class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.fixture=DenoisingTests();self.fixture.setUp();self.x=self.fixture
        for p in self.x.model.parameters():p.requires_grad_(False)
        self.x.model.eval()
        with torch.no_grad():
            for p in self.x.model.adapter.parameters():p.normal_(std=.02)

    def sample(self,steps,**kwargs):
        x=self.x
        return decode_steps(x.model,x.z,x.features,x.keep,x.mask,x.coords,noise=x.noise,steps=steps,**kwargs)

    def test_three_steps_exactly_reproduce_existing_inference_for_both_arms(self):
        x=self.x
        for dropped in (False,True):
            expected=x.model(x.z,x.features,x.keep,x.mask,x.coords,noise=x.noise,drop_fragment=dropped)
            torch.testing.assert_close(self.sample(3,drop_fragment=dropped),expected,atol=0,rtol=0)

    def test_ten_steps_are_reproducible_and_do_not_change_noise_or_weights(self):
        x=self.x;noise=x.noise.clone();weights={k:v.clone() for k,v in x.model.state_dict().items()}
        a=self.sample(10);b=self.sample(10)
        torch.testing.assert_close(a,b,atol=0,rtol=0)
        self.assertTrue(torch.equal(noise,x.noise))
        self.assertTrue(all(torch.equal(v,x.model.state_dict()[k]) for k,v in weights.items()))
        self.assertFalse(torch.equal(a,self.sample(3)))

    def test_ten_step_pose_and_hidden_code_controls(self):
        x=self.x;a=self.sample(10)
        x.z[x.keep]=900
        torch.testing.assert_close(a,self.sample(10),atol=0,rtol=0)
        x.coords=(x.coords.double()@torch.tensor([[0.,-1,0],[1,0,0],[0,0,1]],dtype=torch.float64)+11)*x.keep[...,None]
        torch.testing.assert_close(a,self.sample(10),atol=1e-5,rtol=0)

    def test_undeclared_schedule_and_padding_rejected(self):
        for s in (0,1,5,30):
            with self.assertRaises(ValueError):self.sample(s)
        self.x.mask[0,-1]=False
        with self.assertRaises(ValueError):self.sample(10)


if __name__=='__main__':unittest.main()
