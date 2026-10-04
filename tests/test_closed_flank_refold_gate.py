import unittest
from closed_flank_refold_gate import require_quality


def report(count=45):
    rows=[dict(arm=a,target_id=str(i),generation_slot=k,qualified_raw=(4*i+k<count),
               hidden_flank_bonds=dict(all_edges_valid=True),refold_eligible_geometry=(4*i+k<count))
          for a in ('generated_cond','generated_untrained') for i in range(32) for k in range(4)]
    return dict(status='complete',profile_only=False,flank_context=True,context_flank=8,numerically_qualified=True,updates=2000,
        closure_records=rows,closure_summary=[dict(arm=a,samples=128,refold_eligible_geometry=count) for a in ('generated_cond','generated_untrained')],
        qualified=count>=45,refold_eligibility=dict(qualified=count>=45,eligible_complete_geometry=count,required=45))


class ClosedFlankGate(unittest.TestCase):
    def test_exact_threshold_requires_complete_matched_denominators(self):
        self.assertEqual(require_quality(report()),dict(generated_cond=45,generated_untrained=45))
        with self.assertRaises(ValueError):require_quality(report(44))
        d=report();d['closure_records'].pop()
        with self.assertRaises(ValueError):require_quality(d)
        d=report();d['closure_records'][-1]=d['closure_records'][0]
        with self.assertRaises(ValueError):require_quality(d)

    def test_break_moved_to_outer_flank_cannot_pass(self):
        d=report();d['closure_records'][0]['hidden_flank_bonds']['all_edges_valid']=False
        with self.assertRaises(ValueError):require_quality(d)

    def test_profile_or_forged_summary_cannot_license_refolds(self):
        d=report();d['profile_only']=True
        with self.assertRaises(ValueError):require_quality(d)
        d=report(44);d['qualified']=True;d['refold_eligibility']['qualified']=True
        with self.assertRaises(ValueError):require_quality(d)


if __name__=='__main__':unittest.main()
