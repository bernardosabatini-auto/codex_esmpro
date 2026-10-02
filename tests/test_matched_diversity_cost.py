import unittest
from analyze_matched_diversity_cost import affordable_counts


class CostTests(unittest.TestCase):
    def test_per_target_budget_counts_without_quality_input(self):
        times={'1':{'a':.5,'b':2.},'8':{'a':1.,'b':3.},'32':{'a':4.,'b':10.}}
        self.assertEqual(affordable_counts(times,1.),{'a':8,'b':0})
        self.assertEqual(affordable_counts(times,4.),{'a':32,'b':8})
        self.assertEqual(affordable_counts(times,100.),{'a':32,'b':32})

    def test_missing_targets_and_nonfinite_latency_rejected(self):
        with self.assertRaises(ValueError):affordable_counts({'1':{'a':1.},'8':{'b':2.},'32':{'a':3.}},4.)
        with self.assertRaises(ValueError):affordable_counts({'1':{'a':1.},'8':{'a':float('nan')},'32':{'a':3.}},4.)


if __name__=='__main__':unittest.main()
