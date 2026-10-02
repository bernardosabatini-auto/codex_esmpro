"""Do not advance a checkpoint on training recall or transfer alone."""
import copy,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from prepare_capacity_ensemble import qualified


class QualificationTests(unittest.TestCase):
    def test_joint_prerequisites(self):
        cap=dict(step=500,matched=True,capacity_checks=dict(aligned_teacher=dict(passed=True)))
        transfer=dict(summaries=dict(aligned_teacher_balanced_cfg1=dict(quality_passed=True)))
        self.assertEqual(qualified(cap,transfer,'aligned_teacher_balanced',1),'aligned_teacher_balanced_cfg1')
        final=copy.deepcopy(cap);final['step']=2000
        self.assertEqual(qualified(final,transfer,'aligned_teacher_balanced',1,step=2000),'aligned_teacher_balanced_cfg1')
        with self.assertRaises(ValueError):qualified(cap,transfer,'aligned_teacher_balanced',1,step=2000)
        for kind in ('capacity','transfer','step','matched','guidance','head'):
            c=copy.deepcopy(cap);t=copy.deepcopy(transfer);head='aligned_teacher_balanced';guidance=1
            if kind=='capacity':c['capacity_checks']['aligned_teacher']['passed']=False
            if kind=='transfer':t['summaries']['aligned_teacher_balanced_cfg1']['quality_passed']=False
            if kind=='step':c['step']=2000
            if kind=='matched':c['matched']=False
            if kind=='guidance':guidance=2
            if kind=='head':head='aligned_teacher_empirical'
            with self.subTest(kind=kind),self.assertRaises(ValueError):qualified(c,t,head,guidance)


if __name__=='__main__':unittest.main()
