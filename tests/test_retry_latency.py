import unittest
import numpy as np
from retry_latency_core import bounded_outputs

class RetryLatencyTests(unittest.TestCase):
    def test_prefixes_keep_external_stride_and_first_valid_selection(self):
        calls=[]
        def draw(indices):
            calls.append(indices);bb=np.zeros((len(indices),3,4,3));bb[:,0,0,0]=indices;return bb
        geometry=lambda bb:dict(coarse_valid=np.isin(bb[:,0,0,0],[0,33,66]))
        bb,d=bounded_outputs(draw,3,geometry)
        self.assertEqual(calls,[[0,1,2],[33,34],[66]])
        self.assertEqual(d,dict(attempts=6,exhausted=0,selected_draws=[0,33,66]))
        self.assertEqual(bb[:,0,0,0].tolist(),[0,33,66])
    def test_exhausted_slots_return_first_draw_and_retain_failure_count(self):
        calls=[]
        def draw(indices):
            calls.append(indices);bb=np.zeros((len(indices),3,4,3));bb[:,0,0,0]=indices;return bb
        bb,d=bounded_outputs(draw,1,lambda bb:dict(coarse_valid=[False]))
        self.assertEqual(calls,[[0],[32],[64],[96]]);self.assertEqual(bb[0,0,0,0],0);self.assertEqual(d,dict(attempts=4,exhausted=1,selected_draws=[0]))
    def test_nonfinite_output_or_wrong_prefix_is_rejected(self):
        with self.assertRaises(ValueError):bounded_outputs(lambda indices:np.full((len(indices),3,4,3),np.nan),1)
        for k in (0,33,1.0):
            with self.assertRaises(ValueError):bounded_outputs(None,k)

if __name__=='__main__':unittest.main()
