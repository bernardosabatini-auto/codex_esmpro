import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import h5py
import numpy as np

from prepare_fragment_repetition_refold import screen, audit_inputs
from prepare_overfit import sha


class RepetitionScreenTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        self.c = c = {}
        for key in ('generation_manifest', 'generation_report', 'generation_predictions',
                    'protocol', 'fragments', 'predictions', 'usalign', 'native_predictions'):
            c[key] = str(root / key)
        spec = dict(samples=16, target_id='case', guidance=[1, 2], max_refold_backbones=33)
        Path(c['protocol']).write_text(json.dumps(spec))
        with h5py.File(c['fragments'], 'w') as f:
            v = f.create_group('development/case')
            v.attrs.update(family='family', length=5)
            q = v.create_group('conditions/f30_center')
            q.attrs.update(start=1, sequence='AAA')
            q.create_dataset('fragment', data=np.zeros((3, 4, 3)))
        with h5py.File(c['generation_predictions'], 'w') as f:
            for g in (1, 2):
                f.create_dataset(f'guidance{g}/case/backbone', data=np.broadcast_to(
                    np.arange(16)[:, None, None, None], (16, 5, 4, 3)))
        for key in ('predictions', 'usalign', 'native_predictions'):
            Path(c[key]).write_text('placeholder')
        for key in ('protocol', 'fragments', 'generation_predictions', 'predictions', 'usalign', 'native_predictions'):
            c[key + '_sha256'] = sha(c[key])
        gc = dict(target_id='case', condition='f30_center', samples=16, guidance=[1, 2],
                  fragments_sha256=c['fragments_sha256'], protocol_sha256=c['protocol_sha256'])
        Path(c['generation_manifest']).write_text(json.dumps(dict(status='complete', config=gc,
            predictions_sha256=c['generation_predictions_sha256'])))
        c['generation_manifest_sha256'] = sha(c['generation_manifest'])
        Path(c['generation_report']).write_text(json.dumps(dict(status='complete',
            manifest_sha256=c['generation_manifest_sha256'])))
        c['generation_report_sha256'] = sha(c['generation_report'])
        self.addCleanup(patch.stopall)
        patch('prepare_fragment_repetition_refold.audit_config').start()
        validity = np.ones(16, dtype=bool)
        validity[2] = False
        patch('prepare_fragment_repetition_refold.backbone_geometry', return_value={'coarse_valid': validity}).start()
        patch('prepare_fragment_repetition_refold.motif_fit', side_effect=lambda x, *args:
              dict(motif_drms=.5, motif_ca_rmsd=.5 if x[0, 0, 0] < 4 else 2.)).start()

    def test_all_matches_kept_with_full_denominator(self):
        rows, selected, _ = screen(self.c)
        self.assertEqual(len(rows), 32)
        self.assertEqual(len(selected), 6)
        self.assertEqual({k[2] for k in selected}, {0, 1, 3})
        self.assertEqual(sum(r['raw_gate_passed'] for r in rows), 6)

    def test_missing_sample_rejected_even_after_rehash(self):
        with h5py.File(self.c['generation_predictions'], 'a') as f:
            bb = f['guidance1/case/backbone'][:]
            del f['guidance1/case/backbone']
            f.create_dataset('guidance1/case/backbone', data=bb[:15])
        self.c['generation_predictions_sha256'] = sha(self.c['generation_predictions'])
        with self.assertRaises(ValueError):
            screen(self.c)

    def test_dropped_passing_sample_rejected(self):
        rows, selected, _ = screen(self.c)
        c = dict(self.c, screen_rows=rows, screens=[{'arm': 'guidance1'}, {'arm': 'guidance2'}],
                 expected_backbones=7, entries=[], dependencies=[], teacher_artifacts=[])
        with self.assertRaisesRegex(ValueError, 'Dropped or added'):
            audit_inputs(c)


if __name__ == '__main__':
    unittest.main()
