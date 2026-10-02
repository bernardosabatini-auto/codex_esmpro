import hashlib
import unittest
from audit_training_expansion import components,eligible


class ExpansionAuditTests(unittest.TestCase):
    def test_transitive_exclusion_and_occupied_components(self):
        rows={i:dict(id=i,sequence='ACDE',sequence_sha256=hashlib.sha256(b'ACDE').hexdigest(),length=4) for i in 'abcde'}
        groups=components(rows,'a\tb\t0.4\t0.6\t0.2\nb\tc\t0.3\t0.2\t0.5\n')
        self.assertEqual(groups['a'],groups['c'])
        result=eligible(rows,groups,'c\texcluded\t0.3\t0.5\t0.1\n',{'d'})
        self.assertEqual([r['id'] for r in result],['e'])

    def test_below_threshold_and_unknown_queries(self):
        rows={i:dict(id=i,sequence='ACDE',sequence_sha256=hashlib.sha256(b'ACDE').hexdigest(),length=4) for i in 'ab'}
        groups=components(rows,'a\tb\t0.29\t1\t1\n')
        self.assertNotEqual(groups['a'],groups['b'])
        self.assertEqual(len(eligible(rows,groups,'a\tx\t0.9\t0.49\t0.49\n',set())),2)
        with self.assertRaises(ValueError):eligible(rows,groups,'z\tx\t0.9\t1\t1\n',set())


if __name__=='__main__':unittest.main()
