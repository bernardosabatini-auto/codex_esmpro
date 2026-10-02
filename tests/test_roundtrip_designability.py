import unittest
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from summarize_roundtrip_designability import auc,discriminate


class ReconstructionSignalTests(unittest.TestCase):
    def test_empty_coarse_valid_cohort_is_unqualified(self):
        d=discriminate([]);self.assertEqual(d['backbones'],0);self.assertIsNone(d['pooled_auc'])

    def test_auc_ties_and_missing_class(self):
        self.assertEqual(auc([1,0],[2,1]),1.)
        self.assertEqual(auc([1,0],[1,2]),0.)
        self.assertEqual(auc([1,0],[1,1]),.5)
        self.assertIsNone(auc([1,1],[1,2]))
        with self.assertRaises(ValueError):auc([1,0],[float('nan'),1])

    def test_family_separation_does_not_create_within_family_signal(self):
        rows=[dict(family='a',designable=True,mean_ca_rmsd=1.) for _ in range(3)]+[dict(family='b',designable=False,mean_ca_rmsd=3.) for _ in range(3)]
        d=discriminate(rows);self.assertEqual(d['pooled_auc'],1.);self.assertEqual(d['mixed_label_families'],0);self.assertIsNone(d['within_family_auc'])

    def test_lower_error_and_equal_family_weight(self):
        rows=[dict(family='a',designable=y,mean_ca_rmsd=e) for y,e in [(True,1.),(False,2.)]]+[dict(family='b',designable=y,mean_ca_rmsd=e) for y,e in [(True,4.),(False,3.)]]*3
        d=discriminate(rows);self.assertEqual(d['mixed_label_families'],2);self.assertEqual(d['within_family_auc'],.5)


if __name__=='__main__':unittest.main()
