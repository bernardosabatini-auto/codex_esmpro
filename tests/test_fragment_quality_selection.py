import itertools
import unittest
import numpy as np
from prepare_fragment_quality_selection import assign


class AssignmentTests(unittest.TestCase):
    def test_exact_optimum_and_matching(self):
        q=np.array([[99,10,12],[20,98,10],[10,20,97],[65,45,22],[32,75,88]],float)
        old,new,before,after=assign(q,list('abcde'),list('LCR'),21)
        self.assertEqual(sorted(old),sorted(new))
        expected=max(sum(q[i,k] for i,k in enumerate(p)) for p in set(itertools.permutations(old)))
        self.assertEqual(after.sum(),expected)
        self.assertGreaterEqual(after.sum(),before.sum())

    def test_reproducible(self):
        q=np.array([[10,90,50],[90,50,10],[50,10,90]],float)
        a=assign(q,list('abc'),list('LCR'),21);b=assign(q,list('abc'),list('LCR'),21)
        for left,right in zip(a,b):np.testing.assert_array_equal(left,right)

    def test_invalid_confidence(self):
        with self.assertRaises(ValueError):assign([[90,float('nan'),20]],['a'],list('LCR'),21)


if __name__=='__main__':unittest.main()
