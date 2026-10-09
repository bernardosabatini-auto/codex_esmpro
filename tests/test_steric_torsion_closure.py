import json,unittest
from pathlib import Path
import numpy as np
import torch
from latentfold.steric_torsion_closure import StericTorsionClosure,close_steric_torsions
from latentfold.torsion_closure import TorsionClosure


class StericTorsionClosureTests(unittest.TestCase):
    def setUp(self):
        root=Path(__file__).resolve().parents[1]
        self.spec=json.loads((root/'configs/torsion_bridge_closure_protocol.json').read_text())
        self.nb=json.loads((root/'configs/steric_torsion_closure_protocol.json').read_text())['nonbonded']
        self.parent=np.random.default_rng(910).normal(size=(32,4,3))*4

    def test_parent_noop_exact(self):
        x,d=close_steric_torsions(self.parent,self.parent,10,10,self.spec,self.nb)
        np.testing.assert_array_equal(x,self.parent);self.assertEqual(d['closure_calls'],0)

    def test_full_objective_finite_difference(self):
        source=self.parent.copy();source[10:20]+=[.03,.01,-.01]
        p=StericTorsionClosure(source,self.parent,10,10,self.spec,self.nb)
        delta=torch.full((p.count,),.02,dtype=torch.float64,requires_grad=True)
        old=TorsionClosure(source,self.parent,10,10,self.spec).loss(delta)[1]
        new=p.loss(delta)[1]
        for key in old:torch.testing.assert_close(old[key],new[key],rtol=0,atol=0)
        self.assertTrue(torch.autograd.gradcheck(lambda d:p.loss(d)[0],(delta,),atol=1e-4,rtol=1e-4))


if __name__=='__main__':unittest.main()
