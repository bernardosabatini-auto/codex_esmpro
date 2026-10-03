import json
import tempfile
import unittest
from pathlib import Path

from broad_fragment_followups import advance, completed_report, existing_job, ARMS


class BroadFollowupTests(unittest.TestCase):
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
