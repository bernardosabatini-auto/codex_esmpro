import copy,json,tempfile,unittest
from pathlib import Path
from prepare_overfit import sha
from summarize_replay_native import analyze
from prepare_replay_ensemble import qualified,training_identity


class ReplayNativeTests(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup);root=Path(tmp.name)
        protocol=json.loads(Path('configs/replay_native_protocol.json').read_text());p=root/'protocol.json';p.write_text(json.dumps(protocol))
        selection=root/'selection.json';selection.write_text(json.dumps(dict(tuning=[dict(id=str(i),family='f'+str(i)) for i in range(64)])))
        self.capacity=dict(training_targets=427,step=500,matched=True,seeds=[2026100171,2026100181],replicated_capacity_retained=True)
        capacity=root/'capacity.json';capacity.write_text(json.dumps(self.capacity))
        c=dict(protocol=str(p),protocol_sha256=sha(p),selection=str(selection),selection_sha256=sha(selection),capacity_report=str(capacity),capacity_report_sha256=sha(capacity),heads=[dict(name=h) for h in protocol['heads']],training_family_count=427,replay_family_count=390,training_checkpoint_step=500,evaluation_seed=123)
        settings=[(h,g) for h in protocol['heads'] for g in protocol['guidance_by_head'][h]]
        self.m=dict(status='complete',config=c,training_updates_executed=0,controls=[dict(head=h,guidance=g,length=b,ca_rmsd=0,ca_lddt=1) for h,g in settings for b in (128,256,384,512)],scores=[dict(head=h,guidance=g,target_id=str(i),sample=k,ca_lddt=.8,coarse_valid=1.) for h,g in settings for i in range(64) for k in range(3)])
        plain=copy.deepcopy(self.m);plain_protocol=root/'plain_protocol.json';plain_protocol.write_text(Path('configs/expansion_native_protocol.json').read_text())
        plain['config'].update(protocol=str(plain_protocol),protocol_sha256=sha(plain_protocol))
        for row in plain['config']['heads']:row['name']=row['name'].replace('_replay','_expansion')
        for row in plain['scores']+plain['controls']:row['head']=row['head'].replace('_replay','_expansion')
        pp=root/'plain.json';pp.write_text(json.dumps(plain));c.update(plain_native_manifest=str(pp),plain_native_manifest_sha256=sha(pp))

    def test_identical_baseline_and_individual_quality_gate(self):
        d=analyze(self.m);self.assertTrue(d['replicated_quality_passed'])
        for r in [r for r in self.m['scores'] if r['head']=='seed2026100181_replay'][:2]:r['coarse_valid']=0
        d=analyze(self.m);self.assertFalse(d['replicated_quality_passed']);self.assertTrue(d['summaries']['seed2026100171_replay_cfg1']['quality_passed'])
        self.assertEqual(qualified(self.capacity,d,'seed2026100171_replay',1),'seed2026100171_replay_cfg1')
        with self.assertRaisesRegex(ValueError,'transfer'):qualified(self.capacity,d,'seed2026100181_replay',1)

    def test_incomplete_scores_controls_and_changed_original_rejected(self):
        for mode in ('missing','duplicate','nonfinite','control','original'):
            m=copy.deepcopy(self.m)
            if mode=='missing':m['scores'].pop()
            elif mode=='duplicate':m['scores'][-1]=m['scores'][-2].copy()
            elif mode=='nonfinite':m['scores'][0]['ca_lddt']=float('nan')
            elif mode=='control':m['controls'][0]['ca_rmsd']=.21
            else:m['scores'][0]['ca_lddt']=.9
            with self.assertRaises(ValueError):analyze(m)

    def test_capacity_and_training_identity_mandatory(self):
        d=analyze(self.m);c=copy.deepcopy(self.capacity);c['replicated_capacity_retained']=False
        with self.assertRaisesRegex(ValueError,'capacity'):qualified(c,d,'seed2026100171_replay',1)
        identity=dict(functional_replay=True,seed=2026100171,label_distribution='balanced',corpus_kind='expansion')
        training_identity(identity,'seed2026100171_replay');identity['functional_replay']=False
        with self.assertRaises(ValueError):training_identity(identity,'seed2026100171_replay')


if __name__=='__main__':unittest.main()
