import unittest
import numpy as np
from analyze_bounded_retry import select_draws, metrics

class RetryTests(unittest.TestCase):
    def test_fixed_attempts_first_valid_and_exhausted_fallback(self):
        valid=np.array([True,False,False, False,False,False, False,True,False, False,True,False])
        selected,used=select_draws(valid,outputs=3,attempts=4)
        np.testing.assert_array_equal(selected,[0,7,2])
        np.testing.assert_array_equal(used,[1,3,4])
        self.assertEqual(len(set(selected)),3)

    def test_selector_rejects_incomplete_or_nonboolean_inputs(self):
        with self.assertRaises(ValueError):select_draws(np.ones(127,dtype=bool))
        with self.assertRaises(ValueError):select_draws(np.ones(128))

    def test_invalid_high_reference_quality_cannot_be_selected(self):
        valid=np.array([False,True,True,True])
        selected,used=select_draws(valid,outputs=2,attempts=2)
        score=metrics(selected,valid,np.array([1.,.9,.5,.9]),np.array([-1,0,-1,1]))
        self.assertEqual(selected.tolist(),[2,1])
        self.assertEqual(score['valid_fraction'],1.)
        self.assertEqual(score['coverage'],.5)
        self.assertAlmostEqual(score['oracle_ca_lddt'],.7)

if __name__=='__main__':unittest.main()
