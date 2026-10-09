import json
import unittest
from pathlib import Path
import numpy as np
import torch
from latentfold.movable_motif_closure import MovableMotifClosure, close_movable_motif, rotation
from latentfold.torsion_closure import TorsionClosure


class MovableMotifTests(unittest.TestCase):
    def setUp(self):
        self.spec = json.loads((Path(__file__).resolve().parents[1] / 'configs/torsion_bridge_closure_protocol.json').read_text())
        self.parent = np.random.default_rng(6431).normal(size=(32,4,3)) * 4
        self.source = self.parent.copy()
        self.source[10:20] += [.03, .01, -.01]
        self.problem = MovableMotifClosure(self.source, self.parent, 10, 10, self.spec)

    def test_rotation_and_rigid_motif_and_far_scaffold(self):
        for vector in ([0.,0.,0.], [.2,-.4,.7]):
            r = rotation(torch.tensor(vector, dtype=torch.float64))
            torch.testing.assert_close(r.T @ r, torch.eye(3,dtype=torch.float64), atol=1e-14, rtol=0)
            self.assertAlmostEqual(float(torch.linalg.det(r)), 1., places=14)
        pose = torch.tensor([.2,-.4,.7,1.,-2.,3.], dtype=torch.float64)
        result, _ = self.problem.assemble(torch.full((self.problem.count,),.03,dtype=torch.float64), pose)
        a, b = result[10:20].reshape(-1,3), self.problem.motif.reshape(-1,3)
        torch.testing.assert_close(torch.cdist(a,a), torch.cdist(b,b), atol=3e-7, rtol=0)
        self.assertTrue(torch.equal(result[:2], self.problem.source[:2]))
        self.assertTrue(torch.equal(result[28:], self.problem.source[28:]))

    def test_zero_pose_matches_original_kinematics_and_common_terms(self):
        delta = torch.full((self.problem.count,),.03,dtype=torch.float64)
        pose = torch.zeros(6,dtype=torch.float64)
        old = TorsionClosure(self.source,self.parent,10,10,self.spec)
        for a,b in zip(self.problem.assemble(delta,pose),old.assemble(delta)):
            torch.testing.assert_close(a,b,atol=1e-12,rtol=0)
        for k,v in old.loss(delta)[1].items():
            torch.testing.assert_close(v,self.problem.loss(delta,pose)[1][k],atol=1e-9,rtol=1e-12)
        pairs = self.problem.pairs.numpy() // 4
        self.assertFalse(np.any(((pairs>=10)&(pairs<20)).all(axis=1)))

    def test_finite_difference_at_zero_and_nonzero_pose(self):
        delta = torch.full((self.problem.count,),.02,dtype=torch.float64,requires_grad=True)
        for values in ([0.]*6,[.01,-.02,.03,.04,-.03,.02]):
            pose = torch.tensor(values,dtype=torch.float64,requires_grad=True)
            self.assertTrue(torch.autograd.gradcheck(lambda d,p:self.problem.loss(d,p)[0],
                            (delta,pose),atol=1e-3,rtol=1e-4))

    def test_exact_parent_noop_in_both_arms(self):
        for free in (False,True):
            x,s = close_movable_motif(self.parent,self.parent,10,10,self.spec,free_pose=free)
            np.testing.assert_array_equal(x,self.parent)
            self.assertEqual(s['closure_calls'],0)
            self.assertEqual(s['pose'],[0.]*6)


if __name__ == '__main__': unittest.main()
