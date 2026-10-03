import unittest
import json
import tempfile
from collections import Counter
from pathlib import Path

from prepare_fragment_source_refold import select_sources
from compare_fragment_source_refolds import summarize, ready_command


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

    def test_followup_requires_all_own_reports_and_exact_panel(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'runs').mkdir();(root/'reports').mkdir()
            ids=['1','2','3','4'];plan=dict(jobs=ids,inventory_sha256='panel')
            (root/'runs/fragment_source_comparison.json').write_text(json.dumps(plan))
            registry={'jobs':[dict(id=i,completion_action='summarize_fragment_source_refold') for i in ids]}
            (root/'runs/jobs.json').write_text(json.dumps(registry))
            self.assertIsNone(ready_command(root))
            for i in ids:
                (root/f'reports/fragment_source_refold_{i}.json').write_text(json.dumps(dict(status='complete',inventory_sha256='panel')))
            self.assertIsNotNone(ready_command(root))
            (root/'reports/fragment_source_refold_4.json').write_text(json.dumps(dict(status='complete',inventory_sha256='other')))
            with self.assertRaises(ValueError):ready_command(root)
            registry['jobs'].pop();(root/'runs/jobs.json').write_text(json.dumps(registry))
            with self.assertRaises(ValueError):ready_command(root)


if __name__=='__main__':
    unittest.main()
