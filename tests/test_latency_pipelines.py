import unittest
from latentfold.latency import latency_kinds


class PipelineTests(unittest.TestCase):
    def test_existing_rosters_and_isolated_compact_comparator(self):
        self.assertEqual(latency_kinds({}),('student','teacher'))
        self.assertEqual(latency_kinds(dict(candidate_checkpoint='a')),('student','candidate','teacher'))
        c=dict(candidate_checkpoint='a',candidate_compact_condition=True,include_expanded_candidate=True)
        self.assertEqual(latency_kinds(c),('student','expanded_candidate','candidate','teacher'))
        for key in ('candidate_checkpoint','candidate_compact_condition'):
            with self.assertRaises(ValueError):latency_kinds({k:v for k,v in c.items() if k!=key})


if __name__=='__main__':unittest.main()
