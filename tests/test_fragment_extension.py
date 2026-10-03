import copy,json,tempfile,unittest
from pathlib import Path
from fragment_extension import audit_extension
from prepare_overfit import sha


class ExtensionLineageTests(unittest.TestCase):
    def test_only_declared_parent_data_objective_and_exposure_are_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);parent=root/'parent';parent.mkdir();protocol=root/'protocol.json';report=root/'report.json'
            spec=dict(parents={'plain':'parent'},seed=12,total_prior_updates=4000,updates=2000,evaluation_steps=[500,2000])
            protocol.write_text(json.dumps(spec));pc=dict(fragments_sha256='f',batches={'128':64},evaluation_train_ids=['a'],initial_predictions_sha256='i',decoder_checkpoint_sha256='d',distance_precision='fp64',geometry_protocol_sha256='g')
            manifest=parent/'manifest.json';manifest.write_text(json.dumps(dict(status='complete',updates=2000,config=pc)))
            report.write_text(json.dumps(dict(status='complete',manifest_sha256=sha(manifest),total_training_updates=4000)))
            c=dict(pc,extension_protocol=str(protocol),extension_protocol_sha256=sha(protocol),extension_arm='plain',warm_protocol=str(protocol),warm_protocol_sha256=sha(protocol),warm_parent_manifest=str(manifest),warm_parent_report=str(report),total_prior_updates=4000,seed=12,checkpoint=str(parent/'ema_2000.ckpt'),warm_predictions=str(parent/'evaluation_2000.h5'),profile_only=True,updates=40,evaluation_steps=[40])
            self.assertEqual(audit_extension(c),spec)
            for key,value in [('sampling_control_mode','same_batch_repeat'),('total_prior_updates',4001),('seed',13),('latent_motif_weight',3),('fragments_sha256','other'),('checkpoint','other'),('updates',80),('evaluation_steps',[80]),('rollout_motif',{'weight':1})]:
                with self.subTest(key=key),self.assertRaises(ValueError):audit_extension(dict(copy.deepcopy(c),**{key:value}))
            manifest.write_text(json.dumps(dict(status='failed',updates=2000,config=pc)))
            with self.assertRaises(ValueError):audit_extension(c)

    def test_comparison_rejects_missing_or_different_primary_draws(self):
        from compare_fragment_extension import matched_traces,TRACE
        rows=[{k:i for k in TRACE} for i in range(2000)]
        matched_traces(rows,copy.deepcopy(rows))
        with self.assertRaises(ValueError):matched_traces(rows,rows[:-1])
        changed=copy.deepcopy(rows);changed[50]["ids"]=["different"]
        with self.assertRaises(ValueError):matched_traces(rows,changed)

    def test_capacity_panel_is_inherited_without_expanding_evaluation(self):
        from fragment_extension import validate_capacity_panel
        parent={"evaluation_train_ids":["a","b"]};c=dict(parent,extension_protocol="declared")
        validate_capacity_panel(c,parent,["a","b","c"])
        with self.assertRaises(ValueError):validate_capacity_panel(parent,parent,["a","b","c"])
        with self.assertRaises(ValueError):validate_capacity_panel(dict(c,evaluation_train_ids=["a","b","c"]),parent,["a","b","c"])
        validate_capacity_panel(parent,{},["a","b"])
