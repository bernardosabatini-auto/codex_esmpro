import copy
import unittest

from latentfold.fragment_preferences import motif_quality, split_preference
from fragment_preference_calibration import select_sources


def record(slot=0, error=1.):
    raw=dict(coarse_valid=True,motif_ca_rmsd=error,motif_drms=error)
    return dict(target_id='trainA',slot=slot,raw=raw,
                refolds=[dict(raw,sequence_index=k,sc_tm=.8,scaffold_tm=.8) for k in range(8)])


class PreferenceTests(unittest.TestCase):
    def test_requires_same_valid_global_scaffold_refold(self):
        row=record()
        for k,r in enumerate(row['refolds']):
            r['sc_tm']=.8 if k%2 else .4
            r['scaffold_tm']=.4 if k%2 else .8
        self.assertEqual(motif_quality(row,range(8)),0)
        row['refolds'][0]['sc_tm']=.8
        row['refolds'][0]['coarse_valid']=False
        self.assertEqual(motif_quality(row,range(8)),0)
        row['refolds'][0]['coarse_valid']=True
        self.assertEqual(motif_quality(row,range(8)),1)

    def test_raw_and_both_motif_errors_bound_quality(self):
        row=record();row['raw']['motif_drms']=3
        self.assertAlmostEqual(motif_quality(row,range(8)),1/3)
        row['raw']['coarse_valid']=False
        self.assertEqual(motif_quality(row,range(8)),0)

    def test_confirmation_cannot_reselect_pair(self):
        winner,loser,third=record(0),record(1,4),record(2,2)
        for r in winner['refolds'][4:]:r['motif_drms']=8
        result=split_preference([winner,loser,third])
        self.assertEqual((result['winner'],result['loser']),(0,1))
        self.assertTrue(result['eligible']);self.assertFalse(result['confirmed'])
        # Third candidate beats loser on confirmation, but cannot replace winner.
        self.assertGreater(result['scores'][2][1],result['scores'][1][1])

    def test_confirmed_ranking_and_stable_ties(self):
        rows=[record(2,4),record(1),record(0)]
        result=split_preference(rows)
        self.assertEqual((result['winner'],result['loser']),(0,2))
        self.assertTrue(result['confirmed'])
        self.assertFalse(split_preference([record(0),record(1)])['eligible'])

    def test_rejects_corrupt_or_mixed_records(self):
        for key in ('motif_drms','sc_tm','scaffold_tm'):
            row=record();row['refolds'][7][key]=float('nan')
            with self.assertRaises(ValueError):motif_quality(row,range(4))
        row=record();row['refolds'][7]['sequence_index']=0
        with self.assertRaises(ValueError):motif_quality(row,range(8))
        other=record(1);other['target_id']='other'
        with self.assertRaises(ValueError):split_preference([record(),other])

    def test_selection_is_balanced_excludes_prior_and_ignores_outcomes(self):
        inventory={f'{b}_{k}':dict(id=f'{b}_{k}',bucket=b,length=b,family=f'{b}_{k}')
                   for b in (128,256,384,512) for k in range(12)}
        excluded={f'{b}_0' for b in (128,256,384,512)}
        spec=dict(selection_seed=2026100403)
        rows=select_sources(spec,inventory,excluded)
        self.assertEqual(len(rows),32)
        self.assertFalse({r['id'] for r in rows}&excluded)
        for partition in range(4):
            for bucket in (128,256,384,512):
                self.assertEqual(sum(r['partition']==partition and r['bucket']==bucket for r in rows),2)
        reversed_inventory=dict(reversed(list(inventory.items())))
        self.assertEqual(rows,select_sources(spec,reversed_inventory,excluded))


if __name__=='__main__':unittest.main()
