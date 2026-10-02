import unittest
from diagnose_model_mixtures import combine

class MixtureTests(unittest.TestCase):
    def test_fixed_prefix_does_not_choose_late_desired_state(self):
        rows={'a':dict(assignments=[0]*32,quality=[.9]*32,valid=[True]*32),'b':dict(assignments=[None]*16+[1]*16,quality=[.8]*32,valid=[True]*32)}
        r=combine(rows,dict(a=16,b=16));self.assertEqual(r['coverage'],.5);self.assertEqual(r['both_states'],0.)
        with self.assertRaises(ValueError):combine(rows,dict(a=32,b=32))
    def test_complementary_states_can_be_recovered_without_reference_selection(self):
        rows={'a':dict(assignments=[0]*32,quality=[.9]*32,valid=[True]*32),'b':dict(assignments=[1]*32,quality=[.8]*32,valid=[True]*32)}
        r=combine(rows,dict(a=16,b=16));self.assertEqual(r['coverage'],1.);self.assertAlmostEqual(r['ca_lddt'],.85)

if __name__=='__main__':unittest.main()
