import unittest
import numpy as np
import torch
from latentfold.batching import prediction_batch
from latentfold.online_inputs import sequence_noise_batch,select_trios


class OnlineInputTests(unittest.TestCase):
    def test_noise_and_masks_equal_cached_batch_without_reading_embeddings(self):
        records=[dict(id=name,sequence='A'*n,esm=torch.ones(n,12),z=torch.zeros(n,8),ca=torch.zeros(n,3)) for name,n in [('a',5),('b',9)]]
        requests=[(r,k) for r in records for k in range(3)]
        original=prediction_batch(requests,16,seed=71,decoder_scale=2.)[1:]
        sequences=[(dict(id=r['id'],sequence=r['sequence']),k) for r,k in requests]
        new=sequence_noise_batch(sequences,16,seed=71,decoder_scale=2.)
        for a,b in zip(original,new):torch.testing.assert_close(a,b,rtol=0,atol=0)

    def test_native_free_trio_coverage_and_ties(self):
        xyz=np.random.default_rng(4).normal(size=(20,3))
        choices=select_trios([('a',0),('a',1),('a',2)],[20]*3,np.array([xyz*3,xyz,xyz]))
        self.assertEqual(choices,{'a':1})
        with self.assertRaisesRegex(ValueError,'ordering'):
            select_trios([('a',0),('b',1),('a',2)],[20]*3,np.array([xyz]*3))
        with self.assertRaisesRegex(ValueError,'complete'):
            select_trios([('a',0)],[20],np.array([xyz]))


if __name__=='__main__':unittest.main()
