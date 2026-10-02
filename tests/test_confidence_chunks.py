import unittest
from types import SimpleNamespace
import torch
from confidence_chunks import chunk_confidence


class Head(torch.nn.Module):
    def forward(self,**kw):
        x=kw['predicted_coords'].reshape(-1,2,3)
        return dict(plddt=x.mean((1,2))[:,None],pae=x.square())


class ConfidenceChunksTests(unittest.TestCase):
    def test_order_remainder_and_restoration(self):
        model=SimpleNamespace(confidence_head=Head());args=dict(single_inputs=torch.ones(1,3,4),predicted_coords=torch.arange(66.).reshape(11,2,3),num_diffusion_samples=11);original=model.confidence_head.forward;expected=original(**args)
        with chunk_confidence(model,4):
            actual=model.confidence_head(**args)
            for k in expected:self.assertTrue(torch.equal(expected[k],actual[k]))
        self.assertEqual(model.confidence_head.forward,original)
    def test_ambiguous_batch_rejected_and_method_restored_on_error(self):
        model=SimpleNamespace(confidence_head=Head());original=model.confidence_head.forward
        with self.assertRaises(ValueError),chunk_confidence(model,4):model.confidence_head(single_inputs=torch.ones(2,3,4),predicted_coords=torch.ones(16,2,3),num_diffusion_samples=8)
        self.assertEqual(model.confidence_head.forward,original)


if __name__=='__main__':unittest.main()
