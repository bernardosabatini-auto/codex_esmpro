import unittest
import torch
from latentfold.backbone import align_backbone_to_reference


class ReferencePoseTests(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(1701)
        self.reference = torch.randn(12, 4, 3, dtype=torch.float64)
        self.mask = torch.ones(12, dtype=torch.bool)
        q, _ = torch.linalg.qr(torch.randn(3, 3, dtype=torch.float64))
        q[:, 0] *= torch.linalg.det(q)
        self.rotation = q

    def test_recovers_rigid_pose_and_preserves_distances(self):
        moved = (self.reference @ self.rotation + 19)[None].repeat(2, 1, 1, 1)
        result = align_backbone_to_reference(moved, self.reference, self.mask)
        torch.testing.assert_close(result, self.reference[None].expand_as(result), atol=1e-10, rtol=0)
        torch.testing.assert_close(torch.cdist(moved.flatten(1, 2), moved.flatten(1, 2)),
                                   torch.cdist(result.flatten(1, 2), result.flatten(1, 2)), atol=1e-6, rtol=0)

    def test_ignores_tail_for_fit_but_transforms_tail(self):
        changed = self.reference.clone(); changed[-1] += torch.tensor([20., 0., 0.])
        self.mask[-1] = False
        moved = (changed @ self.rotation - 11)[None]
        result = align_backbone_to_reference(moved, self.reference, self.mask)
        torch.testing.assert_close(result[0], changed, atol=1e-10, rtol=0)

    def test_does_not_mirror_chirality(self):
        mirrored = self.reference.clone(); mirrored[..., 0] *= -1
        result = align_backbone_to_reference(mirrored[None], self.reference, self.mask)[0]
        def volume(x):
            return torch.linalg.det(x[0, 1:] - x[0, 0])
        torch.testing.assert_close(volume(result), volume(mirrored), atol=1e-10, rtol=0)
        self.assertGreater(float((result - self.reference).square().mean()), .01)

    def test_rejects_degenerate_core(self):
        bad = self.reference.clone(); bad[:, 1] = 0
        with self.assertRaisesRegex(ValueError, 'degenerate'):
            align_backbone_to_reference(bad[None], bad, self.mask)
