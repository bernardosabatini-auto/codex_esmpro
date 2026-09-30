import unittest
import torch
from latentfold.flow import flow_loss, FlowConfig
from latentfold.quality import confidence_weights


class Table(torch.nn.Module):
    self_cond = False

    def __init__(self):
        super().__init__()
        self.value = torch.nn.Parameter(torch.ones(2, 4, 8))

    def forward(self, *args, **kwargs):
        return self.value


class QualityTests(unittest.TestCase):
    def test_weights_scale_each_residue_gradient_without_changing_random_draws(self):
        model = Table(); z = torch.zeros(2, 4, 8); esm = torch.zeros(2, 4, 3)
        mask = torch.tensor([[1, 1, 0, 0], [1, 1, 1, 1]], dtype=torch.bool)
        weights = torch.tensor([[.2, 1.8, 0, 0], [.3, .8, 1.1, 1.8]])
        cfg = FlowConfig()
        a = torch.Generator().manual_seed(9); b = torch.Generator().manual_seed(9)
        plain, _ = flow_loss(model, z, esm, mask, cfg, generator=a)
        grad = torch.autograd.grad(plain, model.value)[0]
        weighted, _ = flow_loss(model, z, esm, mask, cfg, generator=b, residue_weights=weights)
        actual = torch.autograd.grad(weighted, model.value)[0]
        torch.testing.assert_close(actual, grad*weights[..., None])
        self.assertTrue(torch.equal(a.get_state(), b.get_state()))
        same, _ = flow_loss(model, z, esm, mask, cfg, generator=torch.Generator().manual_seed(9), residue_weights=torch.ones_like(weights))
        torch.testing.assert_close(same, plain, rtol=0, atol=0)
        with self.assertRaises(ValueError):
            flow_loss(model, z, esm, mask, cfg, generator=b, residue_weights=torch.zeros_like(weights))

    def test_confidence_rule_preserves_low_confidence_examples(self):
        actual = confidence_weights(torch.tensor([0., 50., 70., 90., 100.]), .5)
        torch.testing.assert_close(actual, torch.tensor([.1, .1, 1., 2., 2.]))
        with self.assertRaises(ValueError):
            confidence_weights(torch.tensor([float('nan')]))
