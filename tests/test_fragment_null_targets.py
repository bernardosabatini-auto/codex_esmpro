import unittest
import torch
from latentfold.pair_model import PairFlowNet
from latentfold.fragment_conditioning import FragmentAdapter,fragment_features,fragment_flow_loss


class NullTargetTests(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(63);self.net=PairFlowNet(d_model=16,n_layers=1,n_heads=2,d_cond=12,d_pair=4,n_pair_blocks=1,max_len=16).eval();self.adapter=FragmentAdapter(16,12).eval();ff,kk=fragment_features(torch.randn(3,8),'ACD',length=7,start=2);self.features=ff[None].repeat(64,1,1);self.keep=kk[None].repeat(64,1);self.mask=torch.ones(64,7,dtype=torch.bool);self.target=torch.randn(64,7,8);self.original=torch.randn_like(self.target)

    def loss(self,**kwargs):
        return fragment_flow_loss(self.net,self.adapter,self.target,self.features,self.keep,self.mask,generator=torch.Generator().manual_seed(41),return_state=True,**kwargs)

    def test_null_examples_use_original_targets_without_changing_draws(self):
        _,base=self.loss();_,new=self.loss(null_target=self.original)
        for key in ['noise','t','dropped']:self.assertTrue(torch.equal(base[key],new[key]))
        self.assertEqual(base['self_conditioned'],new['self_conditioned']);self.assertTrue(new['dropped'].any());self.assertTrue((~new['dropped']).any())
        expected=torch.where(new['dropped'][:,None,None],self.original,self.target);self.assertTrue(torch.equal(new['target'],expected));tt=new['t'][:,None,None];torch.testing.assert_close(new['state']['x'],(1-tt)*new['noise']+tt*expected,atol=0,rtol=0)

    def test_identical_null_target_preserves_original_loss(self):
        before,_=self.loss();after,_=self.loss(null_target=self.target);torch.testing.assert_close(before,after,atol=0,rtol=0)
        with self.assertRaises(ValueError):self.loss(null_target=self.original.requires_grad_())


if __name__=='__main__':unittest.main()
