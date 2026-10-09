import unittest
import torch
from latentfold.fragment_context_flow import ContextFlow, isolated_features, sample_codes


class ContextFlowTests(unittest.TestCase):
    def test_family_split(self):
        from prepare_fragment_context_flow import family_split
        rows = [dict(id=f'{b}_{i}', family=f'{b}_{i}', bucket=b)
                for b in (128, 256, 384, 512) for i in range(10)]
        excluded = {f'{b}_0' for b in (128, 256, 384, 512)}
        split = family_split(rows, excluded, 4)
        self.assertEqual({k for k,v in split.items() if v=='evaluation'}, excluded)
        self.assertEqual(sum(v=='validation' for v in split.values()), 16)
        self.assertEqual(sum(v=='train' for v in split.values()), 20)
        self.assertEqual(split, family_split(list(reversed(rows)), excluded, 4))
        with self.assertRaises(ValueError):
            family_split(rows+[rows[0]], excluded, 4)

    def test_proper_pose_and_chirality(self):
        torch.manual_seed(91)
        latent = torch.randn(20, 8)
        bb = torch.randn(20, 4, 3)
        q, _ = torch.linalg.qr(torch.randn(3, 3, dtype=torch.float64))
        q[:, 0] *= torch.linalg.det(q)
        a, pos = isolated_features(latent, bb.double(), 'A'*20, length=128, start=54)
        b, pos2 = isolated_features(latent, bb.double()@q+11, 'A'*20, length=128, start=54)
        self.assertTrue(torch.allclose(a, b, atol=1e-6, rtol=0))
        self.assertTrue(torch.equal(pos, pos2))
        reflected = bb.clone(); reflected[..., 2] *= -1
        c, _ = isolated_features(latent, reflected, 'A'*20, length=128, start=54)
        self.assertGreater(float((a-c).abs().max()), .1)

    def test_sampling_and_condition_gradient(self):
        torch.manual_seed(9)
        model = ContextFlow(width=32, layers=1, heads=4, feedforward=64).eval()
        noise = torch.randn(2, 20, 8); features = torch.randn(2, 20, 40)
        pos = torch.randn(2, 20, 4); t = torch.rand(2)
        self.assertTrue(torch.equal(sample_codes(model, noise, features, pos, steps=2), noise))
        torch.nn.init.normal_(model.output.weight, std=.1)
        model(noise, t, features, pos).square().mean().backward()
        self.assertGreater(float(model.condition.weight.grad.norm()), 0)
        self.assertTrue(torch.isfinite(model.condition.weight.grad).all())

    def test_reject_invalid_fragment(self):
        with self.assertRaises(ValueError):
            isolated_features(torch.zeros(20, 8), torch.zeros(20, 4, 3), 'A'*20, length=128, start=54)
        with self.assertRaises(ValueError):
            isolated_features(torch.zeros(20, 8), torch.randn(20, 4, 3), 'A'*20, length=128, start=120)


if __name__ == '__main__':
    unittest.main()
