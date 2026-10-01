import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from matched_online_analysis import ORDER, VARIANTS, timing_result, selected_rows


class MatchedOnlineTests(unittest.TestCase):
    def fixture(self):
        passes=[]
        for repeat,order in enumerate(ORDER):
            for name in order:
                passes.append(dict(repeat=repeat,variant=name,status='complete',choices={'protein':1},
                    fingerprints=['a'*64],identical_to_first=True,batches=[dict(length=128,batch=3,proteins=1,
                    seconds=3.0 if name=='reference' else 1.0,selection_seconds=.1,peak_reserved_bytes=1024)]))
        return dict(order=ORDER,variants=VARIANTS,config=dict(target_ids=['protein']),passes=passes)

    def test_repeat_identity_and_coverage_gate(self):
        m=self.fixture()
        self.assertTrue(timing_result(m)['speed_gate_passed'])
        changed=copy.deepcopy(m)
        changed['passes'][-1]['fingerprints']=['b'*64]
        with self.assertRaises(ValueError):timing_result(changed)
        changed['passes'][-1]['identical_to_first']=False
        self.assertFalse(timing_result(changed)['speed_gate_passed'])
        missing=copy.deepcopy(m);missing['passes'].pop()
        with self.assertRaises(ValueError):timing_result(missing)
        changed=copy.deepcopy(m);changed['passes'][-1]['batches'][0]['seconds']=2
        self.assertFalse(timing_result(changed)['speed_gate_passed'])

    def test_selected_scores_require_all_samples(self):
        rows=[dict(target_id='protein',sample=k,tm_fixed_reference=k/3) for k in range(3)]
        self.assertEqual(selected_rows(rows,{'protein':1}),[rows[1]])
        with self.assertRaises(ValueError):selected_rows(rows[:-1],{'protein':1})
        with self.assertRaises(ValueError):selected_rows(rows+rows[:1],{'protein':1})


if __name__=='__main__':unittest.main()
