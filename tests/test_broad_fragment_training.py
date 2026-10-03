import json
import tempfile
import unittest
from pathlib import Path

from broad_fragment_training import audit_broad
from prepare_overfit import sha


class BroadTrainingLineageTests(unittest.TestCase):
    def test_declared_data_change_cannot_change_other_training_settings(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); (root / 'configs').mkdir(); parent = root / 'parent'; parent.mkdir()
            def write(path, data):
                path.write_text(json.dumps(data)); return path
            protocol = write(root / 'configs/protocol.json', dict(broad_short_corpus=True, parent='parent',
                arms={'control_weight3': dict(corpus='control512', motif_mass=None)}, weight=3., seed=123,
                total_prior_updates=6000, updates=2000, evaluation_steps=[500, 2000],
                sampling_control_mode='same_batch_repeat', assembly_protocol='configs/assembly.json'))
            assembly = write(root / 'configs/assembly.json', {})
            pc = dict(fragments_sha256='original', latent_motif_weight=3., sampling_control_mode='same_batch_repeat',
                      evaluation_train_ids=['0'], batches={'128': 64}, distance_precision='fp64')
            mp = write(parent / 'manifest.json', dict(status='complete', updates=2000, config=pc))
            rp = write(root / 'parent_report.json', dict(status='complete', manifest_sha256=sha(mp), total_training_updates=6000))
            ckpt = write(parent / 'ema_2000.ckpt', {})
            predictions = write(parent / 'evaluation_2000.h5', {})
            fragments = write(root / 'fragments.h5', {})
            shards = []
            for i in range(4):
                sm = write(root / f'shard{i}.json', {})
                sf = write(root / f'shard{i}.h5', {})
                sr = write(root / f'report{i}.json', dict(status='complete', data_gate_passed=True,
                    partition=i, manifest_sha256=sha(sm), fragments_sha256=sha(sf)))
                shards.append(dict(manifest=str(sm), manifest_sha256=sha(sm), report=str(sr), report_sha256=sha(sr),
                                   fragments=str(sf), fragments_sha256=sha(sf)))
            dm = write(root / 'data.json', dict(status='complete', training_gate_passed=True,
                training_protein_count=512, corpus='control512', conditions_per_training_protein=12,
                original_proteins_preserved=512, development_proteins_preserved=16, fragments_sha256=sha(fragments),
                config=dict(base_fragments_sha256='original', protocol_sha256=sha(assembly), shards=shards,
                            training_targets=[dict(id=str(i)) for i in range(512)])))
            dr = write(root / 'data_report.json', dict(status='complete', training_gate_passed=True,
                training_protein_count=512, fragments_sha256=sha(fragments), manifest_sha256=sha(dm)))
            c = dict(pc, extension_arm='control_weight3', corpus='control512', motif_mass=None, seed=123,
                     total_prior_updates=6000, training_protein_count=512, profile_only=True, updates=40, evaluation_steps=[40])
            for key, path in [('extension_protocol', protocol), ('broad_corpus_protocol', protocol),
                              ('warm_protocol', protocol), ('latent_weight_protocol', protocol),
                              ('warm_parent_manifest', mp), ('warm_parent_report', rp), ('warm_predictions', predictions),
                              ('checkpoint', ckpt), ('data_manifest', dm), ('data_report', dr),
                              ('fragments', fragments), ('expanded_protocol', assembly)]:
                c[key], c[key + '_sha256'] = str(path), sha(path)
            self.assertEqual(audit_broad(c)['training_protein_count'], 512)
            for key, value in [('motif_mass', .5), ('seed', 124), ('batches', {'128': 32}),
                               ('training_protein_count', 8192), ('evaluation_train_ids', ['1']),
                               ('distance_precision', 'fp32'), ('augmentation_protocol', 'unplanned'),
                               ('freeze_trunk', True)]:
                with self.subTest(key=key), self.assertRaises(ValueError):
                    audit_broad(dict(c, **{key: value}))
