import copy,unittest
from summarize_fragment_validation_scaffold import summarize_views


class SameRefoldViewsTests(unittest.TestCase):
    def fixture(self):
        records=[dict(arm=a,target_id='focus',generation_slot=s,family='family',raw_gate_passed=True,successful_refold_indices=[0]) for a,s in [('native',0),('model',0),('model',7)]]
        rows=[dict(arm=r['arm'],target_id='focus',generation_slot=r['generation_slot'],sequence_index=i,primary_joint_success=i==0,scaffold_only_tm=.6 if i==0 else .4,scaffold_joint_success=i==0) for r in records for i in range(8)]
        primary=dict(records=records,summaries=[dict(arm='model',view=v,screened=n,raw_matches=k,strict_successes=k) for v,n,k in [('whole_panel',64,1),('focus',16,2)]])
        return primary,dict(rows=rows,successful_scaffold_diversity=[]),dict(focus_id='focus')

    def test_focus_extra_success_does_not_enter_whole_panel(self):
        result=summarize_views(*self.fixture())
        self.assertEqual([(r['scaffold_successes'],r['screened']) for r in result['summaries']],[(1,64),(2,16)])
        self.assertTrue(result['native_scaffold_controls']['focus'])

    def test_different_sequence_metrics_cannot_be_combined(self):
        primary,scaffold,spec=self.fixture()
        changed=copy.deepcopy(scaffold)
        changed['rows'][0]['scaffold_only_tm']=.4
        changed['rows'][1]['scaffold_only_tm']=.6
        with self.assertRaises(ValueError):summarize_views(primary,changed,spec)
        changed['rows'][0]['scaffold_joint_success']=False
        result=summarize_views(primary,changed,spec)
        self.assertFalse(result['native_scaffold_controls']['focus'])

    def test_missing_design_is_not_silently_dropped(self):
        primary,scaffold,spec=self.fixture();scaffold['rows'].pop()
        with self.assertRaises(ValueError):summarize_views(primary,scaffold,spec)
