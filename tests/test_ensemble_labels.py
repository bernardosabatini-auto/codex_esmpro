import unittest
import numpy as np
from latentfold.ensemble_labels import label_index


class LabelTests(unittest.TestCase):
    def test_reference_and_invalid_fallback(self):
        for arm in ('raw_reference','reference','empirical','balanced'):
            self.assertEqual(label_index(arm,[False],[-1],[.99,.5,.5]),-1)
        self.assertEqual(label_index('reference',[True],[0],[.99,.5,.5]),-1)

    def test_empirical_and_balanced_mass(self):
        # Exact grid: 50% reference; two clusters of sizes 1 and 3.
        valid=[True]*4+[False];clusters=[0,1,1,1,-1]
        counts={arm:np.zeros(5) for arm in ('empirical','balanced')}
        for arm in counts:
            for u in (.25,.75):
                for v in (.25,.75):
                    for w in (.125,.375,.625,.875):
                        counts[arm][label_index(arm,valid,clusters,[u,v,w])+1]+=1
        self.assertEqual(counts['empirical'][0],8)
        self.assertEqual(counts['balanced'][0],8)
        self.assertEqual(counts['empirical'][1],2)
        self.assertEqual(counts['balanced'][1],4)
