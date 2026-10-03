import unittest
import numpy as np
from latentfold.fragment_codec_batch import pack_backbones


class CodecPackingTests(unittest.TestCase):
    def test_padding_cannot_change_real_coordinates_or_mask(self):
        a=np.arange(60,dtype=np.float32).reshape(5,4,3);b=np.ones((37,4,3),np.float32)
        x,mask,lengths=pack_backbones([dict(backbone=a),dict(backbone=b)],'cpu')
        self.assertEqual(lengths,[5,37]);self.assertEqual(tuple(x.shape),(2,64,4,3))
        np.testing.assert_array_equal(x[0,:5].numpy(),a);np.testing.assert_array_equal(x[1,:37].numpy(),b)
        self.assertEqual(mask.sum(1).tolist(),[5,37]);self.assertTrue((x[~mask]==0).all())

    def test_incomplete_or_nonfinite_source_atoms_are_rejected(self):
        for x in (np.ones((5,3,3)),np.full((5,4,3),np.nan)):
            with self.assertRaises(ValueError):pack_backbones([dict(backbone=x)],'cpu')
        with self.assertRaises(ValueError):pack_backbones([],'cpu')

    def test_exact_length_mode_forbids_padding(self):
        a=dict(backbone=np.ones((5,4,3),np.float32));b=dict(backbone=np.ones((6,4,3),np.float32))
        x,mask,lengths=pack_backbones([a,a],'cpu',length_multiple=1)
        self.assertEqual(tuple(x.shape),(2,5,4,3));self.assertTrue(mask.all())
        with self.assertRaises(ValueError):pack_backbones([a,b],'cpu',length_multiple=1)
