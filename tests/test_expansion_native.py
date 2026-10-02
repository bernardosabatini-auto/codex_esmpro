import copy,json,tempfile,unittest
from pathlib import Path
from prepare_overfit import sha
from summarize_expansion_native import analyze


class ExpansionNativeTests(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup);root=Path(tmp.name)
        protocol=json.loads(Path('configs/expansion_native_protocol.json').read_text());p=root/'protocol.json';p.write_text(json.dumps(protocol))
        selection=root/'selection.json';selection.write_text(json.dumps(dict(tuning=[dict(id=str(i),family='f'+str(i)) for i in range(64)])))
        capacity=root/'capacity.json';capacity.write_text(json.dumps(dict(training_targets=450,step=500,matched=True)))
        c=dict(protocol=str(p),protocol_sha256=sha(p),selection=str(selection),selection_sha256=sha(selection),capacity_report=str(capacity),capacity_report_sha256=sha(capacity),heads=[dict(name=h) for h in protocol['heads']],training_family_count=450,training_checkpoint_step=500)
        settings=[(h,g) for h in protocol['heads'] for g in protocol['guidance_by_head'][h]]
        self.m=dict(config=c,training_updates_executed=0,controls=[dict(head=h,guidance=g,length=b,ca_rmsd=0,ca_lddt=1) for h,g in settings for b in (128,256,384,512)],scores=[dict(head=h,guidance=g,target_id=str(i),sample=k,ca_lddt=.8,coarse_valid=1.) for h,g in settings for i in range(64) for k in range(3)])

    def test_identity_and_seed_specific_geometry_failure(self):
        self.assertTrue(analyze(self.m)['replicated_quality_passed'])
        rows=[r for r in self.m['scores'] if r['head']=='seed2026100181_expansion']
        for r in rows[:2]:r['coarse_valid']=0
        result=analyze(self.m);self.assertFalse(result['replicated_quality_passed']);self.assertTrue(result['summaries']['seed2026100171_expansion_cfg1']['quality_passed'])

    def test_reject_incomplete_duplicate_and_wrong_scope(self):
        for mode in ('missing','duplicate','nonfinite','control','training','step'):
            m=copy.deepcopy(self.m)
            if mode=='missing':m['scores'].pop()
            elif mode=='duplicate':m['scores'][-1]=m['scores'][-2].copy()
            elif mode=='nonfinite':m['scores'][0]['ca_lddt']=float('nan')
            elif mode=='control':m['controls'][0]['ca_rmsd']=.21
            elif mode=='training':m['training_updates_executed']=1
            else:m['config']['training_checkpoint_step']=2000
            with self.assertRaises(ValueError):analyze(m)


if __name__=='__main__':unittest.main()
