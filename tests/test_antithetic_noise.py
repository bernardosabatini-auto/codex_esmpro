import unittest
import torch
from antithetic_noise import noise_address,native_scheme,raw_identity_samples
from latentfold.flow import target_noise

class AntitheticTests(unittest.TestCase):
    def test_exact_sign_pairs_and_independent_decoder_addressing(self):
        values=[]
        for logical in range(8):
            index,sign=noise_address(logical,'antithetic');values.append(sign*target_noise(['test'],[7],8,seed=123,sample_index=index,device='cpu'))
        for i in range(0,8,2):self.assertTrue(torch.equal(values[i],-values[i+1]))
        self.assertTrue(torch.equal(values[2],target_noise(['test'],[7],8,seed=123,sample_index=1,device='cpu')))
        self.assertEqual(noise_address(5),(5,1))

    def test_unrecognized_or_negative_addresses_rejected(self):
        for index,scheme in [(-1,'iid'),(1.5,'antithetic'),(True,'iid'),(0,'unknown')]:
            with self.assertRaises(ValueError):noise_address(index,scheme)

    def test_only_declared_head_has_changed_identity_expectation(self):
        protocol=dict(antithetic_head='paired');head=dict(name='paired',latent_noise_scheme='antithetic')
        self.assertEqual(raw_identity_samples(head,protocol),(0,));self.assertEqual(raw_identity_samples(dict(name='original'),protocol),(0,1,2))
        with self.assertRaises(ValueError):native_scheme(dict(name='original',latent_noise_scheme='antithetic'),protocol)

if __name__=='__main__':unittest.main()
