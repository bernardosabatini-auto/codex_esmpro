import json
from pathlib import Path
import unittest
import numpy as np
from latentfold.backbone_repair import acceptance, repair_backbone
from latentfold.ensemble_metrics import backbone_geometry


class RepairTests(unittest.TestCase):
    def setUp(self):
        self.config = json.loads((Path(__file__).resolve().parents[1]/'configs/backbone_repair_protocol.json').read_text())['repair']
        self.bb = np.zeros((12, 4, 3), dtype=np.float32)
        self.bb[:, :, 0] = np.arange(12)[:, None]*3.8+np.array([-1.23, 0, 1.23, 1.23])
        self.bb[:, 3, 1] = 1

    def test_valid_is_bitwise_unchanged(self):
        out, diag = repair_backbone(self.bb, self.config)
        np.testing.assert_array_equal(out, self.bb)
        self.assertEqual(diag['status'], 'unchanged_valid')

    def test_repair_preserves_atoms_and_all_constraints(self):
        damaged = self.bb.copy()
        damaged[5, :, 0] += .4
        self.assertFalse(backbone_geometry(damaged[None])['coarse_valid'][0])
        out, diag = repair_backbone(damaged, self.config)
        self.assertEqual(diag['status'], 'repaired')
        self.assertTrue(acceptance(damaged, out, self.config)[0])
        np.testing.assert_allclose(out-out[:, 1:2], damaged-damaged[:, 1:2], atol=2e-5)
        np.testing.assert_array_equal(damaged[4], self.bb[4])

    def test_large_damage_falls_back_exactly(self):
        damaged = self.bb.copy()
        damaged[5, :, 0] += 4
        out, diag = repair_backbone(damaged, self.config)
        self.assertEqual(diag['status'], 'fallback_constraints')
        np.testing.assert_array_equal(out, damaged)

    def test_invalid_inputs_and_neighbor_coverage(self):
        bad = self.bb.copy(); bad[0, 0, 0] = np.nan
        with self.assertRaises(ValueError): repair_backbone(bad, self.config)
        with self.assertRaises(ValueError): repair_backbone(self.bb, {**self.config, 'neighbor_radius': 3.1})
        moved = self.bb.copy(); moved[:, 0, 1] += .01
        self.assertFalse(acceptance(self.bb, moved, self.config)[0])

    def test_rigid_transform_equivariance(self):
        # Adam is coordinatewise: exact axis permutations/sign changes are equivariant;
        # arbitrary rotations are not claimed or required by this diagnostic.
        damaged = self.bb.copy(); damaged[5, :, 0] += .4
        q = np.array([[0, 1, 0], [-1, 0, 0], [0, 0, 1]], dtype=np.float32)
        first, _ = repair_backbone(damaged, self.config)
        second, _ = repair_backbone(damaged@q, self.config)
        np.testing.assert_allclose(first@q, second, atol=2e-5)


if __name__ == '__main__': unittest.main()
