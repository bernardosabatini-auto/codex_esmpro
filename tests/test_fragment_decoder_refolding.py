import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from fragment_decoder_training_core import refold_eligibility
from pretrained_masked_refolding import require_decoder_quality, study_of, qualify_training
from compare_fragment_decoder_models import ready_command
from compare_native_anchor_models import fragment_decoder_gate


def fixture(raw=9, valid=45):
    spec = json.loads((Path(__file__).resolve().parents[1]/'configs/fragment_decoder_protocol.json').read_text())
    ids = [str(i) for i in range(32)]
    counts = dict(parent=(25,128), native_direct=(128,128), generated_cond=(raw,valid),
                  generated_null=(0,0), native_cond=(0,0), native_null=(0,0))
    rows = [dict(arm=a, target_id=i, generation_slot=k, raw_gate_passed=j < nr, coarse_valid=j < nv)
            for a,(nr,nv) in counts.items() for j,(i,k) in enumerate((i,k) for i in ids for k in range(4))]
    summary = [dict(arm=a, samples=128, raw=nr, valid=nv) for a,(nr,nv) in counts.items()]
    return spec, dict(status='complete', fragment_decoder=True, profile_only=False,
                      numerically_qualified=True, qualified=True, updates=2000, records=rows, summary=summary,
                      refold_eligibility=refold_eligibility(summary,rows,ids,spec))


class DecoderRefoldTests(unittest.TestCase):
    def test_actual_joint_feasibility_without_surrogate_improvement(self):
        spec,d = fixture()
        require_decoder_quality(d,spec)
        with patch('fragment_decoder_training_core.audit') as audit:
            qualify_training(dict(spec=spec),d,'fragment_decoder')
            audit.assert_called_once()

    def test_ineligible_full_or_profile_cannot_export(self):
        for raw,valid in [(8,45),(9,44)]:
            spec,d = fixture(raw,valid)
            with self.assertRaises(ValueError): require_decoder_quality(d,spec)
        spec,d = fixture()
        for key,value in [('profile_only',True),('updates',40),('numerically_qualified',False),
                          ('fragment_decoder',False),('scaffold_clock',True),('pretrained_masked',True)]:
            bad = dict(d,**{key:value})
            with self.assertRaises(ValueError): require_decoder_quality(bad,spec)

    def test_tampered_counts_and_missing_samples_rejected(self):
        spec,original = fixture()
        for mutation in ('records','summary','eligibility'):
            d = copy.deepcopy(original)
            if mutation == 'records': d['records'].pop()
            elif mutation == 'summary': next(r for r in d['summary'] if r['arm']=='generated_cond')['raw'] += 1
            else: d['refold_eligibility']['checks']['strict_success_still_possible'] = False
            with self.assertRaises(ValueError): require_decoder_quality(d,spec)

    def test_unambiguous_model_family(self):
        self.assertEqual(study_of(dict(fragment_decoder_refold=True)),'fragment_decoder')
        for other in ('scaffold_clock','pretrained_masked'):
            with self.assertRaises(ValueError): study_of(dict(fragment_decoder_refold=True,**{other+'_refold':True}))

    def test_fm_study_cannot_be_confused_with_frozen_decoder_adapter(self):
        spec,d=fixture()
        d['fragment_decoder_fm']=True; del d['fragment_decoder']
        require_decoder_quality(d,spec,study='fragment_decoder_fm')
        with self.assertRaises(ValueError): require_decoder_quality(d,spec)
        with patch('fragment_decoder_fm_core.audit') as audit:
            qualify_training(dict(spec=spec),d,'fragment_decoder_fm')
            audit.assert_called_once()
        self.assertEqual(study_of(dict(fragment_decoder_fm_refold=True)),'fragment_decoder_fm')
        with self.assertRaises(ValueError): study_of(dict(fragment_decoder_fm_refold=True,fragment_decoder_refold=True))
        d['fragment_decoder']=True
        with self.assertRaises(ValueError): require_decoder_quality(d,spec,study='fragment_decoder_fm')

    def test_fm_watcher_waits_for_declared_registered_jobs(self):
        from compare_fragment_decoder_fm_models import ready_command as ready_fm
        with tempfile.TemporaryDirectory() as t:
            root=Path(t); (root/'runs').mkdir(); (root/'reports').mkdir()
            self.assertIsNone(ready_fm(root))
            plan=dict(fragment_decoder_fm_comparison=True,jobs={'generated_cond':['1','2','3','4'],'generated_null':['5','6','7','8']})
            (root/'runs/fragment_decoder_fm_model_comparison.json').write_text(json.dumps(plan))
            (root/'runs/jobs.json').write_text('{"jobs":[]}')
            with self.assertRaises(ValueError): ready_fm(root)

    def test_strict_improvement_must_beat_both_parent_and_null(self):
        parent = dict(strong=8,strong_families=7,designable=45)
        candidate = dict(strong=9,strong_families=7,designable=45)
        self.assertTrue(fragment_decoder_gate(candidate,parent,dict(strong=8)))
        self.assertFalse(fragment_decoder_gate(candidate,parent,dict(strong=9)))
        for key,value in [('strong',8),('strong_families',6),('designable',44)]:
            self.assertFalse(fragment_decoder_gate(dict(candidate,**{key:value}),parent,dict(strong=0)))

    def test_comparison_requires_unique_registered_completed_partitions(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            (root/'runs').mkdir(); (root/'reports').mkdir()
            path = root/'runs/fragment_decoder_model_comparison.json'
            plan = dict(fragment_decoder_comparison=True,jobs={a:[None]*4 for a in ('generated_cond','generated_null')})
            self.assertIsNone(ready_command(root))
            path.write_text(json.dumps(plan)); self.assertIsNone(ready_command(root))
            plan['jobs'] = dict(generated_cond=['1','2','3','4'], generated_null=['5','6','7','8'])
            path.write_text(json.dumps(plan)); (root/'runs/jobs.json').write_text('{"jobs":[]}')
            with self.assertRaises(ValueError): ready_command(root)
            registry = dict(jobs=[dict(id=str(i),completion_action='summarize_fragment_preference_refold') for i in range(1,9)])
            (root/'runs/jobs.json').write_text(json.dumps(registry)); self.assertIsNone(ready_command(root))
            for i in range(1,9): (root/f'reports/fragment_preference_refold_{i}.json').write_text('{"status":"complete"}')
            self.assertIsNotNone(ready_command(root))
            plan['jobs']['generated_null'][-1] = '1'; path.write_text(json.dumps(plan))
            with self.assertRaises(ValueError): ready_command(root)


if __name__ == '__main__': unittest.main()
