import unittest
import torch
from latentfold.checkpoint_blend import blend_states,architecture

class BlendTests(unittest.TestCase):
    def test_endpoints_midpoint_and_no_mutation(self):
        a={'_orig_mod.weight':torch.tensor([1.,-4.]),'count':torch.tensor(2)};b={'weight':torch.tensor([5.,8.]),'count':torch.tensor(2)}
        for alpha,expected in ((0,[1.,-4.]),(.5,[3.,2.]),(1,[5.,8.])):
            out=blend_states(a,b,alpha);torch.testing.assert_close(out['weight'],torch.tensor(expected),rtol=0,atol=0)
        torch.testing.assert_close(a['_orig_mod.weight'],torch.tensor([1.,-4.]),rtol=0,atol=0)
    def test_reject_incompatible_or_nonfinite_states(self):
        a={'x':torch.tensor([1.])}
        for b in ({'y':torch.tensor([1.])},{'x':torch.ones(2)},{'x':torch.ones(1,dtype=torch.float64)},{'x':torch.tensor([float('nan')])}):
            with self.assertRaises(ValueError):blend_states(a,b,.5)
        with self.assertRaises(ValueError):blend_states({'x':torch.tensor(1)},{'x':torch.tensor(2)},.5)
        with self.assertRaises(ValueError):blend_states({'x':torch.ones(1),'_orig_mod.x':torch.ones(1)},a,.5)
        for alpha in (-1,2,float('nan'),True):
            with self.assertRaises(ValueError):blend_states(a,a,alpha)
    def test_metadata_normalizes_position_table_and_inactive_recycling(self):
        p=dict(ema={'pos.weight':torch.zeros(12,3)},arch=dict(d_model=3),extra_arch=dict(recycle=False,p_rec=.5),model='PairFlowNet')
        self.assertEqual(architecture(p),dict(arch=dict(d_model=3,max_len=12),extra_arch={},model='PairFlowNet'))

if __name__=='__main__':unittest.main()
