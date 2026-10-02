import copy,itertools,json,tempfile,unittest
from pathlib import Path
from prepare_overfit import sha
from summarize_compact_native import analyze


class CompactTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);root=Path(self.tmp.name);protocol=json.loads(Path('configs/compact_native_protocol.json').read_text());p=root/'protocol.json';p.write_text(json.dumps(protocol));selection=root/'selection.json';selection.write_text(json.dumps(dict(tuning=[dict(id=str(i),family='f'+str(i)) for i in range(64)])))
        c=dict(protocol=str(p),protocol_sha256=sha(p),selection=str(selection),selection_sha256=sha(selection),heads=[dict(name=h) for h in protocol['heads']]);heads=protocol['heads'];modes=protocol['modes'];base=[dict(head=h,mode=mode,target_id=str(i),sample=k) for h,mode,i,k in itertools.product(heads,modes,range(64),range(3))]
        self.m=dict(config=c,training_updates_executed=0,scores=[dict(r,ca_lddt=.8,coarse_valid=1.) for r in base],agreement=[dict(r,ca_rmsd=0,ca_lddt=1.) for r in base],controls=[dict(head=h,mode=mode,length=l,ca_rmsd=0,ca_lddt=1.) for h,mode,l in itertools.product(heads,modes,(128,256,384,512))],batches=[dict(head=h,mode=mode,target_id=str(i),seconds=1) for h,mode,i in itertools.product(heads,modes,range(64))])
    def test_identity(self):self.assertEqual(analyze(self.m)['qualified_heads'],['original','aligned_teacher_balanced'])
    def test_regression_fails(self):
        rows=[r for r in self.m['scores'] if r['head']=='aligned_teacher_balanced' and r['mode']=='compact']
        for r in rows[:2]:r['coarse_valid']=0
        self.assertEqual(analyze(self.m)['qualified_heads'],['original'])
    def test_missing_duplicate_nonfinite_and_control(self):
        for mode in ('missing','duplicate','nonfinite','control'):
            m=copy.deepcopy(self.m)
            if mode=='missing':m['agreement'].pop()
            elif mode=='duplicate':m['scores'][-1]=m['scores'][-2].copy()
            elif mode=='nonfinite':m['scores'][0]['ca_lddt']=float('nan')
            else:m['controls'][0]['ca_rmsd']=.21
            with self.assertRaises(ValueError):analyze(m)


if __name__=='__main__':unittest.main()
