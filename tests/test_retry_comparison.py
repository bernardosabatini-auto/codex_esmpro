import unittest
from compare_retry_ensembles import comparisons,gates

class RetryComparisonTests(unittest.TestCase):
    def rows(self):
        return {str(i):dict(target_id=str(i),family=str(i),category='multi' if i<16 else 'control',coverage={'2.0':{'32':.5}} if i<16 else {},coarse_valid_fraction=1.,oracle_nearest_reference_ca_lddt_mean=.8,projection_wasserstein={'32':1.}) for i in range(48)}

    def test_identical_rows_do_not_claim_new_diversity(self):
        r=self.rows();d=comparisons(r,r);self.assertTrue(gates(d)['sampling_quality']);self.assertFalse(gates(d)['training_diversity']);self.assertEqual(d['coverage_at_32']['families'],16)

    def test_coverage_loss_blocks_sampling_quality(self):
        a=self.rows();b=self.rows()
        for i in range(16):a[str(i)]['coverage']['2.0']['32']=0.
        self.assertFalse(gates(comparisons(a,b))['sampling_quality'])

    def test_missing_family_and_changed_category_rejected(self):
        a=self.rows();b=self.rows();del a['47']
        with self.assertRaises(ValueError):comparisons(a,b)
        a=self.rows();a['0']['category']='md'
        with self.assertRaises(ValueError):comparisons(a,b)

if __name__=='__main__':unittest.main()
