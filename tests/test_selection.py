import unittest
import numpy as np
from latentfold.selection import ca_lddt_medoid


class SelectionTests(unittest.TestCase):
    def test_rigid_motion_does_not_change_agreement(self):
        rng = np.random.default_rng(3)
        coords = rng.normal(size=(30, 3))*4
        rotation, _ = np.linalg.qr(rng.normal(size=(3, 3)))
        selected, confidence, _ = ca_lddt_medoid([coords, coords@rotation+17, coords])
        self.assertEqual(selected, 0)
        np.testing.assert_equal(confidence, [1, 1, 1])

    def test_agreeing_pair_wins_over_scale_outlier(self):
        coords = np.random.default_rng(7).normal(size=(40, 3))*4
        selected, confidence, _ = ca_lddt_medoid([coords*3, coords, coords.copy()])
        self.assertEqual(selected, 1)
        self.assertGreater(confidence[1], confidence[0])
        with self.assertRaises(ValueError):
            ca_lddt_medoid([coords, coords, coords*np.nan])
