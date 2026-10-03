import json,tempfile,unittest
from pathlib import Path
from fragment_weight_breadth import audit
from prepare_overfit import sha


class WeightedBreadthTests(unittest.TestCase):
    def test_only_weight_changes_and_exposure_stays_matched(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);parent=root/'baseline';parent.mkdir()
            path=parent/'manifest.json';protocol=root/'protocol.json'
            pc=dict(seed=24,batches={'128':64},training_protein_count=512,warm_start=True,checkpoint_sha256='checkpoint',fragments_sha256='data',profile_only=False,updates=2000,evaluation_steps=[500,2000])
            path.write_text(json.dumps(dict(status='complete',updates=2000,config=pc)))
            protocol.write_text(json.dumps(dict(baseline='baseline',updates=2000,weight=3,training_protein_count=512)))
            c=dict(pc,profile_only=True,updates=40,evaluation_steps=[40],latent_motif_weight=3,weight_breadth_protocol=str(protocol),weight_breadth_protocol_sha256=sha(protocol),weight_breadth_baseline=str(path),weight_breadth_baseline_sha256=sha(path))
            audit(c);audit(dict(c,profile_only=False,updates=2000,evaluation_steps=[500,2000]))
            for key,value in [('seed',25),('latent_motif_weight',4),('fragments_sha256','other'),('checkpoint_sha256','other'),('training_protein_count',128),('updates',80),('sampling_control_mode','same_batch_repeat'),('rollout_motif',True),('extension_protocol','new')]:
                with self.subTest(key=key),self.assertRaises(ValueError):audit(dict(c,**{key:value}))
            path.write_text(path.read_text()+' ')
            with self.assertRaises(ValueError):audit(c)
