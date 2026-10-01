import math
import unittest
import torch
from latentfold.flow import SampleConfig,sample


class Field(torch.nn.Module):
    def __init__(self,self_cond=False):
        super().__init__();self.self_cond=self_cond;self.pos=torch.nn.Embedding(8,8);self.calls=[]
    def forward(self,x,t,esm,mask,drop,sc):
        self.calls.append((t.clone(),None if sc is None else sc.clone()))
        return x+(0 if sc is None else .1*sc)


class MidpointTests(unittest.TestCase):
    def run_field(self,model,steps,solver,guidance=1):
        return sample(model.eval(),torch.zeros(1,2,3),torch.ones(1,2,dtype=torch.bool),SampleConfig(steps=steps,guidance=guidance,project=False,solver=solver),noise=torch.ones(1,2,8),cache_condition=False)

    def test_linear_field_accuracy_at_matched_evaluations(self):
        euler,midpoint=Field(),Field()
        a=self.run_field(euler,20,'euler');b=self.run_field(midpoint,10,'midpoint')
        self.assertEqual(len(euler.calls),20);self.assertEqual(len(midpoint.calls),20)
        self.assertLess((b-math.e).abs().max().item(),(a-math.e).abs().max().item()/10)

    def test_self_condition_updates_at_each_evaluation(self):
        model=Field(self_cond=True);value=self.run_field(model,1,'midpoint')
        torch.testing.assert_close(value,torch.full_like(value,2.7))
        torch.testing.assert_close(model.calls[1][0],torch.tensor([.5]))
        torch.testing.assert_close(model.calls[1][1],torch.full((1,2,8),2.))

    def test_guidance_call_count_and_endpoint_not_evaluated(self):
        model=Field();self.run_field(model,8,'midpoint',guidance=2)
        self.assertEqual(len(model.calls),32)
        self.assertLess(max(float(t.max()) for t,sc in model.calls),1.)
        with self.assertRaises(ValueError):SampleConfig(solver='unsupported')


if __name__=='__main__':unittest.main()
