import unittest

from audit_fragment_failure_stages import refold_stage


def record():
    return dict(refolds=[dict(sequence_index=i, coarse_valid=True, sc_tm=.3,
                             motif_ca_rmsd=2., motif_drms=2.) for i in range(8)],
                scaffold_scores=[.3] * 8, successful_refold_indices=[],
                scaffold_successful_refold_indices=[])


class FailureStageTests(unittest.TestCase):
    def test_different_refolds_cannot_supply_global_and_motif(self):
        r = record()
        r['refolds'][0]['sc_tm'] = .7
        r['refolds'][1].update(motif_ca_rmsd=.4, motif_drms=.4)
        self.assertEqual(refold_stage(r), ('global_without_same_refold_motif', True))

    def test_scaffold_must_pass_in_the_same_joint_refold(self):
        r = record()
        r['refolds'][0].update(sc_tm=.7, motif_ca_rmsd=.4, motif_drms=.4)
        r['successful_refold_indices'] = [0]
        r['scaffold_scores'][1] = .8
        self.assertEqual(refold_stage(r), ('joint_without_scaffold_agreement', False))
        r['scaffold_scores'][0] = .8
        r['scaffold_successful_refold_indices'] = [0]
        self.assertEqual(refold_stage(r), ('strong_success', False))

    def test_invalid_refolds_and_inconsistent_saved_scores_are_rejected(self):
        r = record()
        for row in r['refolds']:
            row.update(coarse_valid=False, sc_tm=.9, motif_ca_rmsd=.1, motif_drms=.1)
        self.assertEqual(refold_stage(r), ('no_valid_refold', False))
        r['successful_refold_indices'] = [0]
        with self.assertRaisesRegex(ValueError, 'decisions disagree'):
            refold_stage(r)


if __name__ == '__main__':
    unittest.main()
