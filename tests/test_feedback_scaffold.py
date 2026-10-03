import unittest
from latentfold.fragment_designability import first_repaired_target


class ScaffoldFeedbackTests(unittest.TestCase):
    def test_same_refold_required_and_first_qualifying(self):
        raw=dict(coarse_valid=True,motif_drms=2.,motif_ca_rmsd=2.)
        rows=[dict(coarse_valid=True,motif_drms=.5,motif_ca_rmsd=.5,sc_tm=.7,scaffold_tm=.4),dict(coarse_valid=True,motif_drms=2.,motif_ca_rmsd=2.,sc_tm=.8,scaffold_tm=.9)]
        self.assertEqual(first_repaired_target(raw,rows),0)
        self.assertIsNone(first_repaired_target(raw,rows,require_scaffold=True))
        rows.append(dict(coarse_valid=True,motif_drms=.5,motif_ca_rmsd=.5,sc_tm=.7,scaffold_tm=.6))
        self.assertEqual(first_repaired_target(raw,rows,require_scaffold=True),2)
        raw['coarse_valid']=False
        self.assertIsNone(first_repaired_target(raw,rows,require_scaffold=True))

    def test_threshold_and_bad_score(self):
        raw=dict(coarse_valid=True,motif_drms=.5,motif_ca_rmsd=.5)
        rows=[dict(**raw,sc_tm=.8,scaffold_tm=.5)]
        self.assertIsNone(first_repaired_target(raw,rows,require_scaffold=True))
        rows[0]['scaffold_tm']=float('nan')
        with self.assertRaises(ValueError):first_repaired_target(raw,rows,require_scaffold=True)


if __name__=='__main__':unittest.main()
