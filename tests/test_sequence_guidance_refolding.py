import unittest
from sequence_guidance_refolding import validate_pairing


class SequenceGuidancePairingTests(unittest.TestCase):
    def row(self):return dict(target_id='x',generation_slot=0,family='x',length=80,fixed_start=30,motif_start=30,fixed_sequence='ACDE')
    def test_changed_constraint_rejected(self):
        a=self.row();b=dict(a);validate_pairing([a],[b]);b['fixed_sequence']='EDCA'
        with self.assertRaises(ValueError):validate_pairing([a],[b])
    def test_duplicate_attempt_rejected(self):
        a=self.row()
        with self.assertRaises(ValueError):validate_pairing([a,a],[a])
