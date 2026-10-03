import unittest
from fragment_validation_core import view_rows


class ValidationCohortTests(unittest.TestCase):
    def test_overlapping_views_never_change_denominators(self):
        rows=[dict(arm=arm,target_id=str(i),generation_slot=k,raw_gate_passed=(i==0 and k==15)) for arm in ('plain','weighted') for i in range(16) for k in range(16 if i==0 else 4)]
        self.assertEqual(len(rows),152)
        for arm in ('plain','weighted'):
            panel=view_rows(rows,arm,'whole_panel','0');focus=view_rows(rows,arm,'focus','0')
            self.assertEqual(len(panel),64);self.assertEqual(len(focus),16)
            p={(r['target_id'],r['generation_slot']) for r in panel};f={(r['target_id'],r['generation_slot']) for r in focus}
            self.assertEqual(len(p|f),76);self.assertEqual(len(p&f),4)
            self.assertEqual(sum(r['raw_gate_passed'] for r in panel),0);self.assertEqual(sum(r['raw_gate_passed'] for r in focus),1)
        with self.assertRaises(ValueError):view_rows(rows,'plain','pooled','0')
