import copy
from types import SimpleNamespace
import unittest

import torch
from torch import nn

from latentfold.decoder import DifferentiableDecoder
from latentfold.fragment_conditioning import fragment_features
from latentfold.fragment_geometry_conditioning import fragment_coordinates
from latentfold.fragment_decoder import FragmentDecoder, weighted_backbone_mse, fragment_decoder_loss


class TokenFeatures(nn.Module):
    def __init__(self):
        super().__init__()
        self.linear = nn.Linear(1, 16)
    def forward(self, batch):
        return self.linear(batch['t'][:, None, None].expand(-1, batch['mask'].shape[1], 1))


class PairFeatures(nn.Module):
    def __init__(self):
        super().__init__()
        self.bias = nn.Parameter(torch.randn(8))
    def forward(self, batch):
        b, n = batch['mask'].shape
        return self.bias.expand(b, n, n, -1)


class TinyDecoder(nn.Module):
    def __init__(self):
        super().__init__()
        self.cond_factory, self.pair_repr_builder = TokenFeatures(), PairFeatures()
        self.token, self.pair, self.latent = nn.Linear(16, 12), nn.Linear(8, 12), nn.Linear(8, 12)
    def forward(self, batch):
        b, n = batch['mask'].shape
        velocity = self.token(self.cond_factory(batch)) + self.pair(self.pair_repr_builder(batch).mean(2)) + self.latent(batch['single_repr'])
        return dict(coors_pred=velocity.reshape(b, 4*n, 3) - .1 * batch['x_t'])


class FragmentDecoderTests(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(61)
        ae = SimpleNamespace(decoder=TinyDecoder(), fm=SimpleNamespace(scale_ref=1.), cfg_exp=SimpleNamespace(model=SimpleNamespace(target_pred='v')))
        self.codec = DifferentiableDecoder(ae, n_steps=3)
        self.model = FragmentDecoder(self.codec, seed=62, token_width=16, pair_width=8)
        self.z = torch.randn(2, 8, 8)
        self.mask = torch.ones(2, 8, dtype=torch.bool)
        f, k = fragment_features(torch.randn(3, 8), 'ACD', length=8, start=2)
        self.features, self.keep = f[None].repeat(2, 1, 1), k[None].repeat(2, 1)
        self.coords = fragment_coordinates(torch.randn(3, 4, 3), length=8, start=2)[None].repeat(2, 1, 1)
        self.noise = torch.randn(2, 32, 3)
        self.target = torch.randn(2, 8, 4, 3) * 5

    def sample(self, z=None, coords=None, **kwargs):
        return self.model(self.z if z is None else z, self.features, self.keep, self.mask,
                          self.coords if coords is None else coords, noise=self.noise, **kwargs)

    def test_initial_zero_adapter_matches_original_decoder_exactly(self):
        for masked in (False, True):
            z = torch.where(self.keep[..., None], torch.zeros_like(self.z), self.z) if masked else self.z
            expected = self.codec(z, self.mask, noise=self.noise, return_backbone=True)[1]
            self.assertTrue(torch.equal(expected, self.sample(mask_fragment=masked)))

    def test_disabled_condition_preserves_original_after_training(self):
        for p in self.model.adapter.parameters():
            nn.init.normal_(p, std=.05)
        expected = self.codec(self.z, self.mask, noise=self.noise, return_backbone=True)[1]
        self.assertTrue(torch.equal(expected, self.sample(drop_fragment=True, mask_fragment=False)))
        self.assertFalse(torch.equal(expected, self.sample(mask_fragment=False)))

    def test_hidden_endpoint_cannot_leak_and_supplied_pose_is_invariant(self):
        for p in self.model.adapter.parameters():
            nn.init.normal_(p, std=.05)
        other = self.z.clone()
        other[self.keep] = 900
        self.assertTrue(torch.equal(self.sample(), self.sample(z=other)))
        posed = (self.coords.double() @ torch.tensor([[0., -1, 0], [1, 0, 0], [0, 0, 1]], dtype=torch.float64) + 11) * self.keep[..., None]
        torch.testing.assert_close(self.sample(), self.sample(coords=posed), rtol=0, atol=1e-5)

    def test_actual_three_step_gradient_only_updates_adapters(self):
        self.model.train()
        self.assertFalse(self.model.decoder.training)
        loss, _ = fragment_decoder_loss(self.model, self.z, self.target, self.features, self.keep, self.mask, self.coords, noise=self.noise)
        loss.backward()
        self.assertGreater(float(self.model.adapter.output.weight.grad.norm()), 0)
        self.assertGreater(float(self.model.adapter.pair_output.weight.grad.norm()), 0)
        self.assertTrue(all(p.grad is None and not p.requires_grad for p in self.model.decoder.parameters()))

    def test_checkpoint_matches_direct_gradients(self):
        self.model.train()
        outputs, gradients = [], []
        for use_checkpoint in (False, True):
            self.model.zero_grad(set_to_none=True)
            bb = self.sample(checkpoint_steps=use_checkpoint)
            weighted_backbone_mse(bb, self.target, self.keep).backward()
            outputs.append(bb.detach())
            gradients.append({k: p.grad.clone() for k, p in self.model.adapter.named_parameters()})
        self.assertTrue(torch.equal(*outputs))
        for k in gradients[0]:
            torch.testing.assert_close(gradients[0][k], gradients[1][k], rtol=0, atol=1e-6)

    def test_weighted_proper_alignment_and_directional_derivative(self):
        q = self.target.double()
        rotation = torch.tensor([[0., -1, 0], [1, 0, 0], [0, 0, 1]], dtype=torch.float64)
        self.assertLess(float(weighted_backbone_mse(q @ rotation + 17, q, self.keep)), 1e-10)
        reflected = q.clone()
        reflected[..., 0] *= -1
        self.assertGreater(float(weighted_backbone_mse(reflected, q, self.keep)), 1)
        p = (q + torch.randn_like(q)).requires_grad_()
        direction = torch.randn_like(p)
        direction /= direction.norm()
        loss = weighted_backbone_mse(p, q, self.keep)
        gradient, = torch.autograd.grad(loss, p)
        h = 1e-5
        finite_difference = (weighted_backbone_mse(p.detach()+h*direction, q, self.keep) - weighted_backbone_mse(p.detach()-h*direction, q, self.keep))/(2*h)
        self.assertAlmostEqual(float(finite_difference), float((gradient*direction).sum()), places=6)

    def test_rejects_padded_codec_batches(self):
        self.mask[1, -1] = False
        with self.assertRaises(ValueError):
            self.sample()


if __name__ == '__main__':
    unittest.main()
