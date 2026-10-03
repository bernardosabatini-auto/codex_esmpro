import tempfile
import unittest
from pathlib import Path

import h5py
import numpy as np
from assemble_broad_fragment_data import equal_group


class AssemblyPreservationTests(unittest.TestCase):
    def test_nested_development_conditions_must_be_exact(self):
        with tempfile.TemporaryDirectory() as temp, h5py.File(Path(temp) / 'inputs.h5', 'w') as f:
            a = f.create_group('original')
            q = a.create_group('protein/conditions/f30_center')
            q.attrs.update(start=12, sequence='ACD')
            q['latent'] = np.zeros((3, 8), np.float32)
            f.copy(a, f, name='copy')
            equal_group(a, f['copy'])
            f['copy/protein/conditions/f30_center'].attrs['sequence'] = 'ACE'
            with self.assertRaises(ValueError):
                equal_group(a, f['copy'])
            f['copy/protein/conditions/f30_center'].attrs['sequence'] = 'ACD'
            f['copy/protein/conditions/f30_center/latent'][0, 0] = 1
            with self.assertRaises(ValueError):
                equal_group(a, f['copy'])
