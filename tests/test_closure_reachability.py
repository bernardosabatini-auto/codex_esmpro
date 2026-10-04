import unittest
import numpy as np
from closure_reachability import bounds,chain_bound


class ReachabilityTests(unittest.TestCase):
    def test_reference_paths_never_excluded(self):
        rng=np.random.default_rng(92)
        for _ in range(30):
            parent=rng.normal(size=(32,4,3))*10
            rr=bounds(parent,parent,10,8,4)
            self.assertEqual(len(rr),2)
            self.assertFalse(any(r['impossible'] for r in rr))

    def test_far_motif_is_impossible_and_bound_is_pose_invariant(self):
        rng=np.random.default_rng(22);parent=rng.normal(size=(32,4,3));source=parent.copy();source[10:18]+=100
        rotation,_=np.linalg.qr(rng.normal(size=(3,3)));rotation[:,0]*=np.linalg.det(rotation)
        a=bounds(source,parent,10,8);b=bounds(source@rotation+11,parent@rotation+11,10,8)
        self.assertTrue(all(r['impossible'] for r in a))
        for x,y in zip(a,b):
            for key in ('required_distance','upper_bound'):self.assertAlmostEqual(x[key],y[key],places=10)

    def test_free_ended_flank_has_no_anchor_distance_bound(self):
        parent=np.random.default_rng(9).normal(size=(32,4,3))
        self.assertEqual([r['side'] for r in bounds(parent,parent,0,20)],['right'])
        self.assertEqual([r['side'] for r in bounds(parent,parent,12,20)],['left'])

    def test_two_bond_bound_is_analytic(self):
        self.assertAlmostEqual(chain_bound(np.array([1.,1.]),np.array([np.pi/2])),
                               np.sqrt(2*1.05**2-2*1.05**2*np.cos(np.radians(100))))


if __name__=='__main__':unittest.main()
