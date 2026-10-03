import copy,json,tempfile,unittest
from pathlib import Path
from pretrained_masked_refolding import require_quality
from compare_pretrained_masked_models import ready_command


def qualified_fixture():
    arms=('parent','native_direct','generated_cond','generated_null','native_cond','native_null')
    rows=[dict(arm=a,samples=128,raw=26,valid=128) for a in arms]
    for r in rows:
        if r['arm']=='parent':r['raw']=25
        if r['arm']=='generated_null':r['raw']=20
        if r['arm']=='native_cond':r['raw']=103
    return dict(status='complete',profile_only=False,pretrained_masked=True,numerically_qualified=True,qualified=True,summary=rows,refold_gate=dict(qualified=True,improved_families=2,checks={k:True for k in ('native_capacity','native_validity','generated_validity','raw_gain_over_parent','raw_gain_over_null','families')}))


class PretrainedRefoldGateTests(unittest.TestCase):
    def test_full_gate_and_profile_rejection(self):
        d=qualified_fixture();require_quality(d);d['profile_only']=True
        with self.assertRaises(ValueError):require_quality(d)

    def test_native_success_does_not_rescue_generated_failure(self):
        d=qualified_fixture();next(r for r in d['summary'] if r['arm']=='generated_cond')['valid']=125
        with self.assertRaises(ValueError):require_quality(d)

    def test_qualified_flag_cannot_hide_missing_denominator_or_no_gain(self):
        for key,value in [('samples',127),('raw',25)]:
            d=qualified_fixture();next(r for r in d['summary'] if r['arm']=='generated_cond')[key]=value
            with self.assertRaises(ValueError):require_quality(d)

    def test_comparison_waits_for_registration_and_rejects_foreign_ids(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'runs').mkdir();(root/'reports').mkdir();path=root/'runs/pretrained_masked_model_comparison.json'
            d=dict(pretrained_masked_comparison=True,jobs={a:[None]*4 for a in ('generated_cond','generated_null')});path.write_text(json.dumps(d));self.assertIsNone(ready_command(root))
            d['jobs']={'generated_cond':['1','2','3','4'],'generated_null':['5','6','7','8']};path.write_text(json.dumps(d));(root/'runs/jobs.json').write_text('{"jobs":[]}')
            with self.assertRaises(ValueError):ready_command(root)


if __name__=='__main__':unittest.main()
