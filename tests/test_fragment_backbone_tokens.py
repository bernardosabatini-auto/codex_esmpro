import tempfile
import unittest
from pathlib import Path

import h5py
import numpy as np
import torch

from latentfold.fragment_conditioning import fragment_features
from latentfold.fragment_geometry_conditioning import FragmentGeometryAdapter
from train_fragment_conditioning import load_data


class BackboneTokenTests(unittest.TestCase):
    def test_shared_initialization_rng_and_output_parity(self):
        torch.manual_seed(77)
        base = FragmentGeometryAdapter(16, n_layers=2, n_heads=2)
        expected_rng = torch.get_rng_state().clone()
        torch.manual_seed(77)
        new = FragmentGeometryAdapter(16, n_layers=2, n_heads=2, backbone_tokens=True)
        torch.testing.assert_close(torch.get_rng_state(), expected_rng, rtol=0, atol=0)
        for key, value in base.state_dict().items():
            torch.testing.assert_close(value, new.state_dict()[key], rtol=0, atol=0)
        f, keep = fragment_features(torch.randn(4, 8), 'ACDE', length=8, start=2)
        extra = torch.zeros(8, 12)
        extra[keep] = torch.randn(4, 12)
        full = torch.cat((f, extra), -1)[None]
        keep, mask, drop = keep[None], torch.ones(1, 8, dtype=torch.bool), torch.zeros(1, dtype=torch.bool)
        torch.testing.assert_close(base(f[None], keep, mask, drop), new(full, keep, mask, drop), rtol=0, atol=0)
        new(full, keep, mask, drop).sum().backward()
        self.assertGreater(float(new.backbone_output.weight.grad.norm()), 0)
        with torch.no_grad():
            new.backbone_output.weight.normal_()
        self.assertGreater(float(new(full, keep, mask, drop).norm()), 0)
        self.assertEqual(int(torch.count_nonzero(new(full, keep, mask, ~drop))), 0)
        full[0, 0, 29] = 1
        with self.assertRaises(ValueError):
            new(full, keep, mask, drop)

    def test_only_isolated_atoms_added_without_altering_existing_inputs(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'data.h5'
            rng = np.random.default_rng(9)
            fragment = rng.normal(size=(4, 4, 3)).astype('float32')
            with h5py.File(path, 'w') as f:
                for cohort in ('train', 'development'):
                    g = f.create_group(cohort + '/case')
                    g.attrs.update(length=8, family='case')
                    q = g.create_group('conditions/f30_center')
                    q.attrs.update(start=2, sequence='ACDE')
                    q.create_dataset('latent', data=rng.normal(size=(4, 8)).astype('float32'))
                    q.create_dataset('fragment', data=fragment)
                    if cohort == 'train':
                        g.create_dataset('reference_z', data=np.ones((8, 8), 'float32'))
                        g.create_dataset('reference_backbone', data=np.ones((8, 4, 3), 'float32'))
            base, new = load_data(path), load_data(path, backbone_tokens=True)
            for key, v in new.items():
                q, old = v['conditions']['f30_center'], base[key]['conditions']['f30_center']
                torch.testing.assert_close(q['features'][:, :29], old['features'], rtol=0, atol=0)
                torch.testing.assert_close(q['coordinates'], old['coordinates'], rtol=0, atol=0)
                torch.testing.assert_close(q['features'][q['keep'], 29:], torch.from_numpy(fragment).reshape(4, 12)/10, rtol=0, atol=0)
                self.assertEqual(int(torch.count_nonzero(q['features'][~q['keep']])), 0)
                if key[0] == 'train':
                    torch.testing.assert_close(v['target'], base[key]['target'], rtol=0, atol=0)


if __name__ == '__main__':
    unittest.main()
