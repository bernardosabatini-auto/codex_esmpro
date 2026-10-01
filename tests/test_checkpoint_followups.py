import json,subprocess,tempfile,unittest,sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import checkpoint_followups as controller


class FollowupTests(unittest.TestCase):
    def setup_root(self, root, count=2):
        (root/'runs/watch').mkdir(parents=True)
        nodes=[];jobs=[];watch={}
        def write(path,value):path.write_text(json.dumps(value))
        for i in range(count):
            parent=str(100+i);arm='arm'+str(i);nodes.append(dict(parent=parent,arm=arm,script=f'slurm/{arm}.sbatch',config=f'runs/{arm}.json'));jobs.append(dict(id=parent,completion_action='summarize_distillation'))
            watch[parent]=dict(tasks={parent:dict(state='COMPLETED',exit_code='0:0')})
            directory=root/f'runs/distillation_{parent}';directory.mkdir();write(directory/'manifest.json',dict(status='complete',config=dict(arm=arm),updates=2000))
        write(root/'runs/checkpoint_followups.json',dict(status='active',nodes=nodes));write(root/'runs/execution_policy.json',dict(status='active'));write(root/'runs/jobs.json',dict(jobs=jobs));write(root/'runs/watch/state.json',dict(jobs=watch))

    def test_dry_run_never_submits(self):
        with tempfile.TemporaryDirectory() as temporary,patch.object(controller.subprocess,'run') as run:
            root=Path(temporary);self.setup_root(root)
            result=controller.tick(root,dry_run=True)
            self.assertTrue(all(n['status']=='eligible' for n in result['nodes']));run.assert_not_called()

    def test_at_most_one_submission_per_tick(self):
        with tempfile.TemporaryDirectory() as temporary,patch.object(controller.subprocess,'run',return_value=subprocess.CompletedProcess([],0,stdout='{"submitted":"999"}')) as run:
            root=Path(temporary);self.setup_root(root);result=controller.tick(root)
            self.assertEqual(result['submitted'],'999');self.assertEqual(run.call_count,2)
            self.assertIn('scripts/submit_registered.py',run.call_args.args[0])
            self.assertNotIn('CUDA_VISIBLE_DEVICES',run.call_args.kwargs['env'])

    def test_cap_rejection_does_not_try_another_node(self):
        failure=subprocess.CalledProcessError(1,[],stderr='project GPU cap would be exceeded')
        with tempfile.TemporaryDirectory() as temporary,patch.object(controller.subprocess,'run',side_effect=[subprocess.CompletedProcess([],0),failure]) as run:
            root=Path(temporary);self.setup_root(root);result=controller.tick(root)
            self.assertIsNone(result['submitted']);self.assertEqual(run.call_count,2);self.assertEqual(result['nodes'][0]['status'],'retry')

    def test_existing_child_prevents_duplicate_submission(self):
        with tempfile.TemporaryDirectory() as temporary,patch.object(controller.subprocess,'run') as run:
            root=Path(temporary);self.setup_root(root,count=1);snapshot=root/'snapshot';(snapshot/'entry_configs').mkdir(parents=True);(snapshot/'entry_configs/0.json').write_text(json.dumps(dict(checkpoint=str(root/'runs/distillation_100/ema_2000.ckpt'))))
            path=root/'runs/jobs.json';registry=json.loads(path.read_text());registry['jobs'].append(dict(id='999',script='slurm/arm0.sbatch',code_snapshot=str(snapshot)));path.write_text(json.dumps(registry))
            result=controller.tick(root,dry_run=True);self.assertEqual(result['nodes'][0]['child'],'999');run.assert_not_called()
