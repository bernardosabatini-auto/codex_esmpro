import copy
import unittest

import torch

from latentfold.fragment_conditioning import fragment_features, fragment_flow_loss, sample_fragment
from latentfold.fragment_cross_attention import FragmentCrossAttentionAdapter, load_fragment_adapter
from latentfold.fragment_geometry_conditioning import FragmentGeometryAdapter
from latentfold.pair_model import PairFlowNet


class CrossAttentionTests(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(84)
        self.net = PairFlowNet(d_model=16, n_layers=2, n_heads=2, d_cond=12,
                               d_pair=4, n_pair_blocks=1, max_len=12).eval()
        with torch.no_grad():
            for p in self.net.parameters():
                p.normal_(0, .1)
        self.parent = FragmentGeometryAdapter(16, n_layers=2, n_heads=2,
                                               distance_precision='fp64').eval()
        with torch.no_grad():
            self.parent.output.weight.normal_(0, .1)
            self.parent.pair_output.weight.normal_(0, .1)
        self.adapter = FragmentCrossAttentionAdapter(16, n_layers=2, n_heads=2,
                           distance_precision='fp64', cross_width=8, cross_heads=2).eval()
        self.adapter.load_parent(self.parent.state_dict())
        self.adapter.freeze_parent()
        first = fragment_features(torch.randn(4, 8), 'ACDE', length=10, start=2)
        second = fragment_features(torch.randn(3, 8), 'FGH', length=10, start=3)
        self.features = torch.stack([first[0], second[0]])
        self.keep = torch.stack([first[1], second[1]])
        self.mask = torch.ones_like(self.keep)
        self.mask[1, 8:] = False
        self.coords = torch.randn(2, 10, 3).double() * self.keep[..., None]
        self.noise = torch.randn(2, 10, 8)

    def sample(self, adapter, **kwargs):
        return sample_fragment(self.net, adapter, self.features, self.keep, self.mask,
                               noise=self.noise, steps=4, coordinates=self.coords, **kwargs)

    def activate(self, adapter):
        with torch.no_grad():
            for output in adapter.cross_outputs:
                output.weight.normal_(0, .1)
                output.bias.fill_(.03)

    def test_initial_parent_parity_and_trained_null_parity(self):
        torch.testing.assert_close(self.sample(self.adapter), self.sample(self.parent), rtol=0, atol=0)
        self.activate(self.adapter)
        self.assertGreater(float((self.sample(self.adapter) - self.sample(self.parent)).abs().max()), 1e-4)
        torch.testing.assert_close(self.sample(self.adapter, drop_fragment=True),
                                   self.sample(self.parent, drop_fragment=True), rtol=0, atol=0)
        torch.testing.assert_close(self.sample(self.adapter, guidance=0),
                                   self.sample(self.parent, drop_fragment=True), rtol=0, atol=0)

    def test_routing_dropout_and_packed_memory(self):
        self.activate(self.adapter)
        dropped = torch.tensor([False, True])
        memory = self.adapter.cross_condition(self.features, self.keep, self.mask, dropped)
        self.assertEqual(memory[0].shape[-2], 4)
        hidden = torch.randn(2, 10, 16)
        all_output = self.adapter.cross_update(hidden, 0, memory)
        torch.testing.assert_close(all_output[1], hidden[1], rtol=0, atol=0)
        self.assertGreater(float((all_output[0, ~self.keep[0]] - hidden[0, ~self.keep[0]]).abs().sum().detach()), 0)
        self.adapter.cross_route = 'motif'
        local = self.adapter.cross_update(hidden, 0, self.adapter.cross_condition(
            self.features, self.keep, self.mask, dropped))
        torch.testing.assert_close(local[~self.keep], hidden[~self.keep], rtol=0, atol=0)
        torch.testing.assert_close(local[self.keep], all_output[self.keep], rtol=0, atol=0)
        altered = self.features.clone()
        altered[0, 0, 0] = 1
        with self.assertRaisesRegex(ValueError, 'Scaffold'):
            self.adapter.cross_condition(altered, self.keep, self.mask, dropped)

    def test_checkpoint_gradients_and_parent_freeze(self):
        self.net.requires_grad_(False)
        self.adapter.train()
        self.activate(self.adapter)
        model = copy.deepcopy(self.net)
        adapter = copy.deepcopy(self.adapter)
        target = torch.randn_like(self.noise)
        losses = []
        for net, module, use_checkpoint in ((self.net, self.adapter, False), (model, adapter, True)):
            net.train()
            net.checkpoint_blocks = use_checkpoint
            loss, _ = fragment_flow_loss(net, module, target, self.features, self.keep, self.mask,
                                        generator=torch.Generator().manual_seed(31), coordinates=self.coords)
            loss.backward()
            losses.append(loss.detach())
            self.assertTrue(all(p.grad is None for p in net.parameters()))
            for name, parameter in module.named_parameters():
                if name.startswith('cross_'):
                    self.assertIsNotNone(parameter.grad, name)
                    self.assertTrue(torch.isfinite(parameter.grad).all(), name)
                    self.assertGreater(float(parameter.grad.norm()), 0, name)
                else:
                    self.assertIsNone(parameter.grad, name)
        torch.testing.assert_close(*losses, rtol=0, atol=0)
        for p, q in zip(self.adapter.parameters(), adapter.parameters()):
            if p.requires_grad:
                torch.testing.assert_close(p.grad, q.grad, rtol=1e-5, atol=1e-7)

    def test_pose_and_padding_invariance(self):
        self.activate(self.adapter)
        expected = self.sample(self.adapter)
        rotation = torch.tensor([[0., -1, 0], [1, 0, 0], [0, 0, 1]], dtype=torch.float64)
        self.coords = (self.coords @ rotation + 13) * self.keep[..., None]
        torch.testing.assert_close(self.sample(self.adapter), expected, rtol=0, atol=0)
        active = torch.zeros(2, dtype=torch.bool)
        memory = self.adapter.cross_condition(self.features, self.keep, self.mask, active)
        hidden = torch.randn(2, 10, 16)
        output = self.adapter.cross_update(hidden, 0, memory)
        torch.testing.assert_close(output[~self.mask], hidden[~self.mask], rtol=0, atol=0)

    def test_strict_parent_loading(self):
        state = dict(self.parent.state_dict())
        state.pop('hidden.weight')
        with self.assertRaisesRegex(ValueError, 'Incompatible parent'):
            self.adapter.load_parent(state)

    def test_checkpoint_restores_route_and_rejects_silent_fallback(self):
        self.activate(self.adapter)
        architecture = dict(cross_width=8, cross_heads=2, cross_route='all')
        checkpoint = dict(adapter_config=dict(output_width=16, n_layers=2, n_heads=2,
            distance_precision='fp64', variant='cross_attention', **architecture),
            experiment=dict(fragment_cross_attention=architecture),
            fragment_adapter=self.adapter.state_dict())
        loaded = load_fragment_adapter(checkpoint, self.net).eval()
        torch.testing.assert_close(self.sample(loaded), self.sample(self.adapter), rtol=0, atol=0)
        checkpoint['adapter_config']['cross_route'] = 'motif'
        with self.assertRaisesRegex(ValueError, 'routing differs'):
            load_fragment_adapter(checkpoint, self.net)


if __name__ == '__main__':
    unittest.main()
