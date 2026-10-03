import unittest
import numpy as np
from decoder_fragment_variance_core import variance_components,motif_distances


class DecoderVarianceTests(unittest.TestCase):
    def test_constant_wrong_decoder_has_systematic_error(self):
        x=np.full((4,5,190),2.);r=variance_components(x,np.zeros(190))
        self.assertEqual(r['systematic_distance_error'],4.)
        self.assertEqual(r['within_latent_decoder_variance'],0.)
        self.assertEqual(r['decoder_fraction_of_error'],0.)

    def test_pure_decoder_variation_and_crossed_identity(self):
        x=np.broadcast_to(np.arange(5)[None,:,None]-2,(4,5,190));r=variance_components(x,np.zeros(190))
        self.assertEqual(r['systematic_distance_error'],0.)
        self.assertEqual(r['decoder_fraction_of_error'],1.)
        x=np.random.default_rng(4).normal(size=(4,5,190));r=variance_components(x,np.ones(190))
        self.assertAlmostEqual(r['mean_squared_distance_error'],r['systematic_distance_error']+r['within_latent_decoder_variance'])
        self.assertAlmostEqual(r['total_variance'],r['between_latent_variance']+r['within_latent_decoder_variance'])

    def test_distances_ignore_global_pose(self):
        b=np.random.default_rng(5).normal(size=(4,5,23,4,3));rotation=np.array([[0,-1,0],[1,0,0],[0,0,1]])
        np.testing.assert_allclose(motif_distances(b,2),motif_distances(b@rotation+7,2),atol=1e-12)
        self.assertEqual(motif_distances(b,2).shape,(4,5,190))


if __name__=='__main__':unittest.main()
