import copy
import json
from pathlib import Path
import tempfile
import unittest

from scaffold_clock_training_core import quality_gate
from pretrained_masked_refolding import require_clock_quality, study_of
from compare_scaffold_clock_models import ready_command
from compare_native_anchor_models import diversity
from prepare_overfit import sha


def fixture():
    spec = json.loads((Path(__file__).resolve().parents[1] / 'configs/scaffold_clock_protocol.json').read_text())
    ids = [str(i) for i in range(32)]
    counts = dict(parent=25, native_direct=128, generated_cond=30, generated_null=10,
                  native_cond=110, native_null=30, initial_generated_cond=20)
    rows = [dict(arm=a, target_id=i, generation_slot=k, raw_gate_passed=j < counts[a], coarse_valid=True)
            for a in counts for j, (i, k) in enumerate((i, k) for i in ids for k in range(4))]
    summary = [dict(arm=a, samples=128, raw=n, valid=128) for a, n in counts.items()]
    return spec, dict(status='complete', profile_only=False, scaffold_clock=True, updates=2000,
                      numerically_qualified=True, qualified=True, summary=summary, records=rows,
                      refold_gate=quality_gate(summary, rows, ids, spec))


class ClockRefoldTests(unittest.TestCase):
    def test_actual_complete_gate_is_recomputed(self):
        spec, d = fixture()
        require_clock_quality(d, spec)
        d['refold_gate']['improved_families'] = 32
        with self.assertRaises(ValueError):
            require_clock_quality(d, spec)

    def test_profile_and_wrong_family_rejected(self):
        for key, value in [('profile_only', True), ('updates', 40), ('pretrained_masked', True)]:
            spec, d = fixture()
            d[key] = value
            with self.assertRaises(ValueError):
                require_clock_quality(d, spec)

    def test_missing_samples_and_forged_summary_rejected(self):
        spec, original = fixture()
        d = copy.deepcopy(original)
        d['records'].pop()
        with self.assertRaises(ValueError):
            require_clock_quality(d, spec)
        d = copy.deepcopy(original)
        next(r for r in d['summary'] if r['arm'] == 'generated_cond')['raw'] += 1
        with self.assertRaises(ValueError):
            require_clock_quality(d, spec)

    def test_initial_path_gain_cannot_be_bypassed_by_flags(self):
        spec, d = fixture()
        for r in d['records']:
            if r['arm'] == 'initial_generated_cond':
                r['raw_gate_passed'] = int(r['target_id']) * 4 + r['generation_slot'] < 30
        next(r for r in d['summary'] if r['arm'] == 'initial_generated_cond')['raw'] = 30
        with self.assertRaises(ValueError):
            require_clock_quality(d, spec)

    def test_study_must_be_unambiguous(self):
        self.assertEqual(study_of(dict(scaffold_clock_refold=True)), 'scaffold_clock')
        self.assertEqual(study_of(dict(pretrained_masked_refold=True)), 'pretrained_masked')
        for c in ({}, dict(pretrained_masked_refold=True, scaffold_clock_refold=True)):
            with self.assertRaises(ValueError):
                study_of(c)

    def test_callback_waits_for_own_complete_registration(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'runs').mkdir()
            (root / 'reports').mkdir()
            path = root / 'runs/scaffold_clock_model_comparison.json'
            d = dict(scaffold_clock_comparison=True, jobs={a: [None] * 4 for a in ('generated_cond', 'generated_null')})
            path.write_text(json.dumps(d))
            self.assertIsNone(ready_command(root))
            d['jobs'] = {'generated_cond': ['1', '2', '3', '4'], 'generated_null': ['5', '6', '7', '8']}
            path.write_text(json.dumps(d))
            (root / 'runs/jobs.json').write_text('{"jobs":[]}')
            with self.assertRaises(ValueError):
                ready_command(root)

    def test_shared_prediction_file_does_not_make_diversity_arms_interchangeable(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest, predictions, scorer, report = [root / p for p in ('manifest.json', 'predictions.h5', 'scorer', 'diversity.json')]
            for p in (manifest, predictions, scorer):
                p.write_bytes(b'fixture')
            report.write_text(json.dumps(dict(status='complete', manifest_sha256=sha(manifest),
                                             predictions_sha256=sha(predictions), scorer_sha256=sha(scorer),
                                             prediction_group='generated_null', records=[])))
            gc = dict(generation_manifest=str(manifest), config=dict(prediction_group='generated_cond'))
            with self.assertRaisesRegex(ValueError, 'different output arm'):
                diversity(gc, [], str(scorer), dict(path=str(report), sha256=sha(report)))


if __name__ == '__main__':
    unittest.main()
