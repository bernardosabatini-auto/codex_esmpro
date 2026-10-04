import unittest
import numpy as np
from audit_inpainting_junctions import junctions


class JunctionTests(unittest.TestCase):
    def setUp(self):
        self.bb=np.zeros((10,4,3));self.bb[:,:,0]=np.arange(10)[:,None]*3.8
        self.bb[:,2,0]+=2.47

    def test_both_edges_of_same_backbone_are_required(self):
        self.assertTrue(junctions(self.bb,3,4)['valid'])
        first=self.bb.copy();first[2,2,0]+=1
        second=self.bb.copy();second[6,2,0]+=1
        self.assertFalse(junctions(first,3,4)['valid'])
        self.assertFalse(junctions(second,3,4)['valid'])

    def test_only_available_junction_at_chain_end(self):
        self.assertEqual(junctions(self.bb,0,4)['edges'],[3])
        self.assertEqual(junctions(self.bb,6,4)['edges'],[5])
        with self.assertRaises(ValueError):junctions(self.bb,0,10)


if __name__=='__main__':unittest.main()
