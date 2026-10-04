import json
from pathlib import Path
import unittest
import numpy as np
import torch
from latentfold.local_closure import ClosureProblem, close_backbone, geometry_audit, topology


class LocalClosure(unittest.TestCase):
    def setUp(self):
        self.spec=json.loads((Path(__file__).resolve().parents[1]/'configs/fragment_local_closure_feasibility.json').read_text())
        self.parent=np.random.default_rng(31).normal(size=(12,4,3))*10
        self.start=4;self.length=4

    def test_graph_includes_both_outer_boundaries_and_excludes_fixed_only_constraints(self):
        g=topology(16,6,4,2);editable=set(g['editable'].tolist())
        self.assertEqual(g['residues'],[4,5,10,11])
        bonds=set(map(tuple,g['bonds'].tolist()))
        self.assertTrue({(14,16),(22,24),(38,40),(46,48)}<=bonds)
        self.assertNotIn((24,25),bonds)
        for key in ('bonds','angles','torsions'):
            self.assertTrue(all(editable.intersection(row) for row in g[key].tolist()))

    def test_noop_and_numpy_geometry_agree(self):
        out,record=close_backbone(self.parent,self.parent,self.start,self.length,self.spec)
        np.testing.assert_array_equal(out,self.parent)
        self.assertEqual(record['final_loss'],0)
        d=geometry_audit(out,self.parent,self.start,self.length)
        self.assertTrue(d['valid']);self.assertEqual(d['max_torsion_delta'],0)

    def test_true_finite_difference_gradient(self):
        problem=ClosureProblem(self.parent,self.parent,self.start,self.length,self.spec)
        x=problem.source[problem.graph['editable']].clone()+.01*torch.randn(len(problem.graph['editable']),3,dtype=torch.float64)
        self.assertTrue(torch.autograd.gradcheck(lambda y:problem.loss(y)[0],(x.requires_grad_(),),atol=1e-5,rtol=1e-4))

    def test_optimizer_reduces_error_without_moving_fixed_atoms(self):
        source=self.parent.copy();g=topology(12,self.start,self.length,4)
        source[g['residues']]+=.05*np.random.default_rng(11).normal(size=(len(g['residues']),4,3))
        out,record=close_backbone(source,self.parent,self.start,self.length,self.spec)
        np.testing.assert_array_equal(out[self.start:self.start+self.length],source[self.start:self.start+self.length])
        self.assertLess(record['final_loss'],record['initial_loss']*.01)
        self.assertTrue(geometry_audit(out,self.parent,self.start,self.length)['valid'])

    def test_proper_pose_equivariance(self):
        source=self.parent.copy();source[3]+=.01
        rotation=np.array([[0,-1,0],[1,0,0],[0,0,1]],dtype=np.float64);offset=np.array([11,13,-9])
        a,_=close_backbone(source,self.parent,self.start,self.length,self.spec)
        b,_=close_backbone(source@rotation+offset,self.parent@rotation+offset,self.start,self.length,self.spec)
        np.testing.assert_allclose(a@rotation+offset,b,atol=.005,rtol=0)

    def test_deadline_is_enforced(self):
        with self.assertRaises(TimeoutError):close_backbone(self.parent,self.parent,self.start,self.length,self.spec,deadline=0)


if __name__=='__main__':unittest.main()
