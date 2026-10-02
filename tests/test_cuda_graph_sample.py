import unittest
import torch
from cuda_graph_sample import flow_body,validate
from latentfold.flow import sample,SampleConfig
from latentfold.pair_model import PairFlowNet


class GraphBodyTests(unittest.TestCase):
    def test_cpu_arithmetic_matches_compact_reference_with_mask_and_new_inputs(self):
        torch.manual_seed(38)
        net=PairFlowNet(d_model=16,n_layers=2,n_heads=2,d_cond=6,d_pair=4,n_pair_blocks=1,max_len=8).eval()
        # Nonzero field; default zero output initialization would hide errors.
        torch.nn.init.normal_(net.out_proj.weight,std=.1)
        with torch.no_grad():
            for k in (1,4):
                for n in (5,8):
                    esm=torch.randn(1,8,6);mask=torch.arange(8)[None]<n;noise=torch.randn(k,8,8)
                    expected=sample(net,esm.repeat(k,1,1),mask.repeat(k,1),SampleConfig(25,1),noise=noise,conditioning_ids=['same']*k,compact_condition=True)
                    actual=flow_body(net,esm,mask,noise)
                    self.assertTrue(torch.equal(actual,expected));self.assertTrue(torch.equal(actual[:,n:],torch.zeros_like(actual[:,n:])))

    def test_invalid_batch_dtype_and_noise_rejected(self):
        esm=torch.zeros(1,8,6);mask=torch.ones(1,8,dtype=torch.bool);noise=torch.zeros(4,8,8)
        validate(esm,mask,noise)
        for e,m,z in [(esm.repeat(2,1,1),mask.repeat(2,1),noise),(esm.double(),mask,noise),(esm,mask,noise[:,:,:7]),(esm,mask,noise+float('nan'))]:
            with self.assertRaises(ValueError):validate(e,m,z)


if __name__=='__main__':unittest.main()
