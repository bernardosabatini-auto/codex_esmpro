import json,tempfile,unittest
from pathlib import Path
import h5py,numpy as np
from prepare_noise_designability import audit_inputs
from prepare_overfit import sha

class NoiseDesignabilityTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);root=Path(self.temp.name);ids=['a','b','c','d'];self.c=dict(entries=[])
        for key,name in [('generation_manifest','manifest.json'),('protocol','protocol.json'),('predictions','input.h5'),('source_predictions','source.h5'),('reference_predictions','refs.h5')]:self.c[key]=str(root/name)
        Path(self.c['generation_manifest']).write_text(json.dumps(dict(config=dict(target_ids=ids))));Path(self.c['protocol']).write_text('{}')
        with h5py.File(self.c['predictions'],'w') as inp,h5py.File(self.c['source_predictions'],'w') as src,h5py.File(self.c['reference_predictions'],'w') as refs:
            for i,ident in enumerate(ids):
                bb=np.arange(60,dtype=np.float32).reshape(5,4,3)+i;refs.create_dataset(f'references/{ident}/backbone',data=bb)
                for mode in ('real','initial','guided','random'):
                    dataset=f'{mode}/{ident}';inp.create_dataset(dataset,data=bb if mode=='real' else np.stack([bb,bb+1]))
                    for k in ([0] if mode=='real' else range(2)):
                        self.c['entries'].append(dict(mode=mode,target_id=ident,slot=k,dataset=dataset))
                        if mode!='real':src.create_dataset(f'{ident}/{k}/'+('random_selected' if mode=='random' else mode),data=bb+k)
        for key in ('generation_manifest','protocol','predictions','source_predictions','reference_predictions'):self.c[key+'_sha256']=sha(self.c[key])
    def test_complete_assay_and_duplicate_rejected(self):
        audit_inputs(self.c);self.c['entries'][-1]=self.c['entries'][-2].copy()
        with self.assertRaisesRegex(ValueError,'coverage'):audit_inputs(self.c)
    def test_rehashed_input_edit_still_rejected(self):
        with h5py.File(self.c['predictions'],'r+') as f:f['guided/a'][0,0,0,0]+=1
        self.c['predictions_sha256']=sha(self.c['predictions'])
        with self.assertRaisesRegex(ValueError,'backbone changed'):audit_inputs(self.c)

if __name__=='__main__':unittest.main()
