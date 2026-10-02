import unittest,json,tempfile
from pathlib import Path
from prepare_overfit import sha
from compare_retry_ensembles import comparisons,gates,validate_source

class RetryComparisonTests(unittest.TestCase):
    def rows(self):
        return {str(i):dict(target_id=str(i),family=str(i),category='multi' if i<16 else 'control',coverage={'2.0':{'32':.5}} if i<16 else {},coarse_valid_fraction=1.,oracle_nearest_reference_ca_lddt_mean=.8,projection_wasserstein={'32':1.}) for i in range(48)}

    def test_identical_rows_do_not_claim_new_diversity(self):
        r=self.rows();d=comparisons(r,r);self.assertTrue(gates(d)['sampling_quality']);self.assertFalse(gates(d)['training_diversity']);self.assertEqual(d['coverage_at_32']['families'],16)

    def test_coverage_loss_blocks_sampling_quality(self):
        a=self.rows();b=self.rows()
        for i in range(16):a[str(i)]['coverage']['2.0']['32']=0.
        self.assertFalse(gates(comparisons(a,b))['sampling_quality'])

    def test_original_reuse_requires_exact_run_protocol_and_native_parent(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);run=root/'old';run.mkdir();(run/'manifest.json').write_text('{}');recipe=root/'previous.json';recipe.write_text('{}')
            c=dict(name='original',protocol_sha256=sha(recipe),native_manifest_sha256='prior',checkpoint='weights',checkpoint_sha256='digest',primary_guidance=2)
            protocol=dict(reused_controls={'original':dict(run=str(run),manifest_sha256=sha(run/'manifest.json'))},reuse_protocol=str(recipe),reuse_protocol_sha256=sha(recipe))
            native=dict(config=dict(prior_retry_manifest_sha256='prior',heads=[dict(name='original',checkpoint='weights',checkpoint_sha256='digest',guidance=2)]))
            validate_source(run,c,recipe,protocol,native)
            with self.assertRaises(ValueError):validate_source(root,c,recipe,protocol,native)
            with self.assertRaises(ValueError):validate_source(run,{**c,'native_manifest_sha256':'other'},recipe,protocol,native)
            with self.assertRaises(ValueError):validate_source(run,{**c,'checkpoint_sha256':'other'},recipe,protocol,native)

    def test_missing_family_and_changed_category_rejected(self):
        a=self.rows();b=self.rows();del a['47']
        with self.assertRaises(ValueError):comparisons(a,b)
        a=self.rows();a['0']['category']='md'
        with self.assertRaises(ValueError):comparisons(a,b)

if __name__=='__main__':unittest.main()
