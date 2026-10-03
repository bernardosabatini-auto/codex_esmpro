import unittest
import numpy as np
from extra_fragment_data import crop_condition


class CropIsolationTests(unittest.TestCase):
    def test_scaffold_coordinates_and_sequence_cannot_change_encoded_crop(self):
        rng=np.random.default_rng(4);bb=rng.normal(size=(40,4,3)).astype(np.float32);sequence='ACDEFGHIKLMNPQRSTVWY'*2;start,letters,fragment,degenerate=crop_condition(bb,sequence)
        other=bb.copy();other[:start]+=1000;other[start+len(fragment):]-=1000
        changed='G'*start+letters+'G'*(len(sequence)-start-len(fragment));result=crop_condition(other,changed)
        self.assertEqual(start,result[0]);self.assertEqual(letters,result[1]);np.testing.assert_array_equal(fragment,result[2]);self.assertEqual(degenerate,result[3])
