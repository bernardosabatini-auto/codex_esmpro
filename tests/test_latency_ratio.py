import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from summarize_ensemble_latency import speed_ratio


class RatioTests(unittest.TestCase):
    def test_paired_known_speedup(self):
        r=speed_ratio({'a':2.,'b':8.},{'a':1.,'b':4.})
        self.assertEqual(r['reference_seconds_over_candidate'],2.)
        self.assertEqual(r['ci95'],[2.,2.])

    def test_reject_unmatched_or_invalid_times(self):
        for ref,cand in [({'a':1},{'b':1}),({'a':1},{'a':0}),({'a':float('nan')},{'a':1})]:
            with self.assertRaises(ValueError):speed_ratio(ref,cand)


if __name__=='__main__':unittest.main()
