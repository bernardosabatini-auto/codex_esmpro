import json
import tempfile
import unittest
from pathlib import Path

import h5py
import numpy as np

from fragment_fixed_coverage import bind_coverage, split_coverage
from prepare_overfit import sha


class FixedCoverageTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = root = Path(tmp.name)
        (root/'runs/generation').mkdir(parents=True)
        self.protocol = dict(covered_assays=[['weighted','runs/fixed.json','fixed_run','native_run']])
        pp = root/'protocol.json'
        pp.write_text(json.dumps(self.protocol))
        bb = np.arange(60, dtype='float32').reshape(5, 4, 3)
        fragment = bb[1:4].copy()
        self.pred = root/'inputs.h5'
        with h5py.File(self.pred, 'w') as f:
            f.create_dataset('conditioned/case', data=bb[None])
            f.create_dataset('motifs/case', data=fragment)
        recipe = dict(num_sequences=8, temperature=.1, mpnn_seed=1, seed=2,
                      precision='fp32', dependencies=[], teacher_artifacts=[], usalign_sha256='align')
        entry = dict(name='gen',mode='conditioned',target_id='case',slot=0,dataset='conditioned/case',
                     fixed_sequence='ACD',fixed_start=1,motif_start=1)
        self.cfg = dict(recipe, assay='trained_fragment', predictions=str(self.pred),
                        predictions_sha256=sha(self.pred), entries=[entry])
        (root/'runs/fixed.json').write_text(json.dumps(self.cfg))
        self.c = dict(recipe, protocol=str(pp), generation_manifest=str(root/'runs/generation/manifest.json'),
                      covered_assays=bind_coverage(root, self.protocol))
        self.selected = {('weighted','case',0):(bb,fragment,'ACD',1,'family'),
                         ('weighted','outside',2):(bb,fragment,'ACD',1,'another')}

    def test_reuses_only_the_exact_fixed_sample_without_losing_denominator(self):
        remaining, reused = split_coverage(self.c, self.selected)
        self.assertEqual(set(remaining), {('weighted','outside',2)})
        self.assertEqual(len(reused), 1)
        self.assertEqual(len(self.selected), 2)
        self.assertEqual(reused[0][1]['slot'], 0)

    def test_changed_backbone_rejected_before_reuse(self):
        with h5py.File(self.pred, 'a') as f:
            f['conditioned/case'][0,0,0,0] += 1
        with self.assertRaises(ValueError):
            split_coverage(self.c, self.selected)

    def test_changed_sequence_budget_rejected(self):
        self.cfg['num_sequences'] = 16
        (self.root/'runs/fixed.json').write_text(json.dumps(self.cfg))
        self.c['covered_assays'] = bind_coverage(self.root, self.protocol)
        with self.assertRaises(ValueError):
            split_coverage(self.c, self.selected)

    def test_changed_motif_sequence_rejected(self):
        self.selected['weighted','case',0] = (*self.selected['weighted','case',0][:2], 'AAA', 1, 'family')
        with self.assertRaises(ValueError):
            split_coverage(self.c, self.selected)


if __name__ == '__main__':
    unittest.main()
