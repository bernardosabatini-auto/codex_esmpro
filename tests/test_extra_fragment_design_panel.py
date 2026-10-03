import unittest
from extra_fragment_design_panel import designability_ids
from prepare_extra_fragment_refold import partitions
from compare_extra_fragment_refolds import summarize, designability_summary


class FixedDesignabilityPanelTests(unittest.TestCase):
    def test_panel_is_balanced_and_independent_of_outcomes_or_order(self):
        items={str(i):dict(length=100 if i<32 else 300) for i in range(64)}
        spec=dict(designability_panel=dict(families_per_length=16,slot=0,seed=2026100377))
        panel=designability_ids(spec,items)
        changed={i:dict(q,raw_gate_passed=i not in panel) for i,q in reversed(list(items.items()))}
        self.assertEqual(panel,designability_ids(spec,changed))
        for ids in partitions({i:q['length'] for i,q in items.items()}):
            chosen=set(ids)&panel
            self.assertEqual(len(chosen),8)
            self.assertEqual(sum(items[i]['length']<=256 for i in chosen),4)

    def test_global_designability_does_not_rescue_a_failed_raw_constraint(self):
        arms=('control','candidate');pairs=[dict(label='objective',baseline=arms[0],candidate=arms[1])]
        items={str(i):dict(length=100 if i<32 else 300) for i in range(64)}
        panel=designability_ids(dict(designability_panel=dict(families_per_length=16,slot=0,seed=2026100377)),items)
        screen=[dict(arm=a,target_id=i,family=i,generation_slot=k,length=q['length'],raw_gate_passed=False)
                for a in arms for i,q in items.items() for k in range(4)]
        records=[dict(r,strict_joint_success=False,scaffold_joint_success=False,valid_designable=r['arm']=='candidate')
                 for r in screen if r['target_id'] in panel and r['generation_slot']==0]
        native={i:dict(scaffold_joint_success=True) for i in items}
        primary,_=summarize(screen,records,native,arms=arms,pairs=pairs,designability_targets=panel)
        self.assertTrue(all(r['scaffold_successes']==0 for r in primary))
        secondary=designability_summary(screen,records,panel,arms,pairs)
        all_rows=[r for r in secondary['summaries'] if r['cohort']=='all']
        self.assertEqual([r['valid_designable'] for r in all_rows],[0,32])
        self.assertEqual([r['samples'] for r in all_rows],[32,32])
        with self.assertRaises(ValueError):summarize(screen,records[:-1],native,arms=arms,pairs=pairs,designability_targets=panel)
