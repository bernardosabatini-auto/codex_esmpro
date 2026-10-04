import unittest
import numpy as np
from context_refresh_frame_core import frame_metrics,frame_gate


class EncoderFramePreflight(unittest.TestCase):
    def test_proper_rotation_can_hide_frame_failure(self):
        ref=np.random.default_rng(5).normal(size=(4,40,4,3))*10
        rotation=np.array([[0,-1,0],[1,0,0],[0,0,1]])
        rows=frame_metrics(ref@rotation+11,ref)
        self.assertTrue(all(r['proper_ca_rmsd']<1e-10 for r in rows))
        self.assertTrue(all(r['centered_ca_rmsd']>1 and not r['frame_pass'] for r in rows))

    def test_rigid_translation_does_not_change_frame(self):
        ref=np.random.default_rng(8).normal(size=(4,40,4,3))*10
        rows=frame_metrics(ref+np.array([11.,-7.,2.]),ref)
        self.assertTrue(all(r['frame_pass'] and r['centered_ca_rmsd']<1e-10 for r in rows))

    def test_gate_counts_each_cohort_and_every_frame(self):
        rows=[dict(arm=a,target_id=str(i),slot=k,reconstruction_pass=True,frame_pass=True)
              for a in ('parent','native_direct') for i in range(4) for k in range(4)]
        self.assertTrue(frame_gate(rows))
        rows[0]['reconstruction_pass']=False;self.assertTrue(frame_gate(rows))
        rows[1]['reconstruction_pass']=False;self.assertFalse(frame_gate(rows))
        rows[1]['reconstruction_pass']=True;rows[-1]['frame_pass']=False;self.assertFalse(frame_gate(rows))
        with self.assertRaises(ValueError):frame_gate(rows[:-1])
        rows[-1]=rows[0]
        with self.assertRaises(ValueError):frame_gate(rows)


if __name__=='__main__':unittest.main()
