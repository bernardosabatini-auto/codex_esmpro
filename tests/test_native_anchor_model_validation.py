import copy
import json
from pathlib import Path
import unittest
from native_anchor_model_validation import check_recipe
from compare_native_anchor_models import verify_outcome


class ModelValidationRecipeTests(unittest.TestCase):
    def setUp(self):
        root=Path(__file__).resolve().parents[1]
        self.base=json.loads((root/'configs/fragment_preference_calibration_protocol.json').read_text())
        self.spec=json.loads((root/'configs/native_anchor_model_validation_protocol.json').read_text())

    def test_preserves_full_budget_and_original_noise(self):
        check_recipe(self.spec,self.base)
        for key,value in [('samples',8),('seed',17),('num_sequences',4),('steps',20),('condition','f30_center'),('cohort','development')]:
            with self.subTest(key=key):
                bad=copy.deepcopy(self.spec);bad[key]=value
                with self.assertRaises(ValueError):check_recipe(bad,self.base)

    def test_requires_matching_final_training_controls(self):
        for key,value in [('historical_condition','f30_center'),('historical_prefix','train/conditioned'),('historical_seed',1)]:
            with self.subTest(key=key):
                bad=copy.deepcopy(self.spec);bad[key]=value
                with self.assertRaises(ValueError):check_recipe(bad,self.base)

    def test_cannot_pool_constraints_across_refolds(self):
        from latentfold.fragment_designability import same_refold_success
        raw=dict(coarse_valid=True,motif_ca_rmsd=.2,motif_drms=.2)
        folds=[dict(raw,sc_tm=.8,scaffold_tm=.3),dict(raw,sc_tm=.8,scaffold_tm=.8,motif_ca_rmsd=2.)]
        r=dict(raw=raw,refolds=folds,**same_refold_success(raw,folds),scaffold_joint_success=False,scaffold_successful_refold_indices=[])
        verify_outcome(r)
        with self.assertRaises(ValueError):verify_outcome(dict(r,scaffold_joint_success=True,scaffold_successful_refold_indices=[0]))

    def test_watcher_callback_needs_no_model_imports(self):
        import os,subprocess,sys
        root=Path(__file__).resolve().parents[1]
        env=dict(os.environ,PYTHONPATH=str(root/'scripts'))
        code='from pathlib import Path; from compare_fragment_preferences import ready_command; import tempfile; t=tempfile.TemporaryDirectory(); assert ready_command(Path(t.name)) is None'
        subprocess.run([sys.executable,'-c',code],cwd='/tmp',env=env,check=True)

    def test_completed_audit_reuse_requires_unchanged_artifacts(self):
        import tempfile
        from unittest.mock import patch
        import summarize_fragment_preference_refold as summary
        from prepare_overfit import sha
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);run=root/'run';run.mkdir()
            (run/'manifest.json').write_text('{}');(run/'refolded.h5').write_bytes(b'original')
            def result(_):return dict(status='complete',manifest_sha256=sha(run/'manifest.json'),refolded_sha256=sha(run/'refolded.h5'))
            with patch('sys.argv',['audit','--runs',str(run),'--output',str(root/'report')]),patch.object(summary,'analyze',side_effect=result) as analyze:
                summary.main();summary.main();self.assertEqual(analyze.call_count,1)
                (run/'refolded.h5').write_bytes(b'changed');summary.main();self.assertEqual(analyze.call_count,2)

    def test_comparison_waits_for_late_cpu_diversity(self):
        import tempfile
        from compare_native_anchor_models import ready_command
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);(root/'runs').mkdir();(root/'reports').mkdir()
            jobs={'positive':['1','2','3','4'],'contrastive':['5','6','7','8']}
            pending={arm:str(root/'reports'/f'{arm}_diversity.json') for arm in ['parent6000','positive','contrastive']}
            path=root/'runs/native_anchor_model_comparison.json';path.write_text(json.dumps(dict(jobs=jobs,diversity_pending=pending)))
            (root/'runs/jobs.json').write_text(json.dumps(dict(jobs=[dict(id=i,completion_action='summarize_fragment_preference_refold') for v in jobs.values() for i in v])))
            for ids in jobs.values():
                for i in ids:(root/f'reports/fragment_preference_refold_{i}.json').write_text('{"status":"complete"}')
            self.assertIsNone(ready_command(root))
            for p in pending.values():Path(p).write_text('{"status":"complete"}')
            self.assertIsNotNone(ready_command(root))
            plan=json.loads(path.read_text());self.assertNotIn('diversity_pending',plan);self.assertEqual(set(plan['diversity']),set(pending))


if __name__=='__main__':unittest.main()
