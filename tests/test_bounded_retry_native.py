import unittest
from summarize_bounded_retry_native import validate_slot,validate_prior_original

class NativeRetryTests(unittest.TestCase):
    def test_stops_first_valid_and_keeps_all_failures(self):
        draws=[dict(attempt=i,draw=1+3*i,coarse_valid=int(i==2)) for i in range(3)]
        s=dict(attempts=3,slot=1,exhausted=False,selected_draw=7)
        raw,chosen=validate_slot(draws,s);self.assertEqual(raw['draw'],1);self.assertEqual(chosen['draw'],7)
        with self.assertRaises(ValueError):validate_slot(draws,{**s,'selected_draw':1})
        draws[0]['coarse_valid']=1
        with self.assertRaises(ValueError):validate_slot(draws,s)

    def test_exhaustion_returns_original_only_after_four(self):
        draws=[dict(attempt=i,draw=2+3*i,coarse_valid=0) for i in range(4)]
        s=dict(attempts=4,slot=2,exhausted=True,selected_draw=2)
        self.assertEqual(validate_slot(draws,s)[1]['draw'],2)
        with self.assertRaises(ValueError):validate_slot(draws[:3],{**s,'attempts':3})
        with self.assertRaises(ValueError):validate_slot(draws,{**s,'selected_draw':11})

    def test_shared_original_identity_requires_all_slots_and_same_selection(self):
        rows=[dict(head='original',target_id=str(i),slot=k,draw=k,coarse_valid=1.,ca_lddt=.8) for i in range(64) for k in range(3)]
        prior=dict(status='complete',draws=rows,selections=[dict(head='original',target_id=r['target_id'],slot=r['slot'],selected_draw=r['draw']) for r in rows])
        current=[dict(r) for r in rows];validate_prior_original(current,prior)
        with self.assertRaises(ValueError):validate_prior_original(current[:-1],prior)
        current[0]['draw']=3
        with self.assertRaises(ValueError):validate_prior_original(current,prior)
        current[0]['draw']=0;current[0]['ca_lddt']=.79
        with self.assertRaises(ValueError):validate_prior_original(current,prior)

    def test_missing_duplicate_and_invalid_order_rejected(self):
        draws=[dict(attempt=i,draw=3*i,coarse_valid=int(i==1)) for i in range(2)]
        s=dict(attempts=2,slot=0,exhausted=False,selected_draw=3)
        with self.assertRaises(ValueError):validate_slot(draws[:1],s)
        with self.assertRaises(ValueError):validate_slot([draws[0],draws[0]],s)
        draws[1]['draw']=6
        with self.assertRaises(ValueError):validate_slot(draws,s)

if __name__=='__main__':unittest.main()
