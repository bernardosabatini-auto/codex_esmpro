import unittest
from collections import Counter

from prepare_fragment_source_refold import select_sources
from compare_fragment_source_refolds import summarize


class SourcePanelTests(unittest.TestCase):
    def test_selection_is_order_invariant_and_partitions_are_balanced(self):
        rows=[dict(id=f'{arm}_{bucket}_{i}',bucket=bucket) for arm in ('old','new')
              for bucket in (128,256,384,512) for i in range(20)]
        old={r['id'] for r in rows if r['id'].startswith('old')}
        spec=dict(seed=1,cohorts=['original512','added7429'],buckets=[128,256,384,512],per_cohort_per_bucket=16)
        selected=select_sources(spec,rows,old)
        self.assertEqual(selected,select_sources(spec,rows[::-1],old))
        self.assertEqual(len({r['id'] for r in selected}),128)
        counts=Counter((r['partition'],r['cohort'],r['bucket']) for r in selected)
        self.assertEqual(set(counts.values()),{4})
        self.assertEqual(len(counts),32)
        with self.assertRaises(ValueError):
            select_sources(spec,rows[:10],old)

    def test_independent_strata_denominators_and_contrast_direction(self):
        rows=[dict(target_id=f'{arm}_{b}_{i}',family=f'{arm}_{b}_{i}',arm=arm,bucket=b,
                   scaffold_joint_success=arm=='original512',valid_designable=True)
              for arm in ('original512','added7429') for b in (128,256,384,512) for i in range(16)]
        _,contrasts=summarize(rows)
        self.assertEqual(contrasts[0]['added_minus_original'],-1.)
        self.assertEqual(contrasts[0]['ci95'],[-1.,-1.])
        self.assertEqual(contrasts[1]['ci95'],[0.,0.])
        with self.assertRaises(ValueError): summarize(rows[:-1])
        with self.assertRaises(ValueError): summarize(rows[:-1]+[rows[0]])


if __name__=='__main__':
    unittest.main()
