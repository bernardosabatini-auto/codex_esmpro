import copy
import json
from pathlib import Path
import tempfile
import unittest
from fragment_inpainting_core import refold_eligibility
from pretrained_masked_refolding import require_decoder_quality,refold_arms,study_of
from compare_native_anchor_models import inpainting_gate
from compare_fragment_inpainting_models import ready_command


def fixture(raw=9,valid=45):
    spec=dict(updates=2000,refold_eligibility=dict(generated_cond_min_raw=9,generated_cond_min_valid=45))
    ids=[str(i) for i in range(32)]
    counts=dict(parent=(25,128),native_direct=(128,128),generated_cond=(raw,valid),
                generated_null=(0,0),native_cond=(128,128),native_null=(0,0),generated_untrained=(9,45),native_untrained=(128,128))
    rows=[dict(arm=a,target_id=i,generation_slot=k,raw_gate_passed=j<nr,coarse_valid=j<nv)
          for a,(nr,nv) in counts.items() for j,(i,k) in enumerate((i,k) for i in ids for k in range(4))]
    summary=[dict(arm=a,samples=128,raw=nr,valid=nv) for a,(nr,nv) in counts.items()]
    gate=refold_eligibility(summary,rows,ids,spec)
    return spec,dict(status='complete',fragment_inpainting=True,profile_only=False,numerically_qualified=True,
                     qualified=gate['qualified'],updates=2000,records=rows,summary=summary,refold_eligibility=gate)


class InpaintingRefoldTests(unittest.TestCase):
    def test_only_full_eligible_inpainting_can_export(self):
        spec,d=fixture();require_decoder_quality(d,spec,study='fragment_inpainting')
        for key,value in [('profile_only',True),('updates',40),('fragment_decoder_fm',True),('numerically_qualified',False)]:
            with self.assertRaises(ValueError):require_decoder_quality(dict(d,**{key:value}),spec,study='fragment_inpainting')
        for raw,valid in [(8,45),(9,44)]:
            spec,d=fixture(raw,valid)
            with self.assertRaises(ValueError):require_decoder_quality(d,spec,study='fragment_inpainting')

    def test_untrained_comparator_is_required_and_cannot_be_null(self):
        self.assertEqual(refold_arms('fragment_inpainting'),('generated_cond','generated_untrained'))
        self.assertEqual(study_of(dict(fragment_inpainting_refold=True)),'fragment_inpainting')
        spec,d=fixture();bad=copy.deepcopy(d)
        bad['records']=[r for r in bad['records'] if r['arm']!='generated_untrained']
        with self.assertRaises(ValueError):require_decoder_quality(bad,spec,study='fragment_inpainting')
        with self.assertRaises(ValueError):study_of(dict(fragment_inpainting_refold=True,fragment_decoder_fm_refold=True))

    def test_primary_rule_requires_gain_and_designability_against_both(self):
        parent=dict(strong=8,strong_families=7,designable=45)
        untrained=dict(strong=10,strong_families=8,designable=51)
        self.assertTrue(inpainting_gate(dict(strong=11,strong_families=7,designable=51),parent,untrained))
        for c in [dict(strong=10,strong_families=7,designable=51),dict(strong=11,strong_families=6,designable=51),dict(strong=11,strong_families=7,designable=50)]:
            self.assertFalse(inpainting_gate(c,parent,untrained))

    def test_completion_requires_eight_unique_owned_finished_reports(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'runs').mkdir();(root/'reports').mkdir()
            path=root/'runs/fragment_inpainting_model_comparison.json'
            plan=dict(fragment_inpainting_comparison=True,jobs={'generated_cond':['1','2','3','4'],'generated_untrained':['5','6','7','8']})
            path.write_text(json.dumps(plan));(root/'runs/jobs.json').write_text('{"jobs":[]}')
            with self.assertRaises(ValueError):ready_command(root)
            (root/'runs/jobs.json').write_text(json.dumps(dict(jobs=[dict(id=str(i),completion_action='summarize_fragment_preference_refold') for i in range(1,9)])))
            self.assertIsNone(ready_command(root))
            for i in range(1,9):(root/f'reports/fragment_preference_refold_{i}.json').write_text('{"status":"complete"}')
            self.assertIsNotNone(ready_command(root))
            plan['jobs']['generated_untrained'][0]='1';path.write_text(json.dumps(plan))
            with self.assertRaises(ValueError):ready_command(root)


if __name__=='__main__':unittest.main()
