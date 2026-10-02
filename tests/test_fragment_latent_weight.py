import unittest

import torch
from torch import nn

from latentfold.fragment_conditioning import FragmentAdapter, fragment_features, fragment_flow_loss


class ConstantVelocity(nn.Module):
    def __init__(self, batch, length):
        super().__init__()
        self.cond_norm = nn.LayerNorm(2)
        self.velocity = nn.Parameter(torch.zeros(batch, length, 8))
        self.self_cond = False

    def prepare_condition(self, esm, mask, dropped):
        return esm.new_zeros(*mask.shape, 16), esm.new_zeros(len(mask), 16)

    def forward(self, x, t, esm, mask, **kwargs):
        return self.velocity


class LatentWeightTests(unittest.TestCase):
    def test_gradient_ratios_dropouts_and_random_draws(self):
        b, n = 32, 4
        net, adapter = ConstantVelocity(b, n), FragmentAdapter(16)
        features, keep = fragment_features(torch.zeros(2, 8), 'AC', length=n, start=1)
        features, keep = features[None].expand(b, -1, -1), keep[None].expand(b, -1)
        mask, target = torch.ones(b, n, dtype=torch.bool), torch.zeros(b, n, 8)
        gradients, traces, states = [], [], []
        for weight in (1., 3.):
            generator = torch.Generator().manual_seed(42)
            net.zero_grad()
            loss, info = fragment_flow_loss(net, adapter, target, features, keep, mask,
                                           generator=generator, motif_weight=weight)
            loss.backward()
            gradients.append(net.velocity.grad.clone())
            traces.append(info)
            states.append(generator.get_state())
        torch.testing.assert_close(states[0], states[1], rtol=0, atol=0)
        for key in ('noise', 't', 'dropped'):
            torch.testing.assert_close(traces[0][key], traces[1][key], rtol=0, atol=0)
        dropped = traces[0]['dropped']
        self.assertTrue(dropped.any() and (~dropped).any())
        # Half the residues are supplied: normalization makes their relative
        # gradient 3/2, the scaffold gradient 1/2, and dropped examples unchanged.
        ratio = torch.where(keep, 1.5, .5)
        ratio[dropped] = 1
        torch.testing.assert_close(gradients[1], gradients[0]*ratio[..., None], rtol=2e-6, atol=1e-8)

    def test_unit_weight_preserves_original_loss_exactly(self):
        net, adapter = ConstantVelocity(1, 4), FragmentAdapter(16)
        f, k = fragment_features(torch.zeros(2, 8), 'AC', length=4, start=1)
        mask = torch.tensor([[True, True, True, False]])
        target = torch.ones(1, 4, 8)
        loss, info = fragment_flow_loss(net, adapter, target, f[None], k[None], mask,
                                       generator=torch.Generator().manual_seed(9))
        original = (((net.velocity-(target-info['noise'])).square().mean(-1)*mask).sum(1)/mask.sum(1)).mean()
        torch.testing.assert_close(loss, original, rtol=0, atol=0)
        for weight in (0, -1, float('nan'), float('inf')):
            with self.assertRaises(ValueError):
                fragment_flow_loss(net, adapter, target, f[None], k[None], mask,
                    generator=torch.Generator(), motif_weight=weight)


if __name__ == '__main__':
    unittest.main()
