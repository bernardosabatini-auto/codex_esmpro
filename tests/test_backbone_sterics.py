import unittest
import numpy as np
import torch
from latentfold.backbone_sterics import nonbonded_pairs,steric_audit,steric_loss


class BackboneStericsTests(unittest.TestCase):
    def test_covalent_exclusion_is_graph_based_and_pairs_unique(self):
        pairs=nonbonded_pairs(6,[2]);actual=set(map(tuple,pairs.tolist()))
        self.assertEqual(len(actual),len(pairs))
        # N2→CA2→C2→N3→CA3 is four bonds; retain despite adjacent residues.
        self.assertIn((8,13),actual)
        # N2→CA2→C2→N3 is three bonds; exclude.
        self.assertNotIn((8,12),actual)
        self.assertNotIn((8,11),actual)
        self.assertTrue(all(a in range(8,12) or b in range(8,12) for a,b in actual))

    def test_overlapping_editable_pairs_are_not_double_counted(self):
        a=set(map(tuple,nonbonded_pairs(7,[2])));b=set(map(tuple,nonbonded_pairs(7,[3])))
        both=nonbonded_pairs(7,[2,3]);self.assertEqual(set(map(tuple,both)),a|b);self.assertEqual(len(both),len(a|b))

    def test_finite_difference_and_repulsive_gradient(self):
        x=torch.tensor([[[0.,0.,0.],[.8,0.,0.],[0.,3.,0.],[0.,0.,3.]]],dtype=torch.float64,requires_grad=True)
        pairs=torch.tensor([[0,1],[1,2]]);cutoffs=torch.tensor([2.5,2.5],dtype=torch.float64)
        fun=lambda a:steric_loss(a,pairs,cutoffs,scale=.25,editable_atoms=4)
        self.assertTrue(torch.autograd.gradcheck(fun,(x,),atol=1e-6,rtol=1e-5))
        gradient=torch.autograd.grad(fun(x),x)[0];moved=x-.001*gradient
        self.assertGreater(float((moved[0,0]-moved[0,1]).norm().detach()),.8)

    def test_audit_translation_rotation_invariant(self):
        x=np.random.default_rng(51).normal(size=(8,4,3))*4;q,_=np.linalg.qr(np.random.default_rng(9).normal(size=(3,3)))
        a=steric_audit(x,[2,3]);b=steric_audit(x@q+11,[2,3])
        self.assertEqual(a['pairs_below_threshold'],b['pairs_below_threshold'])
        self.assertAlmostEqual(a['minimum_distance'],b['minimum_distance'],places=12)


if __name__=='__main__':unittest.main()
