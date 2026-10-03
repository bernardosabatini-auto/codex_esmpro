import json
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from broad_fragment_followups import advance, completed_report, existing_job, ARMS, graph_layout, generation_paths


class BroadFollowupTests(unittest.TestCase):
    def test_cross_graph_rejects_missing_or_swapped_routing(self):
        arms, conditions = graph_layout('cross')
        self.assertEqual(arms, ('motif', 'all'))
        self.assertEqual(conditions, ('c20_center',))
        self.assertEqual(generation_paths('cross', 'c20_center', 'all')[1],
                         'runs/fragment_cross_eval_all_20261003.json')
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); jobs = []; parents = {}
            for arm, jid in zip(arms, ['123', '124']):
                snap = root / jid / 'entry_configs'; snap.mkdir(parents=True)
                (snap / '0.json').write_text(json.dumps(dict(extension_arm=arm, profile_only=False,
                    updates=2000, broad_corpus_protocol_sha256='bound', freeze_trunk=True,
                    fragment_cross_attention=dict(cross_route=arm))))
                jobs.append(dict(id=jid, completion_action='summarize_fragment_training',
                                 code_snapshot=str(snap.parent))); parents[arm] = jid
            plan = dict(study='cross', parents=parents, training_protocol_sha256='bound')
            self.assertEqual(advance(root, plan, jobs, {}, dry_run=True)['phase'], 'waiting_training')
            (root / 'reports').mkdir()
            (root / 'reports/fragment_cross_training_20261003.json').write_text(json.dumps(
                dict(status='complete', profile_only=False, matched_training_updates=2000, protocol_sha256='bound')))
            with patch('broad_fragment_followups.completed_report', return_value={'status':'complete'}):
                self.assertEqual(advance(root, plan, jobs, {}, dry_run=True)['script'],
                                 'slurm/fragment_cross_eval_motif_rtx.sbatch')
            p = root / '123/entry_configs/0.json'; c = json.loads(p.read_text())
            c['fragment_cross_attention']['cross_route'] = 'all'; p.write_text(json.dumps(c))
            with self.assertRaises(ValueError):
                advance(root, plan, jobs, {}, dry_run=True)
            c.pop('fragment_cross_attention'); p.write_text(json.dumps(c))
            with self.assertRaises(ValueError):
                advance(root, plan, jobs, {}, dry_run=True)

    def test_quality_graph_requires_declared_condition_selection(self):
        arms,conditions=graph_layout('quality')
        self.assertEqual(arms,('control','quality'));self.assertEqual(conditions,('c20_center',))
        self.assertEqual(generation_paths('quality','c20_center','quality')[1],'runs/fragment_quality_eval_quality_20261003.json')
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);jobs=[];parents={}
            for arm,jid in zip(arms,['123','124']):
                snap=root/jid/'entry_configs';snap.mkdir(parents=True)
                (snap/'0.json').write_text(json.dumps(dict(extension_arm=arm,profile_only=False,updates=2000,broad_corpus_protocol_sha256='bound',freeze_trunk=True,condition_selection='fixed')))
                jobs.append(dict(id=jid,completion_action='summarize_fragment_training',code_snapshot=str(snap.parent)));parents[arm]=jid
            plan=dict(study='quality',parents=parents,training_protocol_sha256='bound')
            self.assertEqual(advance(root,plan,jobs,{},dry_run=True)['phase'],'waiting_training')
            (root/'reports').mkdir();(root/'reports/fragment_quality_training_20261003.json').write_text(json.dumps(dict(status='complete',profile_only=False,matched_training_updates=2000,protocol_sha256='bound')))
            with patch('broad_fragment_followups.completed_report',return_value={'status':'complete'}):
                self.assertEqual(advance(root,plan,jobs,{},dry_run=True)['script'],'slurm/fragment_quality_eval_control_rtx.sbatch')
            p=root/'123/entry_configs/0.json';c=json.loads(p.read_text());c.pop('condition_selection');p.write_text(json.dumps(c))
            with self.assertRaises(ValueError):advance(root,plan,jobs,{},dry_run=True)

    def test_frozen_graph_is_two_arms_one_task_and_requires_frozen_parents(self):
        arms,conditions=graph_layout('frozen')
        self.assertEqual(conditions,('c20_center',))
        self.assertEqual(len(arms),2)
        self.assertEqual(generation_paths('frozen','c20_center','control_frozen')[1],'runs/fragment_frozen_eval_control_20261003.json')
        with self.assertRaises(ValueError):graph_layout('unknown')
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);jobs=[];parents={}
            for arm,jid in zip(arms,['123','124']):
                snap=root/jid/'entry_configs';snap.mkdir(parents=True)
                (snap/'0.json').write_text(json.dumps(dict(extension_arm=arm,profile_only=False,updates=2000,broad_corpus_protocol_sha256='bound',freeze_trunk=True)))
                jobs.append(dict(id=jid,completion_action='summarize_fragment_training',code_snapshot=str(snap.parent)));parents[arm]=jid
            plan=dict(study='frozen',parents=parents,training_protocol_sha256='bound')
            self.assertEqual(advance(root,plan,jobs,{},dry_run=True)['phase'],'waiting_training')
            (root/'reports').mkdir()
            (root/'reports/fragment_frozen_training_20261003.json').write_text(json.dumps(dict(status='complete',profile_only=False,matched_training_updates=2000,protocol_sha256='bound')))
            with patch('broad_fragment_followups.completed_report',return_value={'status':'complete'}):
                ready=advance(root,plan,jobs,{},dry_run=True)
            self.assertEqual(ready['phase'],'ready_generation')
            self.assertEqual(ready['script'],'slurm/fragment_frozen_eval_control_rtx.sbatch')
            p=root/'123/entry_configs/0.json';c=json.loads(p.read_text());c['freeze_trunk']=False;p.write_text(json.dumps(c))
            with self.assertRaises(ValueError):advance(root,plan,jobs,{},dry_run=True)

    def test_duplicate_scripts_and_failed_predecessors_stop(self):
        j=dict(id='123',script='slurm/own.sbatch')
        self.assertIs(existing_job([j],j['script']),j)
        self.assertIsNone(existing_job([j],'slurm/missing.sbatch'))
        with self.assertRaises(ValueError):existing_job([j,j],j['script'])
        state=dict(jobs={'123':dict(tasks={'123':dict(state='FAILED')})})
        with self.assertRaises(ValueError):completed_report(Path('/unused'),j,state,'fragment_training')
        self.assertIsNone(completed_report(Path('/unused'),j,{},'fragment_training'))

    def test_waits_for_registered_final_training_and_rejects_wrong_scope(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);jobs=[]
            for arm,jid in zip(ARMS,['123','124','125','126']):
                snap=root/jid/'entry_configs';snap.mkdir(parents=True);p=snap/'0.json'
                p.write_text(json.dumps(dict(extension_arm=arm,profile_only=False,updates=2000,broad_corpus_protocol_sha256='bound')))
                jobs.append(dict(id=jid,completion_action='summarize_fragment_training',code_snapshot=str(snap.parent)))
            plan=dict(parents=dict(zip(ARMS,['123','124','125','126'])),training_protocol_sha256='bound')
            result=advance(root,plan,jobs,{},dry_run=True)
            self.assertEqual(result['phase'],'waiting_training')
            p=root/'123/entry_configs/0.json';p.write_text(json.dumps(dict(extension_arm=ARMS[0],profile_only=True,updates=40,broad_corpus_protocol_sha256='bound')))
            with self.assertRaises(ValueError):advance(root,plan,jobs,{},dry_run=True)
            plan['parents'][ARMS[0]]='999'
            with self.assertRaises(ValueError):advance(root,plan,jobs,{},dry_run=True)
