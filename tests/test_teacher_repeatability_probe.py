import itertools
import unittest
from summarize_teacher_repeatability_probe import analyze


def fixture():
    metric=dict(ca_rmsd=.002,ca_lddt=1.)
    return dict(status='complete', design_attempts=0, strict_probe={}, scope='diagnostic',
                records=[dict(index=i,features_before={'x':'a'},features_after={'x':'a'},
                              rng_before_features=['cpu','gpu'],rng_after_features=['cpu','gpu'],
                              original_comparison=dict(metric)) for i in range(6)],
                comparisons=[dict(left=i,right=j,**metric) for i,j in itertools.combinations(range(6),2)])


class ReplayTests(unittest.TestCase):
    def test_failure_preserved(self):
        m=fixture();m['comparisons'][7]['ca_rmsd']=.0107
        d=analyze(m)
        self.assertEqual(len(d['failed_pairs']),1)
        self.assertEqual(d['max_pair_ca_rmsd'],.0107)
        self.assertEqual(len(d['comparisons']),15)

    def test_mutation_and_rng(self):
        m=fixture();m['records'][2]['features_after']['x']='b';m['records'][3]['rng_after_features'][1]='changed'
        d=analyze(m)
        self.assertEqual(d['feature_mutations'],[2])
        self.assertEqual(d['feature_rng_changes'],[3])

    def test_missing_pair_rejected(self):
        m=fixture();m['comparisons'].pop()
        with self.assertRaises(ValueError):analyze(m)


if __name__=='__main__':unittest.main()
