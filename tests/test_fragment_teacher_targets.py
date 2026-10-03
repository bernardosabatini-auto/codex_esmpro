import unittest
import numpy as np
from audit_fragment_teacher_targets import proper_rmsd_batch
from latentfold.metrics import ca_metrics


class TeacherFragmentFitTests(unittest.TestCase):
    def test_rotation_translation_and_reflection_match_proper_metric(self):
        rng=np.random.default_rng(8);reference=rng.normal(size=(12,3));rotation,_=np.linalg.qr(rng.normal(size=(3,3)));rotation[:,0]*=np.linalg.det(rotation)
        mobile=np.stack([reference@rotation+5,reference*np.array([-1,1,1]),reference+rng.normal(size=reference.shape)*.1])
        result=proper_rmsd_batch(mobile,reference)
        np.testing.assert_allclose(result,[ca_metrics(x,reference)['ca_rmsd'] for x in mobile],atol=1e-10)
        self.assertLess(result[0],1e-10);self.assertGreater(result[1],.1)
