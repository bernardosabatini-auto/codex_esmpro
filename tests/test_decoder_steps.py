import copy,itertools,json,tempfile,unittest
from pathlib import Path
from prepare_overfit import sha
from summarize_decoder_steps import analyze,METRICS


class DecoderTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);root=Path(self.tmp.name);protocol=json.loads(Path('configs/decoder_steps_protocol.json').read_text());heads=protocol['heads']
        p=root/'protocol.json';p.write_text(json.dumps(protocol));selection=root/'selection.json';selection.write_text(json.dumps(dict(tuning=[dict(id=str(i),family='f'+str(i),bucket=(128,256,384,512)[i//16]) for i in range(64)])))
        rows=[dict(head=h,decoder_steps=s,target_id=str(i),sample=k,guidance=protocol['guidance_by_head'][h][0],ca_lddt=.8,coarse_valid=1.,peptide_outlier_fraction=0.,ca_clashing_residue_fraction=0.,ca_gap_fraction=0.) for h,s,i,k in itertools.product(heads,(3,5,10),range(64),range(3))]
        source=root/'source.json';source.write_text(json.dumps(dict(status='complete',scores=[r for r in rows if r['decoder_steps']==3])))
        c=dict(heads=[dict(name=h) for h in heads],training_checkpoint_step=500)
        for key,path in [('protocol',p),('selection',selection),('source_native_manifest',source)]:c[key]=str(path);c[key+'_sha256']=sha(path)
        times=[dict(head=h,stage='flow' if s==0 else 'decoder',decoder_steps=s,length=l,offset=o,seconds=1) for h,s,l,o in itertools.product(heads,(0,3,5,10),(128,256,384,512),(0,8))]
        self.m=dict(config=c,scores=rows,batches=times,controls=[dict(head=h,decoder_steps=s,length=l,ca_rmsd=0,ca_lddt=1) for h,s,l in itertools.product(heads,(3,5,10),(128,256,384,512))],reproduction_controls=[dict(head=h,target_id=str(i),sample=k,ca_rmsd=0,ca_lddt=1) for h,i,k in itertools.product(heads,range(64),range(3))],training_updates_executed=0)
    def test_identity(self):
        d=analyze(self.m);self.assertTrue(all(d['replicated_quality_by_decoder'].values()))
        for r in d['summaries'].values():self.assertEqual(r['versus_same_head_decoder3']['ca_lddt']['ci95'],[0,0])
    def test_longer_decoder_can_fail(self):
        rows=[r for r in self.m['scores'] if r['head']=='seed2026100181_balanced' and r['decoder_steps']==10]
        for r in rows[:2]:r['coarse_valid']=0
        self.assertFalse(analyze(self.m)['replicated_quality_by_decoder']['10'])
    def test_missing_duplicate_or_changed_reproduction(self):
        for mode in ('missing','duplicate','reproduction','timing'):
            m=copy.deepcopy(self.m)
            if mode=='missing':m['controls'].pop()
            elif mode=='duplicate':m['scores'][-1]=m['scores'][-2].copy()
            elif mode=='reproduction':m['scores'][0]['ca_lddt']=.79
            else:m['batches'].pop()
            with self.assertRaises(ValueError):analyze(m)


if __name__=='__main__':unittest.main()
