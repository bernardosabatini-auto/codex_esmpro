import unittest
import torch
from torch import nn
from latentfold.flow import FlowConfig, flow_loss


class Velocity(nn.Module):
    self_cond = False

    def __init__(self):
        super().__init__()
        self.scale = nn.Parameter(torch.tensor(0.3))

    def forward(self, x, t, esm, mask, drop, sc):
        return x * self.scale


class ReflowTests(unittest.TestCase):
    def test_pair_coupling_gradient_and_rng(self):
        z = torch.ones(2, 5, 8)
        noise = torch.full_like(z, -2)
        esm = torch.zeros(2, 5, 12)
        mask = torch.ones(2, 5, dtype=torch.bool)
        cfg = FlowConfig(repeats=2, condition_dropout=0, uniform_fraction=.5)
        g1 = torch.Generator().manual_seed(7)
        g2 = torch.Generator().manual_seed(7)
        net = Velocity()
        paired, p = flow_loss(net, z, esm, mask, cfg, generator=g1,
                              initial_noise=noise, return_state=True)
        independent, q = flow_loss(net, z, esm, mask, cfg, generator=g2, return_state=True)
        torch.testing.assert_close(g1.get_state(), g2.get_state(), rtol=0, atol=0)
        torch.testing.assert_close(p['state']['t'], q['state']['t'], rtol=0, atol=0)
        t = p['state']['t'][:, None, None]
        expected = -2 * (1-t) + t
        torch.testing.assert_close(p['state']['x'], expected.expand(4, 5, 8))
        torch.testing.assert_close(paired, ((expected * net.scale - 3)**2).mean())
        self.assertNotEqual(float(paired.detach()), float(independent.detach()))
        paired.backward()
        self.assertTrue(torch.isfinite(net.scale.grad))
        self.assertGreater(float(net.scale.grad.abs()), 0)

    def test_paired_noise_validation(self):
        z = torch.ones(1, 3, 8)
        for bad in (torch.ones(1, 2, 8), z.clone().requires_grad_(), z * float('nan')):
            with self.assertRaises(ValueError):
                flow_loss(Velocity(), z, torch.zeros(1, 3, 12), torch.ones(1, 3, dtype=torch.bool),
                          FlowConfig(), generator=torch.Generator(), initial_noise=bad)


if __name__ == '__main__':
    unittest.main()
