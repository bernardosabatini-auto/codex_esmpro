import unittest
from types import SimpleNamespace
import torch
from latentfold.neighbor_branch import capture_neighbors,fixed_neighbors


class Features:
    def _dist(self,x,mask,eps=1e-6):
        mask2=mask[:,:,None]*mask[:,None,:];d=mask2*torch.sqrt((x[:,None]-x[:,:,None]).square().sum(-1)+eps);d=d+(1-mask2)*d.max(-1,keepdim=True).values
        return torch.topk(d,3,dim=-1,largest=False)


class BranchTests(unittest.TestCase):
    def test_reference_forward_and_gradient_match(self):
        torch.manual_seed(18);x=torch.randn(2,8,3,dtype=torch.float64,requires_grad=True);mask=torch.ones(2,8,dtype=x.dtype);mask[1,-1]=0;model=SimpleNamespace(features=Features())
        with capture_neighbors(model) as state:values,_=model.features._dist(x,mask)
        original_grad,=torch.autograd.grad(values.sum(),x)
        with fixed_neighbors(model,state['indices']):
            fixed,idx=model.features._dist(x,mask);g,=torch.autograd.grad(fixed.sum(),x)
            self.assertTrue(torch.equal(values,fixed));torch.testing.assert_close(g,original_grad,atol=1e-12,rtol=0)
        self.assertTrue(torch.equal(model.features._dist(x,mask)[0],values))

    def test_original_restored_after_failure(self):
        model=SimpleNamespace(features=Features());original=model.features._dist
        with self.assertRaises(RuntimeError):
            with fixed_neighbors(model,torch.zeros(1,1,1,dtype=torch.long)):raise RuntimeError('failed control')
        self.assertEqual(model.features._dist,original)
