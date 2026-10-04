import json
from pathlib import Path
import unittest

from fragment_decoder_training_core import refold_eligibility


class DecoderEligibilityTests(unittest.TestCase):
    def setUp(self):
        self.spec = json.loads((Path(__file__).resolve().parents[1]/'configs/fragment_decoder_protocol.json').read_text())
        self.ids = [str(i) for i in range(32)]
        self.raw = dict(parent=25, native_direct=128, generated_cond=9, generated_null=0, native_cond=0, native_null=0)
        self.valid = dict(parent=128, native_direct=128, generated_cond=45, generated_null=0, native_cond=0, native_null=0)

    def result(self, duplicate=False):
        summary = [dict(arm=a, samples=128, raw=n, valid=self.valid[a]) for a, n in self.raw.items()]
        rows = [dict(arm=a, target_id=i, generation_slot=k, raw_gate_passed=j < self.raw[a], coarse_valid=j < self.valid[a])
                for a in self.raw for j, (i, k) in enumerate((i, k) for i in self.ids for k in range(4))]
        if duplicate:
            rows[-1] = rows[-2]
        return refold_eligibility(summary, rows, self.ids, self.spec)

    def test_raw_gain_and_native_capacity_are_not_designability_surrogates(self):
        self.assertTrue(self.result()['qualified'])

    def test_cannot_exceed_eight_strict_successes_with_only_eight_raw_matches(self):
        self.raw['generated_cond'] = 8
        self.assertFalse(self.result()['checks']['strict_success_still_possible'])

    def test_cannot_reach_designability_floor_with_only_44_valid_backbones(self):
        self.valid['generated_cond'] = 44
        self.assertFalse(self.result()['checks']['designability_floor_still_possible'])

    def test_duplicate_output_rejected(self):
        with self.assertRaises(ValueError):
            self.result(duplicate=True)

    def test_changed_parent_rejected(self):
        self.raw['parent'] = 26
        with self.assertRaises(ValueError):
            self.result()


if __name__ == '__main__':
    unittest.main()
