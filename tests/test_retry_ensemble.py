import copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import h5py,numpy as np
from summarize_retry_ensemble import validate_slot,analyze
from score_ensemble_states import scoring_arms,validate_retry_parent
from prepare_overfit import sha
from start_state_scoring import start

class RetryEnsembleTests(unittest.TestCase):
    def test_first_valid_and_exhausted_slot(self):
        draws=[dict(attempt=i,draw=31+32*i,coarse_valid=int(i==2)) for i in range(3)]
        selection=dict(slot=31,attempts=3,selected_draw=95,exhausted=False)
        self.assertEqual(validate_slot(draws,selection),(31,95))
        with self.assertRaises(ValueError):validate_slot(draws,{**selection,'selected_draw':31})
        draws=[dict(attempt=i,draw=31+32*i,coarse_valid=0) for i in range(4)]
        self.assertEqual(validate_slot(draws,dict(slot=31,attempts=4,selected_draw=31,exhausted=True)),(31,31))
        with self.assertRaises(ValueError):validate_slot(draws[:3],dict(slot=31,attempts=3,selected_draw=31,exhausted=True))

    def test_rejects_duplicate_attempts_and_retry_after_success(self):
        draws=[dict(attempt=i,draw=32*i,coarse_valid=1) for i in range(2)]
        selection=dict(slot=0,attempts=2,selected_draw=32,exhausted=False)
        with self.assertRaises(ValueError):validate_slot(draws,selection)
        with self.assertRaises(ValueError):validate_slot([draws[0],draws[0]],selection)
        draws[0]['coarse_valid']=0;draws[1]['draw']=33
        with self.assertRaises(ValueError):validate_slot(draws,selection)

    def test_existing_scoring_arms_unchanged(self):
        self.assertEqual(scoring_arms({}),('latent','decoder','factorial'))
        self.assertEqual(scoring_arms(dict(noise_arms=['raw','latent'],samples=32,max_attempts=4)),('raw','latent'))
        with self.assertRaises(ValueError):scoring_arms(dict(noise_arms=['latent'],samples=32,max_attempts=4))

    def test_raw_coverage_parent_identity(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'parent.json'
            rows=[dict(target_id=str(i),family=str(i),category='multistate',setting='cfg2/latent',coarse_valid_fraction=.75,coverage={'2.0':{'32':.5}}) for i in range(48)]
            parent=dict(status='complete',protocol_sha256='fixed',definitions={'states':'frozen'},rows=rows);path.write_text(json.dumps(parent))
            actual=copy.deepcopy(parent)
            for r in actual['rows']:r['setting']='cfg2/raw'
            c=dict(parent_scores=str(path),parent_scores_sha256=sha(path),primary_guidance=2)
            validate_retry_parent(actual,c)
            actual['rows'][0]['coverage']['2.0']['32']=1.
            with self.assertRaises(ValueError):validate_retry_parent(actual,c)
            actual=copy.deepcopy(parent);actual['rows']=[]
            with self.assertRaises(ValueError):validate_retry_parent(actual,c)

    def test_complete_storage_audit_retains_exhausted_outputs_and_rejects_tampering(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);panel=root/'panel.json';evidence=root/'evidence.json'
            rows=[dict(query_id=str(i),family=str(i),length=4) for i in range(48)]
            panel.write_text(json.dumps(dict(development=rows)));evidence.write_text('{}')
            c=dict(samples=32,max_attempts=4,noise_arms=['raw','latent'],primary_guidance=1,name='test')
            for key,path in dict(panel=panel,protocol=evidence,native_manifest=evidence,capacity_report=evidence).items():c[key]=str(path);c[key+'_sha256']=sha(path)
            m=dict(status='complete',training_updates_executed=0,config=c,targets=[dict(id=r['query_id']) for r in rows],controls=[],parent_controls=[],draws=[],selections=[],batches=[])
            with h5py.File(root/'predictions.h5','w') as h:
                for row in rows:
                    ident=row['query_id'];m['controls'].append(dict(target_id=ident,ca_rmsd=0.,ca_lddt=1.))
                    for a in range(4):
                        m['batches'].append(dict(target_id=ident,attempt=a,batch=32,seconds=1.,peak_reserved_bytes=1024))
                        for k in range(32):m['draws'].append(dict(target_id=ident,slot=k,attempt=a,draw=k+32*a,coarse_valid=0))
                    for k in range(32):m['selections'].append(dict(target_id=ident,slot=k,attempts=4,selected_draw=k,exhausted=True))
                    g=h.create_group(ident+'/cfg1');attempts=g.create_group('attempts')
                    attempts.create_dataset('draw_indices',data=np.arange(128));attempts.create_dataset('backbone',data=np.zeros((128,4,4,3)))
                    for mode in ('raw','latent'):
                        q=g.create_group(mode);q.create_dataset('backbone',data=np.zeros((32,4,4,3)));q.create_dataset('seed_indices',data=np.stack([np.arange(32),np.zeros(32)],axis=1))
            (root/'manifest.json').write_text(json.dumps(m))
            result=analyze(m,root)
            self.assertEqual(result['attempts'],6144);self.assertEqual(result['exhausted'],1536);self.assertEqual(result['recovered'],0)
            with h5py.File(root/'predictions.h5','a') as h:h['0/cfg1/latent/backbone'][0,0,0,0]=1.
            with self.assertRaises(ValueError):analyze(m,root)

    def test_registered_retry_job_starts_exactly_one_cpu_scorer(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);(root/'runs/retry_ensemble_123').mkdir(parents=True)
            (root/'runs/retry_ensemble_123/manifest.json').write_text(json.dumps({'status':'complete'}))
            job=dict(id='123',completion_action='summarize_retry_ensemble',code_commit='abc',code_snapshot=str(root/'snapshot'))
            (root/'runs/jobs.json').write_text(json.dumps({'jobs':[job]}));(root/'runs/local_jobs.json').write_text(json.dumps({'jobs':[]}))
            with patch('start_state_scoring.subprocess.run') as run:
                self.assertEqual(start(root,'123'),'esm-proae-state-scores-123.service')
                start(root,'123');self.assertEqual(run.call_count,1)
                command=run.call_args.args[0];self.assertIn(str(root/'runs/retry_ensemble_123'),command)
                self.assertIn('--property=CPUQuota=100%',command)
                with self.assertRaises(ValueError):start(root,'999')

if __name__=='__main__':unittest.main()
