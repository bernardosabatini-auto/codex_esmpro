import json
from pathlib import Path
import unittest
from scaffold_clock_training_core import quality_gate


class ClockGateTests(unittest.TestCase):
    def setUp(self):
        self.spec = json.loads((Path(__file__).resolve().parents[1] / 'configs/scaffold_clock_protocol.json').read_text())
        self.ids = [str(i) for i in range(32)]
        self.raw = dict(parent=25, native_direct=128, generated_cond=30, generated_null=10,
                        native_cond=110, native_null=30, initial_generated_cond=20)
        self.valid = {a: 128 for a in self.raw}

    def result(self, duplicate=False):
        summary = [dict(arm=a, samples=128, raw=n, valid=self.valid[a]) for a, n in self.raw.items()]
        rows = [dict(arm=a, target_id=i, generation_slot=k, raw_gate_passed=j < self.raw[a],
                     coarse_valid=j < self.valid[a])
                for a in self.raw for j, (i, k) in enumerate((i, k) for i in self.ids for k in range(4))]
        if duplicate:
            rows[-1] = rows[-2]
        return quality_gate(summary, rows, self.ids, self.spec)

    def test_complete_improvement_passes(self):
        self.assertTrue(self.result()['qualified'])

    def test_invalid_candidate_fails_despite_more_raw_matches(self):
        self.valid['generated_cond'] = 122
        d = self.result()
        self.assertFalse(d['qualified'])
        self.assertFalse(d['checks']['generated_validity'])

    def test_untrained_path_must_be_beaten(self):
        self.raw['initial_generated_cond'] = 30
        self.assertFalse(self.result()['checks']['raw_gain_over_initial'])

    def test_oracle_capacity_is_separate_from_generated_success(self):
        self.raw['native_cond'] = 81
        self.assertFalse(self.result()['qualified'])

    def test_duplicate_output_rejected(self):
        with self.assertRaises(ValueError):
            self.result(duplicate=True)


if __name__ == '__main__':
    unittest.main()
