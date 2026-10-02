import tempfile,unittest
from pathlib import Path
import h5py,numpy as np,torch
from train_fragment_conditioning import load_data


class FragmentRepresentationTests(unittest.TestCase):
    def test_ablation_removes_only_codes_and_is_insensitive_to_their_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'fragments.h5';rng=np.random.default_rng(31)
            with h5py.File(path,'w') as f:
                for cohort in ('train','development'):
                    g=f.create_group(cohort+'/protein');g.attrs['length']=10;g.attrs['family']='family'
                    if cohort=='train':g.create_dataset('reference_z',data=rng.normal(size=(10,8)).astype('f'));g.create_dataset('reference_backbone',data=rng.normal(size=(10,4,3)).astype('f'))
                    q=g.create_group('conditions/f30_center');q.attrs['start']=3;q.attrs['sequence']='ACDE';q.create_dataset('latent',data=rng.normal(size=(4,8)).astype('f'));q.create_dataset('fragment',data=rng.normal(size=(4,4,3)).astype('f'))
            original=load_data(path);ablated=load_data(path,'geometry_sequence')
            for key in original:
                a=original[key]['conditions']['f30_center'];b=ablated[key]['conditions']['f30_center']
                self.assertTrue(torch.equal(a['features'][:,8:],b['features'][:,8:]));self.assertEqual(torch.count_nonzero(b['features'][:,:8]),0)
                self.assertTrue(torch.equal(a['coordinates'],b['coordinates']));self.assertTrue(torch.equal(a['keep'],b['keep']));self.assertEqual(torch.count_nonzero(b['features'][~b['keep']]),0)
                if key[0]=='train':self.assertTrue(torch.equal(original[key]['target'],ablated[key]['target']))
            with h5py.File(path,'a') as f:
                for cohort in ('train','development'):f[cohort+'/protein/conditions/f30_center/latent'][:]=123
            changed=load_data(path,'geometry_sequence')
            for key in changed:self.assertTrue(torch.equal(changed[key]['conditions']['f30_center']['features'],ablated[key]['conditions']['f30_center']['features']))
            with self.assertRaises(ValueError):load_data(path,'unknown')


if __name__=='__main__':unittest.main()
