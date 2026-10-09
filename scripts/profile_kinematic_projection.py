"""Test a fixed training-derived bond envelope on completed decoder outputs."""
import argparse,json,time
from pathlib import Path
import h5py,numpy as np,torch
from latentfold.anchor_kinematics import encode,decode
from latentfold.backbone_sterics import steric_audit
from latentfold.metrics import usalign_coordinates
from fragment_validation_core import raw_rows
from fragment_junction_core import flank_bonds
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1]
    protocol=root/'configs/kinematic_projection_profile_protocol.json';spec=json.loads(protocol.read_text());run=root/'runs'/spec['source_generation']
    mp=run/'manifest.json';m=json.loads(mp.read_text());c=m['config'];report=root/'reports'/(run.name+'.json');d=json.loads(report.read_text())
    if m['status']!='complete' or d['status']!='complete' or d['manifest_sha256']!=sha(mp) or d['predictions_sha256']!=sha(run/'predictions.h5'):
        raise ValueError('Changed completed inpainting source')
    dm=root/'runs/fragment_context_flow_data_20261009/manifest.json';data=json.loads(dm.read_text());train={r['id'] for r in data['records'] if r['split']=='train'}
    excluded={r['family'] for r in data['records'] if r['split']!='train'}
    if len(train)!=464:raise ValueError('Changed empirical training partition')
    selected=[next(r for r in c['selected'] if r['bucket']==b) for b in (128,256,384,512)]
    rc=json.loads((root/'runs/context_retrieved_refold_20261009_0.json').read_text());binary=rc['usalign']
    if sha(binary)!=rc['usalign_sha256']:raise ValueError('Changed scorer')
    sources=[protocol,mp,report,run/'predictions.h5',Path(c['fragments']),dm,root/'src/latentfold/anchor_kinematics.py',Path(__file__)]
    bound=[dict(path=str(p.resolve()),sha256=sha(p)) for p in sources];a.output.mkdir(exist_ok=False);torch.set_num_threads(1);start=time.monotonic()
    pools={k:[[] for _ in range(3)] for k in ('lengths','angles')}
    with h5py.File(c['fragments'],locking=False) as fr:
        for ident in sorted(train):
            g=fr['train/'+ident]
            if str(g.attrs['family']) in excluded:raise ValueError('Held-out family in bond estimation')
            p=encode(torch.from_numpy(g['reference_backbone'][:][None]).double())
            for key in pools:
                values=p[key][0].numpy();types=(np.arange(len(values))+(1 if key=='angles' else 0))%3
                for j in range(3):pools[key][j].extend(values[types==j].tolist())
        limits={k:[np.quantile(v,[.001,.999]).tolist() for v in pools[k]] for k in pools};records=[]
        with h5py.File(run/'predictions.h5',locking=False) as predictions,h5py.File(a.output/'predictions.h5','x') as out:
            for row in selected:
                ident=row['id'];g=fr['train/'+ident];q=g['conditions/c20_center'];st=int(q.attrs['start'])
                inputs={arm:predictions[arm+'/'+ident+'/backbone'][:] for arm in ('generated_cond','generated_untrained','native_cond')}
                inputs['native_reference']=g['reference_backbone'][:][None]
                for arm,array in inputs.items():
                    for slot,old in enumerate(array):
                        r=dict(arm=arm,target_id=ident,slot=slot,bucket=row['bucket'],status='failed')
                        try:
                            x=torch.from_numpy(old[None]).double();p=encode(x)
                            for key in limits:
                                types=(torch.arange(p[key].shape[1])+(1 if key=='angles' else 0))%3
                                bounds=x.new_tensor(limits[key])[types];p[key]=torch.maximum(torch.minimum(p[key],bounds[:,1]),bounds[:,0])
                            new=decode(p,x[:,st:st+20],st)[0].numpy()
                            if not np.array_equal(new[st:st+20],old[st:st+20]):raise ValueError('Changed motif atoms')
                            def score(bb):
                                v=raw_rows(bb[None],q['fragment'][:],st,arm,ident,row['family'])[0]
                                v['connected']=flank_bonds(bb,st,20,8)['all_edges_valid'];v['overlap_free']=steric_audit(bb,list(range(row['length'])))['pairs_below_threshold']==0
                                v['joint']=bool(v['raw_gate_passed'] and v['connected'] and v['overlap_free']);return v
                            r.update(status='complete',source=score(old),projected=score(new),source_tm=usalign_coordinates(binary,new[:,1],old[:,1]))
                            out[f'{arm}/{ident}/{slot}']=new
                        except (ValueError,FloatingPointError) as error:r['error']=str(error)
                        records.append(r)
                print('profiled',row['bucket'],flush=True)
    summary={}
    for arm in ('generated_cond','generated_untrained','native_cond','native_reference'):
        rows=[r for r in records if r['arm']==arm];ok=[r for r in rows if r['status']=='complete']
        summary[arm]=dict(samples=len(rows),failures=len(rows)-len(ok),mean_source_tm=float(np.mean([r['source_tm'] for r in ok])) if ok else 0.,
            minimum_source_tm=min([r['source_tm'] for r in ok],default=0),stages={s:{k:sum(r[s][k] for r in ok) for k in ('coarse_valid','raw_gate_passed','connected','overlap_free','joint')} for s in ('source','projected')})
    native,cond,generated=(summary[k] for k in ('native_reference','native_cond','generated_cond'))
    gate=dict(native=native['stages']['projected']['joint']==4 and native['minimum_source_tm']>=.95,
        native_cond=cond['stages']['projected']['joint']>=14 and cond['mean_source_tm']>=.95,
        generated=generated['stages']['projected']['joint']>=12 and generated['mean_source_tm']>=.8)
    result=dict(status='complete',qualified=all(gate.values()),gate=gate,summary=summary,records=records,bounds=limits,sources=bound,
                designability_tested=False,seconds=time.monotonic()-start,predictions_sha256=sha(a.output/'predictions.h5'))
    (a.output/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    (root/'reports/kinematic_projection_profile_20261009.md').write_text('# Whole-chain bond projection: CPU diagnostic\n\n```json\n'+json.dumps(dict(gate=gate,summary=summary,bounds=limits),indent=2)+'\n```\n')
    print(json.dumps(dict(gate=gate,summary=summary)))


if __name__=='__main__':main()
