import copy,json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from compare_expanded import compare
from prepare_overfit import sha
from latentfold.training_schedule import proportional_schedule


class ExpandedTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);root=Path(self.temp.name)
        counts={128:5,256:70,384:25,512:22};targets=[]
        for length,n in counts.items():
            for _ in range(n):targets.append(dict(id=str(len(targets)),family=str(len(targets)),bucket=length,state_definition=dict(clusters=[0]+[1]*15)))
        inventory=root/'inventory.json';inventory.write_text(json.dumps(dict(targets=targets,capacity_ids=[r['id'] for r in targets[:32]])))
        protocol=root/'protocol.json';protocol.write_text(json.dumps(dict(seeds=[11,21])))
        c=dict(corpus_inventory=str(inventory),corpus_inventory_sha256=sha(inventory),protocol=str(protocol),protocol_sha256=sha(protocol),arm='aligned_teacher',profile_only=False,evaluation_guidance=[1],evaluation_steps=[500,2000],updates=2000,batches={'128':32,'256':16,'384':8,'512':8},checkpoint_sha256='weights')
        self.runs=[]
        for seed in (11,21):
            schedule=proportional_schedule(counts,2000,seed+2)
            logs=[dict(step=s+1,length=schedule[s],batch=c['batches'][str(schedule[s])],learning_rate=.00003,ids_sha256=str(s)) for s in range(500) if s%25==0 or s+1==500]
            for prior in ('empirical','balanced'):
                rows=[]
                for step in (0,500):
                    improved=step==500 and prior=='balanced'
                    for r in targets:
                        rows.append(dict(step=step,guidance=1,target_id=r['id'],assignments=[0,1]*16 if improved else [1]*32,coverage={'32':1. if improved else .5},strict_coverage={'32':1. if improved else .5},valid_fraction=1.,teacher_ca_lddt=.95,reference_ca_lddt=.9,state_total_variation=.4375 if improved else .0625))
                self.runs.append(dict(status='running',updates=500,config=dict(c,seed=seed,label_distribution=prior),initial_checkpoint_sha256='weights',length_schedule=schedule.copy(),training=copy.deepcopy(logs),scores=rows))

    def test_replicated_gain_and_cohort_counts(self):
        d=compare(self.runs,500);self.assertTrue(d['replicated_capacity_passed'])
        self.assertEqual(d['comparisons']['11_balanced_additional90_vs_empirical']['coverage32']['families'],90)
        self.assertEqual(d['comparisons']['21_balanced_original32_vs_initial']['coverage32']['ci95'],[.5,.5])

    def test_one_seed_without_gain_fails_replication(self):
        self.runs[-1]['scores']=copy.deepcopy(self.runs[-2]['scores'])
        d=compare(self.runs,500);self.assertTrue(d['capacity_checks']['11']['passed']);self.assertFalse(d['replicated_capacity_passed'])

    def test_reject_confounds_and_incomplete_data(self):
        for kind in ('draws','schedule','initial','missing'):
            runs=copy.deepcopy(self.runs)
            if kind=='draws':runs[1]['training'][0]['ids_sha256']='different'
            if kind=='schedule':runs[1]['length_schedule'][0]=1024
            if kind=='initial':runs[1]['scores'][0]['teacher_ca_lddt']=.4
            if kind=='missing':runs[1]['scores'].pop()
            with self.subTest(kind=kind),self.assertRaises(ValueError):compare(runs,500)


if __name__=='__main__':unittest.main()
