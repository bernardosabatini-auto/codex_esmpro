import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from overfit_checkpoint_analysis import tick


class CheckpointAnalysisTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);(self.root/'runs/watch').mkdir(parents=True)
        (self.root/'runs/overfit_checkpoint_analyses.json').write_text(json.dumps(dict(comparisons=[dict(kind='empirical',jobs=['1','2','3'],steps=[500,2000])])))
        self.registry=dict(jobs=[dict(id=str(i),completion_action='summarize_overfit') for i in (1,2,3)])
        self.scores=[dict(step=step,guidance=g,target_id=str(i)) for step in (0,500) for g in (1,2) for i in range(32)]
        for i in (1,2,3):
            p=self.root/'runs'/f'overfit_{i}';p.mkdir();(p/'manifest.json').write_text(json.dumps(dict(status='running',updates=500,scores=self.scores)))

    def test_once_only_cpu_analysis_and_no_submission(self):
        state={};run=Mock();events=tick(self.root,state,self.registry,dict(python='python'),run)
        self.assertEqual(len(events),1);self.assertEqual(run.call_count,2)
        for call in run.call_args_list:
            self.assertEqual(call.kwargs['env']['CUDA_VISIBLE_DEVICES'],'')
            self.assertNotIn('sbatch',call.args[0])
        tick(self.root,state,self.registry,dict(python='python'),run)
        self.assertEqual(run.call_count,2)

    def test_partial_checkpoint_waits_and_scope_is_enforced(self):
        p=self.root/'runs/overfit_3/manifest.json';d=json.loads(p.read_text());d['scores'].pop();p.write_text(json.dumps(d))
        run=Mock();self.assertEqual(tick(self.root,{},self.registry,{},run),[]);run.assert_not_called()
        self.registry['jobs'].pop()
        with self.assertRaises(ValueError):tick(self.root,{},self.registry,{},run)

    def test_failure_retries_without_marking_handled(self):
        state={};run=Mock(side_effect=RuntimeError('analysis failure'))
        self.assertIn('failed',tick(self.root,state,self.registry,dict(python='python'),run)[0][0])
        self.assertFalse(state['overfit_checkpoints']['empirical_500'].get('handled',False))
        tick(self.root,state,self.registry,dict(python='python'),run)
        self.assertEqual(run.call_count,1)

    def test_expanded_waits_for_both_seeds_and_scores_all122(self):
        spec=dict(kind='expanded',jobs=['1','2','3','4'],steps=[500,2000])
        (self.root/'runs/overfit_checkpoint_analyses.json').write_text(json.dumps(dict(comparisons=[spec])))
        self.registry['jobs'].append(dict(id='4',completion_action='summarize_overfit'))
        rows=[dict(step=s,guidance=1,target_id=str(i)) for s in (0,500) for i in range(122)]
        for jid in spec['jobs']:
            path=self.root/'runs'/f'overfit_{jid}';path.mkdir(exist_ok=True)
            (path/'manifest.json').write_text(json.dumps(dict(status='running',updates=500,scores=rows if jid!='4' else rows[:-1])))
        state={};run=Mock();self.assertEqual(tick(self.root,state,self.registry,dict(python='python'),run),[])
        (self.root/'runs/overfit_4/manifest.json').write_text(json.dumps(dict(status='running',updates=500,scores=rows)))
        self.assertEqual(len(tick(self.root,state,self.registry,dict(python='python'),run)),1)
        self.assertEqual(run.call_count,1);self.assertTrue(run.call_args.args[0][1].endswith('compare_expanded.py'))
        self.assertNotIn('frequency_report',state['overfit_checkpoints']['expanded_500'])

    def test_tail_waits_for_frozen_checks_and_uses_explicit_pairs(self):
        spec=dict(kind='tail',jobs=['1','2','3','4'],steps=[500,2000])
        (self.root/'runs/overfit_checkpoint_analyses.json').write_text(json.dumps(dict(comparisons=[spec])))
        self.registry['jobs'].append(dict(id='4',completion_action='summarize_overfit'))
        rows=[dict(step=s,guidance=1,target_id=str(i)) for s in (0,500) for i in range(122)]
        for jid in spec['jobs']:
            path=self.root/'runs'/f'overfit_{jid}';path.mkdir(exist_ok=True)
            (path/'manifest.json').write_text(json.dumps(dict(status='running',updates=500,scores=rows,training_subset=dict(frozen_unchanged=True,verified_update=0 if jid=='4' else 500))))
        state={};run=Mock();self.assertEqual(tick(self.root,state,self.registry,dict(python='python'),run),[])
        p=self.root/'runs/overfit_4/manifest.json';m=json.loads(p.read_text());m['training_subset']['verified_update']=500;p.write_text(json.dumps(m))
        self.assertEqual(len(tick(self.root,state,self.registry,dict(python='python'),run)),1)
        command=run.call_args.args[0];self.assertIn('--full',command);self.assertIn('--tail',command);self.assertNotIn('--runs',command)
        self.assertEqual(run.call_count,1)
        tick(self.root,state,self.registry,dict(python='python'),run);self.assertEqual(run.call_count,1)


if __name__=='__main__':unittest.main()
