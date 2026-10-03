import tempfile
import unittest
from pathlib import Path
import h5py
import numpy as np
import torch
from extra_fragment_validation_core import load_conditions
from train_fragment_conditioning import load_data


class ExtraFragmentInputsTests(unittest.TestCase):
    def test_historical_parity_and_no_reference_leakage(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'fragments.h5'
            with h5py.File(path,'w') as f:
                f.create_group('train')
                g=f.create_group('development/example');g.attrs.update(length=10,family='family')
                q=g.create_group('conditions/f30_center');q.attrs.update(start=3,sequence='ACD')
                q['latent']=np.arange(24,dtype=np.float32).reshape(3,8)
                q['fragment']=np.arange(36,dtype=np.float32).reshape(3,4,3)
                f['references/example/backbone']=np.ones((10,4,3),np.float32)
            expected=load_data(path)['development','example']['conditions']['f30_center']
            first=load_conditions(path,['example'])['example']
            for key in ('features','keep','coordinates'):
                self.assertTrue(torch.equal(first[key],expected[key]))
            self.assertTrue((first['features'][~first['keep']]==0).all())
            self.assertTrue((first['coordinates'][~first['keep']]==0).all())
            with h5py.File(path,'a') as f:
                f['references/example/backbone'][:]=np.nan
                f.create_group('development/unrequested_malformed')
            second=load_conditions(path,['example'])['example']
            for key in ('features','keep','coordinates'):
                self.assertTrue(torch.equal(first[key],second[key]))
            with self.assertRaises(KeyError):load_conditions(path,['missing'])
