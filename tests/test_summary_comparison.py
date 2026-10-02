import copy,json,tempfile,unittest
from pathlib import Path
from compare_summary_learning import compare
from prepare_overfit import sha


class SummaryComparisonTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);root=Path(self.tmp.name)
        labels=root/'labels.json';labels.write_text(json.dumps(dict(config=dict(targets=[dict(id=str(i),family=str(i),state_definition=dict(clusters=[0,1])) for i in range(32)]))))
        protocol=root/'protocol.json';protocol.write_text(json.dumps(dict(advance_to_replication=dict(minimum_recall_gain_vs_projected_final=.05,minimum_validity_delta_vs_projected_final=-.01,minimum_validity_delta_vs_initial=-.01))))
        c=dict(seed=191,profile_only=False,label_manifest=str(labels),label_manifest_sha256=sha(labels),summary_protocol=str(protocol),summary_protocol_sha256=sha(protocol))
        self.runs=[]
        for arm in ('projected_final','teacher_summary'):
            scores=[]
            for step in (0,500):
                improved=arm=='teacher_summary' and step==500
                for i in range(32):scores.append(dict(step=step,guidance=1,target_id=str(i),assignments=([0,1]*16 if improved else [0]*32),coverage={'32':1. if improved else .5},strict_coverage={'32':1. if improved else .5},valid_fraction=1.,teacher_ca_lddt=.9,reference_ca_lddt=.85,state_total_variation=0. if improved else .5))
            self.runs.append(dict(status='complete',updates=500,config=dict(c,summary_arm=arm),initial_checkpoint_sha256='identical',summary_adapter=dict(initial_sha256='identical',controls=[dict(initial_exact=True) for _ in range(4)],gradients=[dict(norm=1.) for _ in range(500)]),controls=[{}]*4,scores=scores,training=[dict(step=s,length=128,batch=32,learning_rate=.001,ids_sha256='ids',label_choices_sha256='labels') for s in list(range(1,500,25))+[500]]))

    def test_fixed_denominator_family_comparison_passes_clear_gain(self):
        d=compare(self.runs);self.assertTrue(d['replication_justified']);self.assertEqual(d['comparisons']['projected_final']['coverage32']['difference'],.5)
        self.assertEqual(d['comparisons']['projected_final']['coverage32']['families'],32)

    def test_invalid_family_is_retained_and_can_fail_validity(self):
        r=self.runs[1]['scores'][32];r.update(assignments=[-1]*32,coverage={'32':0.},strict_coverage={'32':0.},valid_fraction=0.)
        d=compare(self.runs);self.assertFalse(d['replication_justified']);self.assertFalse(d['checks']['validity_vs_control']);self.assertEqual(d['comparisons']['projected_final']['coverage32']['families'],32)

    def test_mismatched_draw_or_initial_score_rejected(self):
        m=copy.deepcopy(self.runs);m[1]['training'][0]['label_choices_sha256']='different'
        with self.assertRaisesRegex(ValueError,'draws'):compare(m)
        m=copy.deepcopy(self.runs);m[1]['scores'][0]['teacher_ca_lddt']=.89
        with self.assertRaisesRegex(ValueError,'initial predictions'):compare(m)


if __name__=='__main__':unittest.main()
