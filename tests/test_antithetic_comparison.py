import unittest
from compare_antithetic_ensemble import same_model

class SameModelTests(unittest.TestCase):
    def test_only_noise_coupling_may_change(self):
        fields=('checkpoint_sha256','seed','primary_guidance','compact_condition','samples','max_attempts','flow_steps','flow_solver','flow_time_power','panel_sha256','embedding_cache_sha256','decoder_checkpoint_sha256')
        base={k:'fixed' for k in fields};candidate=dict(base,latent_noise_scheme='antithetic');same_model(candidate,base)
        for key in fields:
            with self.assertRaises(ValueError):same_model({**candidate,key:'changed'},base)
        with self.assertRaises(ValueError):same_model(base,base)

if __name__=='__main__':unittest.main()
