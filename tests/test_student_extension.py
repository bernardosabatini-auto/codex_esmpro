import unittest
from summarize_student_extension import hit_summary,validate_batches


class ExtensionTests(unittest.TestCase):
    def test_timing_requires_every_chunk_once(self):
        rows=[dict(target_id=i,offset=k,seconds=1.,peak_reserved_bytes=1024) for i in ('a','b') for k in (0,32,64,96)]
        validate_batches(rows,['a','b'])
        with self.assertRaises(ValueError):validate_batches(rows[:-1],['a','b'])
        rows[-1]=rows[0]
        with self.assertRaises(ValueError):validate_batches(rows,['a','b'])
    def test_new_state_first_hit_and_prefix_are_distinct(self):
        assignments=[None]*128;assignments[7]=0;assignments[99]=2
        coverage,first=hit_summary(assignments,[0,2])
        self.assertEqual(coverage['4'],0);self.assertEqual(coverage['32'],.5);self.assertEqual(coverage['128'],1.)
        self.assertEqual(first,{'0':8,'2':100})
        assignments[99]=None
        coverage,first=hit_summary(assignments,[0,2]);self.assertEqual(coverage['128'],.5);self.assertIsNone(first['2'])

    def test_invalid_states_and_incomplete_prefix_fail(self):
        with self.assertRaises(ValueError):hit_summary([0]*32,[0,1])
        with self.assertRaises(ValueError):hit_summary([3]*128,[0,1])
        with self.assertRaises(ValueError):hit_summary([0]*128,[0])


if __name__=='__main__':unittest.main()
