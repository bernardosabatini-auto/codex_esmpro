import copy,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import h5py,numpy as np
from teacher_staging_replication import audit_result


class StagingReplayTests(unittest.TestCase):
    def test_sequence_coordinate_and_success_changes_cannot_pass(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);run=root/'new';run.mkdir();old=root/'old.h5'
            names=[str(i) for i in range(32)]
            for path in (old,run/'refolded.h5'):
                with h5py.File(path,'w') as f:
                    for name in names:
                        for i in range(8):f[name+'/'+str(i)]=np.zeros((2,4,3),np.float32)
            rows=[dict(name=n,raw_gate_passed=True,scaffold_joint_success=True,valid_designable=True,complete_strict=True,
                       complete_connected_designable=True,scaffold_successful_refold_indices=[0],complete_strict_indices=[0]) for n in names]
            d=dict(records=rows);rd=copy.deepcopy(d)
            c=dict(entries=[dict(name=n) for n in names],teacher_staging_validation=dict(reference_refolded=str(old)))
            m=dict(config=c,sequences={n:['AA']*8 for n in names},records=[dict(name=n,sequence_index=i) for n in names for i in range(8)],
                   cpu_preflight_file_identity_unchanged=True,elapsed_seconds=1.,mpnn_seconds=1.,teacher_staging_seconds=1.,teacher_load_seconds=1.)
            rm=copy.deepcopy(m)
            with patch('teacher_staging_replication.validate',return_value=(rm,rd)):
                self.assertTrue(audit_result(run,m,d)['qualified'])
                m['sequences']['0'][0]='AC'
                with self.assertRaises(ValueError):audit_result(run,m,d)
                m['sequences']=copy.deepcopy(rm['sequences']);d['records'][0]['scaffold_joint_success']=False
                self.assertFalse(audit_result(run,m,d)['qualified']);d=copy.deepcopy(rd)
                with h5py.File(run/'refolded.h5','r+') as f:f['0/0'][0,0,0]=.001
                self.assertFalse(audit_result(run,m,d)['qualified'])


if __name__=='__main__':unittest.main()
