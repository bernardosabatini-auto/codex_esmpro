import unittest
from prepare_extra_fragment_refold import partitions
from summarize_extra_fragment_refold import same_scaffold_success
from compare_extra_fragment_refolds import summarize


class ExtraRefoldTests(unittest.TestCase):
    def test_disjoint_length_balanced_partition(self):
        lengths={str(i):100 if i<32 else 300 for i in range(64)}
        result=partitions(lengths)
        self.assertEqual(set(i for ids in result for i in ids),set(lengths))
        for ids in result:
            self.assertEqual(len(ids),16)
            self.assertEqual(sum(lengths[i]<=256 for i in ids),8)
        with self.assertRaises(ValueError):partitions(dict(lengths,extra=100))

    def test_different_sequences_cannot_supply_different_constraints(self):
        self.assertEqual(same_scaffold_success([0],[.4,.9,.1,.1,.1,.1,.1,.1]),[])
        self.assertEqual(same_scaffold_success([0,2],[.4,.9,.6,.1,.1,.1,.1,.1]),[2])

    def test_full_denominator_and_duplicate_or_missing_refolds(self):
        native={str(i):dict(scaffold_joint_success=True) for i in range(64)}
        rows=[dict(arm=arm,target_id=str(i),family=str(i),generation_slot=k,length=100 if i<32 else 300,raw_gate_passed=(i==0 and k==0 and arm=='augmented128')) for arm in ('control128','augmented128','control512','augmented512') for i in range(64) for k in range(4)]
        record=dict(next(r for r in rows if r['raw_gate_passed']),strict_joint_success=True,scaffold_joint_success=True)
        summaries,_=summarize(rows,[record],native)
        r=next(r for r in summaries if r['arm']=='augmented128' and r['cohort']=='all')
        self.assertEqual((r['samples'],r['scaffold_successes']),(256,1))
        with self.assertRaises(ValueError):summarize(rows,[],native)
        with self.assertRaises(ValueError):summarize(rows,[record,record],native)
        with self.assertRaises(ValueError):summarize(rows[:-1],[record],native)
