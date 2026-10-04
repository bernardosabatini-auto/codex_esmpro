import json,time,unittest
from pathlib import Path
import numpy as np
import torch
from latentfold.torsion_closure import TorsionClosure,close_torsions


class TorsionClosureTests(unittest.TestCase):
    def setUp(self):
        self.spec=json.loads((Path(__file__).resolve().parents[1]/'configs/torsion_bridge_closure_protocol.json').read_text())
        self.parent=np.random.default_rng(719).normal(size=(32,4,3))*3
        self.source=self.parent.copy();self.source[10:20]+=[.02,-.01,.03]

    def test_exact_noop(self):
        result,stats=close_torsions(self.parent,self.parent,10,10,self.spec)
        np.testing.assert_array_equal(result,self.parent)
        self.assertEqual(stats['closure_calls'],0);self.assertTrue(stats['exact_noop'])

    def test_objective_gradient_and_endpoint_are_differentiable(self):
        problem=TorsionClosure(self.source,self.parent,10,10,self.spec)
        delta=torch.full((problem.count,),.01,dtype=torch.float64,requires_grad=True)
        self.assertTrue(torch.autograd.gradcheck(lambda x:problem.loss(x)[0],(delta,),atol=1e-4,rtol=1e-4))

    def test_reduces_endpoint_error_preserves_fixed_atoms_and_repeats(self):
        result,stats=close_torsions(self.source,self.parent,10,10,self.spec)
        self.assertLess(stats['final_loss'],stats['initial_loss']*.05)
        np.testing.assert_array_equal(result[np.r_[0:2,10:20,28:32]],self.source[np.r_[0:2,10:20,28:32]])
        again,_=close_torsions(self.source,self.parent,10,10,self.spec)
        np.testing.assert_array_equal(result,again)

    def test_optimized_proper_pose_control(self):
        q,_=np.linalg.qr(np.random.default_rng(731).normal(size=(3,3)));q[:,0]*=np.linalg.det(q)
        result,_=close_torsions(self.source,self.parent,10,10,self.spec)
        moved,_=close_torsions(self.source@q+11,self.parent@q+11,10,10,self.spec)
        np.testing.assert_allclose(moved,result@q+11,atol=.005,rtol=0)

    def test_deadline(self):
        with self.assertRaises(TimeoutError):close_torsions(self.source,self.parent,10,10,self.spec,deadline=time.monotonic()-1)


if __name__=='__main__':unittest.main()
