import itertools,unittest
import torch
from latentfold.conditional_coupling import couple_targets

class ConditionalCouplingTests(unittest.TestCase):
    def test_exact_assignment_matches_brute_force_and_preserves_targets(self):
        g=torch.Generator().manual_seed(13);x=torch.randn(4,3,8,generator=g);z=torch.randn(4,3,8,generator=g);mask=torch.ones(4,3,dtype=torch.bool)
        actual,info=couple_targets(x,z,mask,['p']*4,group_size=4,arm='optimal')
        brute=min(float((x-z[list(p)]).square().mean()) for p in itertools.permutations(range(4)))
        self.assertAlmostEqual(float((x-actual).square().mean()),brute,places=6)
        self.assertEqual(sorted(info['permutation']),list(range(4)));self.assertTrue(torch.equal(actual,z[info['permutation']]))
        plain,_=couple_targets(x,z,mask,['p']*4,group_size=4,arm='independent');self.assertTrue(torch.equal(plain,z))
    def test_conditions_never_exchange_labels_and_padding_cannot_choose_match(self):
        g=torch.Generator().manual_seed(17);x=torch.randn(8,4,8,generator=g);z=torch.randn(8,4,8,generator=g);mask=torch.ones(8,4,dtype=torch.bool);mask[:,3]=False;ids=['a']*4+['b']*4
        _,left=couple_targets(x,z,mask,ids,group_size=4,arm='optimal');x[:,3]*=1000;z[:,3]*=-1000;_,right=couple_targets(x,z,mask,ids,group_size=4,arm='optimal')
        self.assertEqual(left,right);self.assertEqual(sorted(left['permutation'][:4]),list(range(4)));self.assertEqual(sorted(left['permutation'][4:]),list(range(4,8)))
        with self.assertRaises(ValueError):couple_targets(x,z,mask,['a','b']*4,group_size=4,arm='optimal')
    def test_invalid_values_and_masks_rejected(self):
        x=torch.zeros(4,2,8);z=x.clone();mask=torch.ones(4,2,dtype=torch.bool);mask[0,1]=False
        with self.assertRaises(ValueError):couple_targets(x,z,mask,['p']*4,group_size=4,arm='optimal')
        mask[:]=True;x[0,0,0]=float('nan')
        with self.assertRaises(ValueError):couple_targets(x,z,mask,['p']*4,group_size=4,arm='optimal')

if __name__=='__main__':unittest.main()
