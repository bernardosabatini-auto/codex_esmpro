import unittest
from unittest.mock import patch

import torch
from latentfold.fragment_conditioning import fragment_flow_loss, region_balanced_loss


class RegionMassTests(unittest.TestCase):
    def test_short_and_long_motifs_get_identical_total_mass(self):
        error = torch.ones(2, 512, requires_grad=True)
        keep = torch.arange(512)[None] < torch.tensor([20, 153])[:, None]
        mask = torch.ones_like(keep)
        loss = region_balanced_loss(error, keep, mask, torch.zeros(2, dtype=torch.bool), .5)
        loss.backward()
        for i in range(2):
            self.assertAlmostEqual(float(error.grad[i][keep[i]].sum()), .25, places=6)
            self.assertAlmostEqual(float(error.grad[i][~keep[i]].sum()), .25, places=6)

    def test_null_padding_and_degenerate_regions(self):
        error = torch.tensor([[1., 3., 100.], [2., 6., 100.], [4., 8., 100.]], requires_grad=True)
        mask = torch.tensor([[True, True, False]]).expand(3, -1)
        keep = torch.tensor([[True, False, True], [False, False, True], [True, True, True]])
        actual = region_balanced_loss(error, keep, mask, torch.tensor([True, False, False]), .9)
        self.assertEqual(float(actual.detach()), 4.)
        actual.backward()
        self.assertTrue(torch.isfinite(error.grad).all())
        self.assertTrue((error.grad[:, 2] == 0).all())
        for mass in (0., 1., float('nan')):
            with self.assertRaises(ValueError):
                region_balanced_loss(error, keep, mask, torch.zeros(3, dtype=torch.bool), mass)

    def test_objective_does_not_change_random_draws_or_null_loss(self):
        class Net(torch.nn.Module):
            self_cond = False
            def forward(self, x, *args, **kwargs):
                return x * .2
        target = torch.ones(32, 8, 8)
        mask = torch.ones(32, 8, dtype=torch.bool)
        keep = mask.clone(); keep[:, 2:] = False
        draws = []
        with patch('latentfold.fragment_conditioning.prepare_fragment_condition', return_value=(None, None)):
            for mass in (None, .5):
                gen = torch.Generator().manual_seed(123)
                loss, info = fragment_flow_loss(Net(), None, target, None, keep, mask, generator=gen, motif_weight=3., motif_mass=mass)
                draws.append((info, gen.get_state()))
                self.assertTrue(torch.isfinite(loss))
            for key in ('noise', 't', 'dropped'):
                torch.testing.assert_close(draws[0][0][key], draws[1][0][key], atol=0, rtol=0)
            torch.testing.assert_close(draws[0][1], draws[1][1], atol=0, rtol=0)
        dropped = draws[0][0]['dropped']
        self.assertTrue(dropped.any())
        error = torch.rand(32, 8)
        expected = error[dropped].mean()
        actual = region_balanced_loss(error[dropped], keep[dropped], mask[dropped], dropped[dropped], .5)
        torch.testing.assert_close(actual, expected)


if __name__ == '__main__':
    unittest.main()
