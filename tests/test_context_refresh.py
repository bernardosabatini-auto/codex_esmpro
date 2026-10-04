import unittest
import torch
from context_refresh_core import starting_state,refresh_rounds


class ContextRefresh(unittest.TestCase):
    def test_start_is_only_translated_and_anchors_are_copied(self):
        torch.manual_seed(8);bb=torch.randn(4,30,4,3)*10;keep=torch.zeros(4,30,dtype=torch.bool);keep[:,5:25]=True
        current,anchors=starting_state(bb,keep)
        torch.testing.assert_close(current-bb,-bb.mean((1,2),keepdim=True).expand_as(bb),rtol=0,atol=2e-6)
        self.assertTrue(torch.equal(anchors[keep],current[keep]));self.assertTrue((anchors[~keep]==0).all())
        self.assertLess(float(current.mean((1,2)).abs().max()),1e-6)

    def test_every_round_encodes_previous_full_output(self):
        initial=torch.zeros(4,30,4,3);seen=[]
        def encode(bb):seen.append(bb.clone());return bb+2
        def decode(z):return z+3
        rows=list(refresh_rounds(initial,encode,decode))
        self.assertEqual(len(rows),3)
        for k,(index,bb,z,out) in enumerate(rows):
            self.assertEqual(index,k+1);self.assertTrue(torch.equal(bb,seen[k]));self.assertTrue((bb==5*k).all())
            self.assertTrue((out==5*(k+1)).all())
        self.assertTrue((initial==0).all())
        with self.assertRaises(ValueError):list(refresh_rounds(initial,encode,decode,rounds=4))

    def test_nonfinite_feedback_stops(self):
        with self.assertRaises(ValueError):list(refresh_rounds(torch.zeros(4,30,4,3),lambda x:x,lambda x:x*float('nan')))


if __name__=='__main__':unittest.main()
