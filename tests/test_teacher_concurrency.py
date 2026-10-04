import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import h5py
import numpy as np
from summarize_teacher_concurrency import analyze, decision
from teacher_concurrency_core import sha


class ConcurrentParity(unittest.TestCase):
    def test_speed_cannot_override_numerics_or_bucket_regression(self):
        self.assertTrue(decision(True,.11,[dict(reduction=.11)]))
        self.assertFalse(decision(False,.3,[dict(reduction=.3)]))
        self.assertFalse(decision(True,.09,[dict(reduction=.09)]))
        self.assertFalse(decision(True,.3,[dict(reduction=-.06)]))

    def test_every_full_atom_output_and_private_rng_is_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);ref=root/'ref.h5';manifest=root/'reference.json'
            entries=[dict(bucket=b) for b in (128,256,384,512) for _ in range(2)]
            m=dict(status='complete',config=dict(original=dict(entries=entries),reference_manifest=str(manifest),reference_coordinates=str(ref)),
                records=[],pairs=[],training_updates_executed=0,new_design_attempts=0,elapsed_seconds=100)
            with h5py.File(ref,'w') as f,h5py.File(root/'coordinates.h5','w') as out:
                for i in range(8):
                    f[str(i)+'/full_0']=np.ones((1,8,3))
                    for mode in ('sequential','concurrent'):
                        for repeat in range(4):
                            key=f'{i}/{mode}_{repeat}';out[key]=np.ones((1,8,3))
                            m['records'].append(dict(entry_index=i,mode=mode,repeat=repeat,dataset=key,rng_after=str(i),parameters_unchanged=True,seconds=.5,peak_reserved_bytes=100))
                for pair in range(4):
                    for mode in ('sequential','concurrent'):
                        for repeat in range(4):
                            m['pairs'].append(dict(pair=pair,bucket=entries[2*pair]['bucket'],mode=mode,repeat=repeat,seconds=1 if mode=='concurrent' else 2))
            manifest.write_text(json.dumps(dict(records=[dict(entry_index=i,arm='full',repeat=0,rng_after=str(i)) for i in range(8)])))
            def save():
                m['coordinates_sha256']=sha(root/'coordinates.h5');(root/'manifest.json').write_text(json.dumps(m))
            save()
            with patch('summarize_teacher_concurrency.audit',return_value=dict(max_atom_difference=1e-5)):
                self.assertTrue(analyze(root)['qualified'])
                with h5py.File(root/'coordinates.h5','r+') as f:f['7/concurrent_3'][0,7,2]=2
                save();self.assertFalse(analyze(root)['qualified'])
                with h5py.File(root/'coordinates.h5','r+') as f:f['7/concurrent_3'][0,7,2]=1
                m['records'][0]['rng_after']='changed';save();self.assertFalse(analyze(root)['qualified'])
                m['records'][0]['rng_after']='0';m['records'].pop();save()
                with self.assertRaises(ValueError):analyze(root)


if __name__=='__main__':unittest.main()
