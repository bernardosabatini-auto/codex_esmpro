import json
from pathlib import Path
import unittest
from types import SimpleNamespace
import torch
from latentfold.local_geometry import local_geometry_loss, endpoint_geometry


class LocalGeometryTests(unittest.TestCase):
    def setUp(self):
        self.c = json.loads((Path(__file__).resolve().parents[1]/'configs/local_geometry122_protocol.json').read_text())['local_geometry']
        self.bb = torch.zeros(1, 12, 4, 3, dtype=torch.float64)
        self.bb[0, :, :, 0] = torch.arange(12)[:, None]*3.8+torch.tensor([-1.23, 0., 1.23, 1.23])
        self.mask = torch.ones(1, 12, dtype=torch.bool)

    def test_zero_and_peptide_descent(self):
        loss, _ = local_geometry_loss(self.bb, self.mask, self.c)
        self.assertEqual(float(loss), 0.)
        damaged = self.bb.clone(); damaged[:, 5, :, 0] += .4; damaged.requires_grad_()
        loss, parts = local_geometry_loss(damaged, self.mask, self.c)
        grad, = torch.autograd.grad(loss, damaged)
        self.assertGreater(float(parts[0]), 0); self.assertTrue(torch.isfinite(grad).all())
        self.assertLess(float(local_geometry_loss(damaged-.1*grad, self.mask, self.c)[0]), float(loss))

    def test_clash_gap_and_rigid_invariance(self):
        damaged = self.bb.clone(); damaged[:, 6:] -= torch.tensor([17., 0., 0.])
        loss, parts = local_geometry_loss(damaged, self.mask, self.c)
        self.assertGreater(float(parts[1]), 0); self.assertGreater(float(parts[2]), 0)
        q, _ = torch.linalg.qr(torch.randn(3, 3, dtype=torch.float64))
        moved = damaged@q+10
        self.assertAlmostEqual(float(local_geometry_loss(moved, self.mask, self.c)[0]), float(loss), places=10)

    def test_padding_and_noncontiguous_rejection(self):
        padded = torch.cat((self.bb, torch.full((1, 3, 4, 3), 1000.)), 1)
        mask = torch.cat((self.mask, torch.zeros(1, 3, dtype=torch.bool)), 1)
        self.assertEqual(float(local_geometry_loss(padded, mask, self.c)[0]), 0.)
        mask[:, 5] = False
        with self.assertRaises(ValueError): local_geometry_loss(padded, mask, self.c)

    def test_no_eligible_does_not_consume_global_rng(self):
        state = dict(t=torch.tensor([.1, .9]), dropped=torch.tensor([False, True]))
        before = torch.get_rng_state().clone()
        loss, stats = endpoint_geometry(None, state, ['a', 'b'], [12, 12], self.c, 0)
        self.assertIsNone(loss); self.assertEqual(stats['geometry_count'], 0)
        self.assertTrue(torch.equal(before, torch.get_rng_state()))

    def test_endpoint_gradient_and_independent_repeated_ids(self):
        class Decoder:
            fm = SimpleNamespace(scale_ref=2.)
            def __call__(self, z, mask, noise, return_backbone):
                self.noise = noise.clone()
                bb = z[..., :3, None].transpose(-1, -2).expand(-1, -1, 4, -1)
                return bb[:, :, 1], bb
        decoder = Decoder()
        velocity = torch.randn(3, 12, 8, requires_grad=True)
        state = dict(t=torch.tensor([.8, .9, .95]), dropped=torch.tensor([False, False, True]), x=torch.randn_like(velocity), velocity=velocity, mask=self.mask.expand(3, -1))
        before = torch.get_rng_state().clone()
        loss, stats = endpoint_geometry(decoder, state, ['a', 'a', 'a'], [12]*3, self.c, 5)
        self.assertEqual(stats['geometry_count'], 2)
        self.assertFalse(torch.equal(decoder.noise[0], decoder.noise[1]))
        self.assertTrue(torch.equal(before, torch.get_rng_state()))
        loss.backward()
        self.assertTrue(torch.isfinite(velocity.grad).all())
        self.assertGreater(float(velocity.grad[:2].norm()), 0.)
        self.assertEqual(float(velocity.grad[2].norm()), 0.)


if __name__ == '__main__': unittest.main()
