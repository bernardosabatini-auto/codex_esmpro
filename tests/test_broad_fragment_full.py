import tempfile,unittest
from pathlib import Path
import h5py,numpy as np
from broad_fragment_full_core import gates,verify_original


class BroadFullDataTests(unittest.TestCase):
    def test_rejections_stay_in_the_frozen_denominator(self):
        fractional=[dict(name=f'f{f}_{p}',motif_ca_rmsd=.2,motif_drms=.2) for f in (20,30,40) for p in ('left','center','right')];short=[dict(name='c20_'+p,motif_ca_rmsd=.2,motif_drms=.2) for p in ('left','center','right')]
        rows=[dict(target_id=str(i),base=i>=1920,qualified=True,conditions=short if i>=1920 else fractional+short) for i in range(2048)]
        self.assertTrue(gates(rows)['data_gate_passed'])
        for r in rows[:193]:r['qualified']=False
        result=gates(rows);self.assertFalse(result['data_gate_passed']);self.assertEqual(result['fractional_roundtrips'],17280);self.assertEqual(result['retained_training_proteins'],1855)
        with self.assertRaises(ValueError):gates(rows[:-1])

    def test_additive_conditions_cannot_change_archived_inputs(self):
        with tempfile.TemporaryDirectory() as temp,h5py.File(Path(temp)/'data.h5','w') as f:
            old=f.create_group('old');old.attrs.update(length=40,family='x');old['reference_z']=np.ones((40,8));old['reference_backbone']=np.ones((40,4,3));q=old.create_group('conditions/f30_center');q.attrs.update(sequence='ACD',start=1);q['latent']=np.ones((3,8));q['fragment']=np.ones((3,4,3));f.copy(old,f,name='new');new=f['new']
            for p in ('left','center','right'):new.create_group('conditions/c20_'+p)
            verify_original(old,new)
            new['conditions/f30_center/latent'][0,0]=2
            with self.assertRaises(ValueError):verify_original(old,new)
