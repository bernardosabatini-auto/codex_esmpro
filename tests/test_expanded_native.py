import copy,json,tempfile,unittest
from pathlib import Path
from prepare_overfit import sha
from summarize_expanded_native import analyze


class ExpandedNativeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);root=Path(self.tmp.name)
        protocol=json.loads(Path('configs/expanded_native_protocol.json').read_text());p=root/'protocol.json';p.write_text(json.dumps(protocol))
        selection=root/'selection.json';selection.write_text(json.dumps(dict(tuning=[dict(id=str(i),family='f'+str(i)) for i in range(64)])))
        c=dict(protocol=str(p),protocol_sha256=sha(p),selection=str(selection),selection_sha256=sha(selection),heads=[dict(name=h) for h in protocol['heads']],training_family_count=122,training_checkpoint_step=500)
        settings=[(h,g) for h in protocol['heads'] for g in protocol['guidance_by_head'][h]]
        self.m=dict(config=c,training_updates_executed=0,controls=[dict(head=h,guidance=g,length=l,ca_rmsd=0,ca_lddt=1) for h,g in settings for l in (128,256,384,512)],scores=[dict(head=h,guidance=g,target_id=str(i),sample=k,ca_lddt=.8,coarse_valid=1.) for h,g in settings for i in range(64) for k in range(3)])
    def test_identity(self):
        d=analyze(self.m);self.assertTrue(d['replicated_quality_passed'])
        for r in d['prior_effects'].values():self.assertEqual(r['ca_lddt']['ci95'],[0,0])
    def test_one_seed_failure_not_replicated(self):
        rows=[r for r in self.m['scores'] if r['head']=='seed2026100181_balanced']
        for r in rows[:2]:r['coarse_valid']=0
        d=analyze(self.m);self.assertFalse(d['replicated_quality_passed']);self.assertTrue(d['summaries']['seed2026100171_balanced_cfg1']['quality_passed'])
    def test_missing_duplicate_nonfinite_or_controls_rejected(self):
        for mode in ('missing','duplicate','nonfinite','control'):
            m=copy.deepcopy(self.m)
            if mode=='missing':m['scores'].pop()
            elif mode=='duplicate':m['scores'][-1]=m['scores'][-2].copy()
            elif mode=='nonfinite':m['scores'][0]['ca_lddt']=float('nan')
            else:m['controls'][-1]['ca_rmsd']=.21
            with self.assertRaises(ValueError):analyze(m)

    def test_tail_pairs_use_same_gate_and_require_both_seeds(self):
        c=self.m['config'];protocol=json.loads(Path('configs/tail_native_protocol.json').read_text())
        old=[h['name'] for h in c['heads']];names=dict(zip(old,protocol['heads']))
        for r in self.m['scores']+self.m['controls']:r['head']=names[r['head']]
        c['heads']=[dict(name=h) for h in protocol['heads']]
        p=Path(c['protocol']);p.write_text(json.dumps(protocol));c['protocol_sha256']=sha(p)
        d=analyze(self.m);self.assertTrue(d['replicated_quality_passed']);self.assertIn('adaptation_effects',d);self.assertNotIn('prior_effects',d)
        rows=[r for r in self.m['scores'] if r['head']=='seed2026100181_tail']
        for r in rows[:2]:r['coarse_valid']=0
        d=analyze(self.m);self.assertFalse(d['replicated_quality_passed']);self.assertTrue(d['summaries']['seed2026100171_tail_cfg1']['quality_passed'])

    def test_fixed_blend_scope_and_quality_gate(self):
        c=self.m['config'];protocol=json.loads(Path('configs/blend_native_protocol.json').read_text())
        names=dict(zip([h['name'] for h in c['heads']],protocol['heads']))
        for r in self.m['scores']+self.m['controls']:r['head']=names[r['head']]
        c.update(heads=[dict(name=h) for h in protocol['heads']],blend_alpha=.5,training_checkpoint_step=2000)
        p=Path(c['protocol']);p.write_text(json.dumps(protocol));c['protocol_sha256']=sha(p)
        d=analyze(self.m);self.assertTrue(d['replicated_quality_passed']);self.assertIn('blend_effects',d)
        c['blend_alpha']=.75
        with self.assertRaises(ValueError):analyze(self.m)


if __name__=='__main__':unittest.main()
