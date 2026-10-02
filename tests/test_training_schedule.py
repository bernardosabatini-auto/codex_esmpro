"""The broader length schedule must avoid over-weighting small buckets."""
import unittest,numpy as np
from latentfold.training_schedule import proportional_schedule


class ScheduleTests(unittest.TestCase):
    def test_equal_expected_protein_weights_and_reproducibility(self):
        counts={128:5,256:70,384:25,512:22}
        draws=proportional_schedule(counts,200000,2026100173)
        self.assertEqual(draws[:500],proportional_schedule(dict(reversed(list(counts.items()))),500,2026100173))
        values=np.asarray(draws)
        for length,n in counts.items():
            # Estimate each protein's expected mean-loss coefficient. Uniform
            # bucket cycling would fail this check by14x between128 and256.
            self.assertAlmostEqual(float((values==length).mean())/n,1/122,delta=.00015)

    def test_invalid_inputs(self):
        for counts,n in (({},1),({128:0},1),({128:1.5},1),({128:2},0)):
            with self.assertRaises(ValueError):proportional_schedule(counts,n,1)


if __name__=='__main__':unittest.main()
