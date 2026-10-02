import copy,unittest
from unittest.mock import patch
from summarize_retry_prefix import analyze

class RetryPrefixTests(unittest.TestCase):
    def fixture(self):
        ids=[str(i) for i in range(8)];c=dict(target_ids=ids)
        for key in ('protocol','failed_manifest','ensemble_manifest','reference','panel','checkpoint','embedding_cache','decoder_checkpoint'):c[key]='fixture';c[key+'_sha256']='s'
        rows=[]
        for ident in ids:
            for kind in ('cached_vs_reference','online_vs_reference','online_vs_cached','cached_prefix_vs32','online_prefix_vs32'):
                for count in ((1,8) if 'prefix' in kind else (1,8,32)):
                    rows.append(dict(target_id=ident,kind=kind,count=count,checks=[dict(slot=k,selected_draw=k,reference_draw=k,validity_identical=True,ca_rmsd=0.,ca_lddt=1.) for k in range(count)]))
        return dict(status='complete',config=c,comparisons=rows,embeddings=[])
    @patch('summarize_retry_prefix.sha',return_value='s')
    def test_late_failing_sample_is_retained_in_report(self,_):
        m=self.fixture();row=next(r for r in m['comparisons'] if (r['target_id'],r['kind'],r['count'])==('6','online_vs_reference',32));row['checks'][31]['ca_rmsd']=.21;r=analyze(m)
        self.assertFalse(r['all_controls_passed']);self.assertEqual(len(r['failures']),1);self.assertEqual(r['failures'][0]['slot'],31)
    @patch('summarize_retry_prefix.sha',return_value='s')
    def test_missing_or_duplicate_control_is_rejected(self,_):
        m=self.fixture();self.assertTrue(analyze(m)['all_controls_passed']);bad=copy.deepcopy(m);bad['comparisons'][-1]=bad['comparisons'][0]
        with self.assertRaises(ValueError):analyze(bad)
        m['comparisons'][-1]['checks'].pop()
        with self.assertRaises(ValueError):analyze(m)

if __name__=='__main__':unittest.main()
