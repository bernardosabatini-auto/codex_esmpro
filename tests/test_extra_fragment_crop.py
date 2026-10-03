import unittest
import numpy as np
from extra_fragment_data import crop_condition


class CropIsolationTests(unittest.TestCase):
    def test_scaffold_coordinates_and_sequence_cannot_change_encoded_crop(self):
        rng=np.random.default_rng(4);bb=rng.normal(size=(40,4,3)).astype(np.float32);sequence='ACDEFGHIKLMNPQRSTVWY'*2
        for length in (None,20):
            start,letters,fragment,degenerate=crop_condition(bb,sequence,length)
            other=bb.copy();other[:start]+=1000;other[start+len(fragment):]-=1000
            changed='G'*start+letters+'G'*(len(sequence)-start-len(fragment));result=crop_condition(other,changed,length)
            self.assertEqual(start,result[0]);self.assertEqual(letters,result[1]);np.testing.assert_array_equal(fragment,result[2]);self.assertEqual(degenerate,result[3])
            if length:self.assertEqual(len(fragment),length)

    def test_invalid_length_is_rejected(self):
        for length in (0,41,20.5):
            with self.assertRaises(ValueError):crop_condition(np.zeros((40,4,3)), 'A'*40,length)
