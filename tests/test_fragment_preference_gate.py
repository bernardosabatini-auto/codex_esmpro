import unittest
from compare_fragment_preferences import feasibility_gate


class GateTests(unittest.TestCase):
    def setUp(self):
        self.limits=dict(minimum_confirmed=8,minimum_confirmation_rate=.75,minimum_buckets=3,
                         minimum_long_confirmed=2,minimum_native_global_scaffold=24)
        self.selected=[dict(id=str(k),length=(k%4+1)*128,bucket=(k%4+1)*128) for k in range(32)]
        self.preferences=[dict(target_id=str(k),eligible=k<8,confirmed=k<8) for k in range(32)]

    def gate(self,native=24):return feasibility_gate(self.preferences,self.selected,native,self.limits)

    def test_all_required(self):
        self.assertTrue(self.gate()['qualified'])
        self.assertFalse(self.gate(23)['qualified'])
        self.preferences[0]['confirmed']=False
        self.assertFalse(self.gate()['qualified'])

    def test_cannot_discard_failed_confirmations(self):
        for r in self.preferences[:11]:r['eligible']=True
        self.assertFalse(self.gate()['checks']['confirmation_rate'])
        self.preferences[10]['eligible']=False
        self.assertTrue(self.gate()['checks']['confirmation_rate'])

    def test_length_coverage_required(self):
        for row in self.selected:row.update(length=128,bucket=128)
        result=self.gate()
        self.assertFalse(result['checks']['length_buckets'])
        self.assertFalse(result['checks']['long_proteins'])

    def test_empty_is_failure(self):
        for r in self.preferences:r.update(eligible=False,confirmed=False)
        self.assertEqual(self.gate()['confirmation_rate'],0)
        self.assertFalse(self.gate()['qualified'])


if __name__=='__main__':unittest.main()
