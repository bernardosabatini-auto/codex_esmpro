import unittest
import torch
from latentfold.posterior_targets import empirical_velocity


class PosteriorTargetTests(unittest.TestCase):
    def test_flow_single_teacher_matches_loss_gradient_and_rng(self):
        from latentfold.flow import FlowConfig, flow_loss
        class Net(torch.nn.Module):
            self_cond = True
            def __init__(self):
                super().__init__()
                self.scale = torch.nn.Parameter(torch.tensor(.2))
            def forward(self, x, t, esm, mask, drop, sc):
                return self.scale*x + (0 if sc is None else .1*sc)
        torch.manual_seed(18)
        z, esm = torch.randn(2, 3, 8), torch.randn(2, 3, 4)
        mask = torch.tensor([[1, 1, 0], [1, 1, 1]], dtype=torch.bool)
        cfg = FlowConfig(repeats=2, self_condition_probability=1.)
        ordinary, averaged = Net(), Net()
        g1, g2 = [torch.Generator().manual_seed(42) for _ in range(2)]
        a, ai = flow_loss(ordinary, z, esm, mask, cfg, generator=g1, return_state=True)
        b, bi = flow_loss(averaged, z, esm, mask, cfg, generator=g2, return_state=True,
                          teacher_bank=z[:, None], teacher_valid=torch.ones(2, 1, dtype=torch.bool))
        torch.testing.assert_close(a, b)
        a.backward(); b.backward()
        torch.testing.assert_close(ordinary.scale.grad, averaged.scale.grad)
        self.assertTrue(torch.equal(g1.get_state(), g2.get_state()))
        for key in ('velocity', 'x', 't', 'dropped', 'mask'):
            self.assertTrue(torch.equal(ai['state'][key], bi['state'][key]))

    def test_conditional_loss_and_gradient_identity(self):
        # Both teacher/noise pairs yield x=.2 at t=.5. Their posterior weights
        # differ, so this checks likelihood weighting as well as target variance.
        bank = torch.tensor([[[[-1.]], [[1.]]]], dtype=torch.float64)
        selected = bank[:, 0]
        noise = torch.tensor([[[1.4]]], dtype=torch.float64)
        t = torch.tensor([.5], dtype=torch.float64)
        mean, variance = empirical_velocity(selected, noise, t, bank,
                                             torch.ones(1, 1, dtype=torch.bool),
                                             torch.ones(1, 2, dtype=torch.bool))
        x = (1-t[:, None, None])*noise + t[:, None, None]*selected
        conditional_noise = (x[:, None]-t[:, None, None, None]*bank)/(1-t[:, None, None, None])
        weights = (-.5*conditional_noise.square().sum((2, 3))).softmax(1)
        velocities = bank-conditional_noise
        prediction = torch.tensor([[[.37]]], dtype=torch.float64, requires_grad=True)
        original = (weights[:, :, None, None]*(prediction[:, None]-velocities).square()).sum()
        averaged = ((prediction-mean).square()+variance).sum()
        torch.testing.assert_close(original, averaged, atol=1e-12, rtol=1e-12)
        a = torch.autograd.grad(original, prediction)[0]
        b = torch.autograd.grad(averaged, prediction)[0]
        torch.testing.assert_close(a, b, atol=1e-12, rtol=1e-12)

    def test_single_teacher_late_time_and_padding(self):
        torch.manual_seed(8)
        z, noise = torch.randn(2, 3, 8), torch.randn(2, 3, 8)
        bank = z[:, None].repeat(1, 2, 1, 1)
        bank[:, 1] = 1e4  # Excluded teacher must not affect posterior.
        mask = torch.tensor([[1, 1, 0], [1, 0, 0]], dtype=torch.bool)
        valid = torch.tensor([[1, 0], [1, 0]], dtype=torch.bool)
        mean, variance = empirical_velocity(z, noise, torch.tensor([0., .9999]), bank, mask, valid)
        torch.testing.assert_close(mean, (z-noise)*mask[:, :, None])
        self.assertEqual(variance.abs().max().item(), 0.)

    def test_zero_time_prior_and_missing_label(self):
        bank = torch.tensor([[[[-1.]], [[1.]]]])
        mask, valid = torch.ones(1, 1, dtype=torch.bool), torch.ones(1, 2, dtype=torch.bool)
        mean, variance = empirical_velocity(bank[:, 0], torch.zeros(1, 1, 1), torch.zeros(1), bank, mask, valid)
        torch.testing.assert_close(mean, torch.zeros_like(mean))
        torch.testing.assert_close(variance, torch.ones_like(variance))
        with self.assertRaises(ValueError):
            empirical_velocity(torch.zeros(1, 1, 1), torch.zeros(1, 1, 1), torch.zeros(1), bank, mask, valid)
