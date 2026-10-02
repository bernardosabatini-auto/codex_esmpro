import unittest,tempfile,sys
from pathlib import Path
import h5py,numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from compare_trained_fragment_designability import matched_fragment_inputs


class AssayInputTests(unittest.TestCase):
    def test_training_corpus_changes_but_fragment_must_not(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths=[Path(tmp)/x for x in ['a.h5','b.h5']]
            for i,path in enumerate(paths):
                with h5py.File(path,'w') as f:
                    f.create_dataset('train/different',data=np.arange(i+1));g=f.create_group('development/p/conditions/f30_center');g.attrs['sequence']='ACD';g.attrs['start']=3;g.create_dataset('fragment',data=np.zeros((3,4,3)));g.create_dataset('latent',data=np.zeros((3,8)))
            matched_fragment_inputs(paths,['p'])
            with h5py.File(paths[1],'a') as f:f['development/p/conditions/f30_center'].attrs['sequence']='ACE'
            with self.assertRaises(ValueError):matched_fragment_inputs(paths,['p'])
            with h5py.File(paths[1],'a') as f:
                g=f['development/p/conditions/f30_center'];g.attrs['sequence']='ACD';g['latent'][0,0]=1
            with self.assertRaises(ValueError):matched_fragment_inputs(paths,['p'])


if __name__=='__main__':unittest.main()
