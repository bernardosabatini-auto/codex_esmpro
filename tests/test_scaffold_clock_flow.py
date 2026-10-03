import unittest
from types import SimpleNamespace
from unittest.mock import patch

import torch
from torch.nn import functional as F

from latentfold.pair_model import PairFlowNet
from latentfold.fragment_geometry_conditioning import FragmentGeometryAdapter, fragment_coordinates
from latentfold.fragment_conditioning import fragment_features, sample_fragment
from latentfold.scaffold_clock_flow import ScaffoldClockFlow, clock_offsets, scaffold_clock_loss, sample_scaffold_clock


class ScaffoldClockTests(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(52)
        net = PairFlowNet(d_model=16, n_layers=2, n_heads=2, d_cond=12, d_pair=4, n_pair_blocks=1, max_len=32)
        adapter = FragmentGeometryAdapter(16, n_layers=2, n_heads=2, hidden=8, pair_hidden=4, distance_precision='fp64')
        for p in list(net.parameters()) + list(adapter.parameters()):
            torch.nn.init.normal_(p, std=.03)
        self.model = ScaffoldClockFlow(net, adapter, 53).eval()
        self.mask = torch.ones(2, 32, dtype=torch.bool)
        self.mask[1, 30:] = False
        self.z = torch.randn(2, 32, 8) * self.mask[..., None]
        self.noise = torch.randn_like(self.z)
        f, k = fragment_features(torch.randn(5, 8), 'ACDEF', length=32, start=10)
        self.features, self.keep = f[None].repeat(2, 1, 1), k[None].repeat(2, 1)
        self.coords = fragment_coordinates(torch.randn(5, 4, 3), length=32, start=10)[None].repeat(2, 1, 1)

    def sample(self, context=None, **kwargs):
        return sample_scaffold_clock(self.model.eval(), self.z if context is None else context,
                                     self.features, self.keep, self.mask, self.coords,
                                     noise=self.noise, steps=3, flank=2, **kwargs)

    def test_zero_clock_matches_original_parent_and_ignores_context(self):
        expected = sample_fragment(self.model.net, self.model.fragment, self.features, self.keep,
                                   self.mask, noise=self.noise, steps=3, coordinates=self.coords)
        self.assertTrue(torch.equal(self.sample(scaffold_start=0), expected))
        other = torch.randn_like(self.z) * self.mask[..., None]
        self.assertTrue(torch.equal(self.sample(scaffold_start=0), self.sample(other, scaffold_start=0)))

    def test_no_motif_endpoint_leak_and_scaffold_is_free_to_move(self):
        for p in self.model.clock.parameters():
            torch.nn.init.normal_(p, std=.03)
        _, window = clock_offsets(self.keep, self.mask, .5, 2)
        z = self.sample()
        other = self.z.clone()
        other[window] = 88
        self.assertTrue(torch.equal(z, self.sample(other)))
        self.assertFalse(torch.equal(z[self.mask & ~window], self.z[self.mask & ~window]))
        self.assertTrue(torch.equal(z[~self.mask], torch.zeros_like(z[~self.mask])))
        posed = (self.coords.double() @ torch.tensor([[0., -1, 0], [1, 0, 0], [0, 0, 1]], dtype=torch.float64) + 11) * self.keep[..., None]
        rotated = sample_scaffold_clock(self.model, self.z, self.features, self.keep, self.mask,
                                       posed, noise=self.noise, steps=3, flank=2)
        torch.testing.assert_close(z, rotated, rtol=0, atol=1e-5)

    def test_exact_velocity_reaches_endpoint_and_history_uses_local_clock(self):
        endpoint = self.z
        velocity = (endpoint - self.noise) * self.mask[..., None]
        histories = []
        class Oracle:
            training = False
            net = SimpleNamespace(self_cond=True)
            def prepare(self, *args):
                return None
            def __call__(self, x, t, mask, alpha, prepared, history=None):
                if history is not None:
                    histories.append(history)
                return velocity
        result = sample_scaffold_clock(Oracle(), endpoint, self.features, self.keep, self.mask,
                                       self.coords, noise=self.noise, steps=7, flank=2)
        torch.testing.assert_close(result, F.layer_norm(endpoint, (8,)) * self.mask[..., None], rtol=0, atol=1e-6)
        self.assertEqual(len(histories), 6)
        for history in histories:
            torch.testing.assert_close(history, endpoint, rtol=0, atol=1e-6)

    def test_training_clock_gradient_and_frozen_weights(self):
        self.model.train()
        loss, info = scaffold_clock_loss(self.model, self.z, self.features, self.keep, self.mask,
                                        self.coords, generator=torch.Generator().manual_seed(4),
                                        flank=2, de_novo_probability=0)
        loss.backward()
        self.assertGreater(float(self.model.clock.output.weight.grad.norm()), 0)
        self.assertTrue((info['alpha'][info['window']] == 0).all())
        self.assertTrue((info['alpha'][self.mask & ~info['window']] == .5).all())
        for name, p in self.model.named_parameters():
            if name in self.model.frozen_names:
                self.assertIsNone(p.grad)

    def test_training_oracle_loss_and_self_conditioning(self):
        # Captured random path lets an analytical endpoint oracle test the loss
        # and local-clock self-conditioning without duplicating network code.
        self.model.train()
        histories = []
        alpha_seen = []
        def oracle(x, t, mask, alpha, prepared, history=None):
            local_t = alpha + (1 - alpha) * t[:, None]
            v = (self.z - x) / (1 - local_t[..., None])
            alpha_seen.append(alpha)
            if history is not None:
                histories.append(history)
            return v
        for seed in range(8):
            with patch.object(self.model, 'forward', side_effect=oracle):
                loss, info = scaffold_clock_loss(self.model, self.z, self.features, self.keep, self.mask,
                                                self.coords, generator=torch.Generator().manual_seed(seed), flank=2)
            self.assertLess(float(loss), 1e-10)
        self.assertTrue(histories)
        for h in histories:
            torch.testing.assert_close(h, self.z, rtol=0, atol=1e-6)
        self.assertTrue(any((a == .5).any() for a in alpha_seen))
        self.assertTrue(any((a.sum(1) == 0).any() for a in alpha_seen))

    def test_rejects_clean_fixed_clock(self):
        with self.assertRaises(ValueError):
            self.sample(scaffold_start=1)


if __name__ == '__main__':
    unittest.main()
