import copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from compare_expansion_training import compare


class ExpansionComparisonTests(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup);p=Path(tmp.name)/'protocol.json';protocol=json.loads(Path('configs/expanded_labels_training_protocol.json').read_text());p.write_text(json.dumps(protocol))
        rows=[dict(id=str(i),family='f'+str(i),cohort='original122' if i<32 else 'new',state_definition=dict(clusters=[0,1],teacher_indices=[0,1])) for i in range(160)]
        self.inventory=dict(targets=rows);self.runs=[]
        for seed in (2026100171,2026100181):
            c=dict(seed=seed,protocol=str(p),corpus_kind='expansion',profile_only=False,evaluation_guidance=[1],evaluation_ids=[str(i) for i in range(64)],checkpoint_sha256='initial')
            c.update({key:protocol[key] for key in ('updates','evaluation_steps','evaluation_guidance','evaluation_seed','learning_rate','ema_decay','warmup_updates','batches')})
            scores=[dict(step=s,guidance=1,target_id=str(i),assignments=[0]*32 if s==0 else [0,1]*16,coverage={'32':.5 if s==0 else 1.},strict_coverage={'32':.5 if s==0 else 1.},valid_fraction=1.,teacher_ca_lddt=.9,reference_ca_lddt=.8) for s in (0,500) for i in range(64)]
            self.runs.append(dict(config=c,status='running',updates=500,initial_checkpoint_sha256='initial',scores=scores))

    def analyze(self,runs):
        with patch('compare_expansion_training.metadata',return_value=self.inventory),patch('compare_expansion_training.verify_draws'):
            return compare(runs,500)

    def test_replicated_new_and_combined_capacity_required(self):
        self.assertTrue(self.analyze(self.runs)['replicated_capacity_passed'])
        for r in self.runs[1]['scores']:
            if r['step']==500 and int(r['target_id'])>=32:r.update(coverage={'32':.5},strict_coverage={'32':.5},assignments=[0]*32)
        result=self.analyze(self.runs);self.assertFalse(result['replicated_capacity_passed']);self.assertTrue(result['capacity_checks']['2026100171']['passed'])

    def test_missing_seed_scores_or_changed_initialization_rejected(self):
        for mode in ('seed','score','initial'):
            runs=copy.deepcopy(self.runs)
            if mode=='seed':runs[1]['config']['seed']=2026100171
            elif mode=='score':runs[1]['scores'].pop()
            else:runs[1]['scores'][0]['assignments']=[1]*32
            with self.assertRaises(ValueError):self.analyze(runs)


if __name__=='__main__':unittest.main()
