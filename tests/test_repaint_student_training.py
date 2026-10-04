import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import h5py
import numpy as np
import torch
from repaint_student_training_core import check_draws,DRAW_KEYS,load_pairs


class RepaintStudentTests(unittest.TestCase):
    def test_only_endpoint_hash_may_differ(self):
        a=[dict.fromkeys(DRAW_KEYS,1)];b=copy.deepcopy(a)
        a[0]['positive_sha256']='native';b[0]['positive_sha256']='generated'
        check_draws(a,b)
        for key in DRAW_KEYS:
            changed=copy.deepcopy(b);changed[0][key]=2
            with self.assertRaises(ValueError):check_draws(a,changed)

    def test_endpoint_changes_do_not_change_isolated_conditioning(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);labels=root/'labels.h5';fr=root/'fr.h5';gen=root/'gen.h5'
            rng=np.random.default_rng(1);native=rng.standard_normal((24,8)).astype('f4');teacher=rng.standard_normal((24,8)).astype('f4')
            latent=rng.standard_normal((20,8)).astype('f4');fragment=rng.standard_normal((20,4,3)).astype('f4')
            with h5py.File(fr,'w') as f:
                g=f.create_group('train/protein');g['reference_z']=native;q=g.create_group('conditions/c20_center')
                q['latent']=latent;q['fragment']=fragment;q.attrs.update(sequence='A'*20,start=2)
            with h5py.File(gen,'w') as f:f['new/protein/latent']=teacher[None]
            with h5py.File(labels,'w') as f:
                g=f.create_group('label_00');g['native_matched']=native;g['repaint_positive']=teacher
                g['fragment_latent']=latent;g['fragment']=fragment;g.attrs.update(sequence='A'*20,start=2,length=24,target_id='protein')
            c=dict(fragments=str(fr),training_ids=['label_00'],arm='native_matched')
            spec=dict(condition='c20_center');ls=dict(labels=str(labels),teacher_predictions=str(gen),rows=[dict(label_id='label_00',target_id='protein',length=24,bucket=128,generation_slot=0)])
            a=load_pairs(c,audited=(spec,ls));b=load_pairs(dict(c,arm='repaint_positive'),audited=(spec,ls))
            self.assertFalse(torch.equal(a['label_00']['positive'],b['label_00']['positive']))
            for key in ('features','keep','coordinates'):self.assertTrue(torch.equal(a['label_00'][key],b['label_00'][key]))
            with h5py.File(labels,'r+') as f:f['label_00/fragment_latent'][0,0]+=1
            with self.assertRaises(ValueError):load_pairs(c,audited=(spec,ls))

    def test_watcher_hook_uses_only_stdlib_on_import(self):
        scripts=Path(__file__).resolve().parents[1]/'scripts'
        subprocess.run([sys.executable,'-I','-S','-c',f'import sys;sys.path.insert(0,{str(scripts)!r});import compare_repaint_student_training'],check=True,capture_output=True)

    def test_ready_command_rejects_unregistered_jobs(self):
        from compare_repaint_student_training import ready_command
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'runs').mkdir();(root/'reports').mkdir()
            (root/'runs/repaint_student_training_profiles.json').write_text(json.dumps(dict(jobs=['1','2'])))
            (root/'runs/jobs.json').write_text(json.dumps(dict(jobs=[])))
            with self.assertRaises(ValueError):ready_command(root)


if __name__=='__main__':unittest.main()
