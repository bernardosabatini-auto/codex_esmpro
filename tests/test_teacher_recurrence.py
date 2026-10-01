import sys
from pathlib import Path
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from evaluate_teacher_recurrence import seed_for,compare_backbones


class RecurrenceTests(unittest.TestCase):
    def test_stream_seeds_are_stable_and_distinct(self):
        a=[seed_for(73,'target',s) for s in ['new_trunk','diffusion:0','diffusion:16']]
        self.assertEqual(a[1],seed_for(73,'target','diffusion:0'))
        self.assertEqual(len(set(a)),3)
        self.assertNotEqual(a[1],seed_for(73,'other','diffusion:0'))

    def test_reproduction_accepts_pose_but_rejects_structure_changes(self):
        bb=np.random.default_rng(4).normal(size=(2,24,4,3))*4
        rotation=np.array([[0,-1,0],[1,0,0],[0,0,1]])
        result=compare_backbones(bb,bb@rotation+13)
        self.assertLess(result['max_ca_rmsd'],1e-10)
        changed=bb.copy();changed[0,0,1]+=2
        with self.assertRaises(ValueError):compare_backbones(bb,changed)


if __name__=='__main__':unittest.main()
