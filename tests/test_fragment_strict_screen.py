import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import h5py,numpy as np
from prepare_fragment_strict_followup import screen
from prepare_overfit import sha


class StrictScreenTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);root=Path(self.tmp.name);s=dict(arm='test',prefix='development/conditioned')
        for key in ('manifest','report','predictions','fragments'):s[key]=str(root/(key+('.h5' if key in ('predictions','fragments') else '.json')))
        Path(s['manifest']).write_text(json.dumps(dict(status='complete')));s['manifest_sha256']=sha(s['manifest']);Path(s['report']).write_text(json.dumps(dict(status='complete',manifest_sha256=s['manifest_sha256'])))
        with h5py.File(s['predictions'],'w') as pred,h5py.File(s['fragments'],'w') as fr:
            for i in range(16):
                ident=str(i);g=fr.create_group('development/'+ident);g.attrs['family']=ident;q=g.create_group('conditions/f30_center');q.attrs['start']=0;q.attrs['sequence']='AAA';q.create_dataset('fragment',data=np.zeros((3,4,3)))
                bb=np.broadcast_to(np.arange(4)[:,None,None,None],(4,4,4,3));pred.create_dataset(s['prefix']+'/'+ident+'/backbone',data=bb)
        for key in ('report','predictions','fragments'):s[key+'_sha256']=sha(s[key])
        self.c=dict(screens=[s])

    def test_keeps_full_denominator_and_every_joint_raw_match(self):
        def fit(bb,*args):return dict(motif_drms=.2,motif_ca_rmsd=1.5 if bb[0,0,0]==2 else .9)
        with patch('prepare_fragment_strict_followup.backbone_geometry',return_value={'coarse_valid':np.array([True,False,True,True])}),patch('prepare_fragment_strict_followup.motif_fit',side_effect=fit):rows,selected=screen(self.c)
        self.assertEqual(len(rows),64);self.assertEqual(len(selected),32)
        self.assertEqual({k[2] for k in selected},{0,3})
        self.assertEqual(sum(r['raw_gate_passed'] for r in rows),32)

    def test_rejects_changed_archive(self):
        with h5py.File(self.c['screens'][0]['predictions'],'a') as f:f.attrs['changed']=True
        with self.assertRaises(ValueError):screen(self.c)


if __name__=='__main__':unittest.main()
