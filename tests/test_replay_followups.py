import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace
from replay_followups import nodes,tick


class FixedFollowupsTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        (self.root/'reports').mkdir()
        self.plan=dict(parents=dict(full=['1','2'],replay=['3','4']),steps=[500,2000])
        self.jobs=[dict(id=str(i),completion_action='summarize_overfit') for i in range(1,5)]
        self.watch=dict(overfit_checkpoints={},jobs={})

    def capacity(self,step,passed=True):
        (self.root/f'reports/functional_replay_comparison_{step}.json').write_text(json.dumps(dict(status='complete',step=step,matched=True,training_targets=427,replicated_capacity_retained=passed)))

    def native(self):
        path=self.root/'snapshot';(path/'entry_configs').mkdir(parents=True)
        config=dict(training_checkpoint_step=500,heads=[dict(name=f'seed{s}_{arm}',checkpoint=str(self.root/f'runs/overfit_{jid}/ema_500.ckpt')) for arm,ids in self.plan['parents'].items() if arm=='replay' for s,jid in zip((2026100171,2026100181),ids)])
        (path/'entry_configs/0.json').write_text(json.dumps(config))
        self.jobs.append(dict(id='5',script='slurm/replay_native_500_h200.sbatch',code_snapshot=str(path)))
        self.watch['jobs']['5']=dict(tasks={'5':dict(state='COMPLETED')})
        (self.root/'reports/replay_native_5.json').write_text(json.dumps(dict(status='complete',step=500,training_targets=427,replay_targets=390,summaries={'seed2026100171_replay_cfg1':dict(quality_passed=True),'seed2026100181_replay_cfg1':dict(quality_passed=False)})))

    def test_wait_then_exact_native_readiness(self):
        self.assertTrue(all(n['status']=='waiting' for n in nodes(self.root,self.plan,self.jobs,self.watch)))
        self.capacity(500)
        self.watch['overfit_checkpoints']['replay_500']=dict(handled=True,jobs=['1','2','3','4'])
        result=nodes(self.root,self.plan,self.jobs,self.watch)
        self.assertEqual(result[0]['status'],'eligible');self.assertEqual(sum(n['status']=='eligible' for n in result),1)
        self.watch['overfit_checkpoints']['replay_500']['jobs'][0]='999'
        with self.assertRaises(ValueError):nodes(self.root,self.plan,self.jobs,self.watch)

    def test_failed_capacity_never_advances_native_or_ensemble(self):
        self.capacity(500,False)
        self.watch['overfit_checkpoints']['replay_500']=dict(handled=True,jobs=['1','2','3','4'])
        self.assertEqual([n['status'] for n in nodes(self.root,self.plan,self.jobs,self.watch)[:3]],['capacity_failed']*3)

    def test_each_head_gate_and_duplicate_protection(self):
        self.native();result=nodes(self.root,self.plan,self.jobs,self.watch)
        self.assertEqual([n['status'] for n in result[:3]],['submitted','eligible','quality_failed'])
        self.assertEqual(result[1]['parent'],'5')
        self.jobs.append(self.jobs[-1].copy())
        with self.assertRaises(ValueError):nodes(self.root,self.plan,self.jobs,self.watch)

    def test_unregistered_or_wrong_snapshot_rejected(self):
        self.native();path=self.root/'snapshot/entry_configs/0.json';d=json.loads(path.read_text());d['heads'][0]['checkpoint']='other';path.write_text(json.dumps(d))
        with self.assertRaises(ValueError):nodes(self.root,self.plan,self.jobs,self.watch)
        self.jobs.pop();self.jobs.pop()
        with self.assertRaises(ValueError):nodes(self.root,self.plan,self.jobs,self.watch)

    def test_failure_uses_watcher_terminal_state(self):
        self.watch['jobs']['3']=dict(tasks={'3':dict(state='FAILED')})
        self.assertTrue(all(n['status']=='failed_predecessor' for n in nodes(self.root,self.plan,self.jobs,self.watch)))
        self.native();self.watch['jobs']['5']['tasks']['5']['state']='FAILED'
        self.assertEqual(nodes(self.root,self.plan,self.jobs,self.watch)[1]['status'],'failed_predecessor')

    def setup_tick(self,deadline):
        (self.root/'runs/watch').mkdir(parents=True)
        (self.root/'runs/replay_followups.json').write_text(json.dumps(dict(self.plan,status='active',code_sha256={})))
        (self.root/'runs/execution_policy.json').write_text(json.dumps(dict(status='active',deadline_utc=deadline)))
        (self.root/'runs/jobs.json').write_text(json.dumps(dict(jobs=self.jobs)))
        self.watch['overfit_checkpoints']={f'replay_{s}':dict(handled=True,jobs=['1','2','3','4']) for s in (500,2000)}
        (self.root/'runs/watch/state.json').write_text(json.dumps(self.watch))
        for step in (500,2000):self.capacity(step)

    def test_one_guarded_submission_per_tick(self):
        self.setup_tick('2099-01-01T00:00:00+00:00')
        with patch('replay_followups.subprocess.run',return_value=SimpleNamespace(stdout='{"submitted":"9"}')) as run:
            d=tick(self.root)
        self.assertEqual(d['submitted'],'9');self.assertEqual(run.call_count,2)
        commands=[c.args[0] for c in run.call_args_list]
        self.assertIn('scripts/submit_registered.py',commands[1]);self.assertNotIn('sbatch',commands[1])

    def test_deadline_closes_without_gpu_submission(self):
        self.setup_tick('2000-01-01T00:00:00+00:00')
        with patch('replay_followups.subprocess.run') as run:d=tick(self.root)
        self.assertEqual(d['status'],'resolved');self.assertIsNone(d['submitted'])
        self.assertEqual(run.call_count,1);self.assertEqual(run.call_args.args[0][:3],['systemctl','--user','stop'])


if __name__=='__main__':unittest.main()
