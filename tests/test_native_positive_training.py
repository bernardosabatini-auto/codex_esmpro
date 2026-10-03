import copy
import unittest
from native_positive_training_core import qualified_inventory,check_draws,DRAW_KEYS


class PositiveCoverageTests(unittest.TestCase):
    def labels(self):
        old=dict(status='complete',rows=[dict(target_id=f'old{i}',length=96,bucket=128) for i in range(10)])
        new=dict(status='complete',gate=dict(qualified=True),rows=[dict(target_id=f'new{i}',length=96,bucket=128,qualified=i%2==0) for i in range(64)])
        return old,new

    def test_all_qualified_and_originals_retained(self):
        old,new=self.labels();rows=qualified_inventory(old,new)
        self.assertEqual(len(rows),42)
        self.assertEqual({r['target_id'] for r in rows},{r['target_id'] for r in old['rows']}|{r['target_id'] for r in new['rows'] if r['qualified']})

    def test_failed_or_overlapping_cohort_rejected(self):
        old,new=self.labels();new['gate']['qualified']=False
        with self.assertRaises(ValueError):qualified_inventory(old,new)
        new['gate']['qualified']=True;new['rows'][0]['target_id']='old0'
        with self.assertRaises(ValueError):qualified_inventory(old,new)

    def test_data_changes_allowed_noise_changes_rejected(self):
        a=[{k:1 for k in DRAW_KEYS}];b=copy.deepcopy(a);a[0]['ids']=['old'];b[0]['ids']=['new'];check_draws(a,b)
        for k in DRAW_KEYS:
            changed=copy.deepcopy(b);changed[0][k]=2
            with self.assertRaises(ValueError):check_draws(a,changed)


if __name__=='__main__':unittest.main()
