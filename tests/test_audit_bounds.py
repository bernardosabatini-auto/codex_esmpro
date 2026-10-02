import itertools,unittest
import numpy as np
from latentfold.audit_bounds import teacher_priors,worst_failure_mass


class BoundTests(unittest.TestCase):
    def test_worst_bound_is_attained_and_covers_all_assignments(self):
        weights=np.array([0,.05,.15,.3,.5])
        for count in range(6):
            actual=[weights[list(indices)].sum() for indices in itertools.combinations(range(5),count)]
            self.assertAlmostEqual(worst_failure_mass(weights,count),max(actual))

    def test_balanced_weights_exclude_invalid_source_labels(self):
        p=teacher_priors(dict(teacher_indices=[0,2,3],clusters=[0,1,1],states=2),4)
        np.testing.assert_allclose(p['balanced'],[.5,0,.25,.25]);np.testing.assert_allclose(p['empirical'],[1/3,0,1/3,1/3])
        self.assertEqual(worst_failure_mass(p['balanced'],1),.5)

    def test_invalid_evidence_rejected(self):
        for weights,n in (([.2,.2],1),([1.,0],3),([1.,0],-1),([float('nan'),0],1)):
            with self.assertRaises(ValueError):worst_failure_mass(weights,n)
        with self.assertRaises(ValueError):teacher_priors(dict(teacher_indices=[0,0],clusters=[0,1],states=2))


if __name__=='__main__':unittest.main()
