"""Coverage and noninferiority controls for the transfer evaluator."""
import copy,json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from prepare_overfit import sha
from summarize_overfit_native import analyze


class TransferTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);root=Path(self.tmp.name)
        names=['original','aligned_teacher_empirical','pca_teacher_empirical','aligned_teacher_balanced','pca_teacher_balanced']
        selection=root/'selection.json';selection.write_text(json.dumps(dict(tuning=[dict(id=str(i),family='f'+str(i)) for i in range(64)])))
        protocol=root/'protocol.json';protocol.write_text(json.dumps(dict(heads=names)))
        c=dict(selection=str(selection),selection_sha256=sha(selection),protocol=str(protocol),protocol_sha256=sha(protocol),heads=[dict(name=n) for n in names])
        self.m=dict(config=c,training_updates_executed=0,scores=[dict(head=n,guidance=g,target_id=str(i),sample=k,ca_lddt=.8,coarse_valid=1.) for n in names for g in (1,2) for i in range(64) for k in range(3)],controls=[dict(head=n,guidance=g,length=l,ca_rmsd=0.,ca_lddt=1.) for n in names for g in (1,2) for l in (128,256,384,512)])

    def test_identity_has_zero_differences(self):
        d=analyze(self.m)
        for r in d['summaries'].values():
            self.assertTrue(r['quality_passed']);self.assertEqual(r['versus_original_cfg2']['ca_lddt']['ci95'],[0,0])
        for r in d['prior_effects'].values():self.assertEqual(r['ca_lddt']['difference'],0)

    def test_two_extra_invalid_samples_fail_margin(self):
        rows=[r for r in self.m['scores'] if r['head']=='aligned_teacher_balanced' and r['guidance']==1]
        for r in rows[:2]:r['coarse_valid']=0.
        d=analyze(self.m)['summaries']['aligned_teacher_balanced_cfg1']
        self.assertFalse(d['quality_passed']);self.assertAlmostEqual(d['versus_original_cfg2']['coarse_valid']['difference'],-2/192)

    def test_accuracy_regression_fails(self):
        for r in self.m['scores']:
            if r['head']=='pca_teacher_balanced':r['ca_lddt']-=.02
        self.assertFalse(analyze(self.m)['summaries']['pca_teacher_balanced_cfg2']['quality_passed'])

    def test_missing_duplicate_or_bad_controls_are_rejected(self):
        for mutation in ('missing','duplicate','bad_control'):
            m=copy.deepcopy(self.m)
            if mutation=='missing':m['scores'].pop()
            elif mutation=='duplicate':m['scores'][-1]=m['scores'][-2].copy()
            else:m['controls'][0]['ca_rmsd']=1.
            with self.assertRaises(ValueError):analyze(m)


if __name__=='__main__':unittest.main()
