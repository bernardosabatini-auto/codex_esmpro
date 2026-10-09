"""CPU whole-chain graft diagnostic; all raw failures retained."""
import argparse,json,time
from pathlib import Path
import h5py,numpy as np,torch
from latentfold.anchor_kinematics import encode,decode
from latentfold.fragment_inpainting import place_fragment
from latentfold.backbone_sterics import steric_audit
from latentfold.metrics import usalign_coordinates
from fragment_validation_core import raw_rows
from fragment_junction_core import flank_bonds
from prepare_overfit import sha


def preserved(a,b,start,size):
    n=a['oxygen'].shape[1];known=torch.zeros(3*n,dtype=torch.bool);known[3*start:3*(start+size)]=True
    result={}
    for key,width in [('lengths',2),('angles',3),('torsions',4)]:
        editable=~known.unfold(0,width,1).all(-1);delta=b[key]-a[key]
        if key=='torsions':delta=torch.atan2(torch.sin(delta),torch.cos(delta))
        result[key]=float(delta[:,editable].abs().max()) if editable.any() else 0.
    mask=torch.ones(n,dtype=torch.bool);mask[start:start+size]=False
    result['oxygen']=float((a['oxygen'][:,mask]-b['oxygen'][:,mask]).abs().max())
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1]
    protocol=root/'configs/anchor_kinematics_profile_protocol.json';spec=json.loads(protocol.read_text());run=root/'runs'/spec['source_generation']
    mp=run/'manifest.json';m=json.loads(mp.read_text());c=m['config'];report=root/'reports'/(run.name+'.json');d=json.loads(report.read_text())
    if (m['status']!='complete' or d['status']!='complete' or d['manifest_sha256']!=sha(mp) or d['predictions_sha256']!=sha(run/'predictions.h5')):
        raise ValueError('Changed completed generation')
    rc=json.loads((root/'runs/context_retrieved_refold_20261009_0.json').read_text())
    if sha(rc['usalign'])!=rc['usalign_sha256']:raise ValueError('Changed scorer')
    selected=[next(r for r in c['selected'] if r['bucket']==b) for b in (128,256,384,512)]
    sources=[protocol,mp,report,run/'predictions.h5',Path(c['fragments']),Path(c['parent']['baseline_predictions']),Path(__file__),root/'src/latentfold/anchor_kinematics.py']
    bound=[dict(path=str(p.resolve()),sha256=sha(p)) for p in sources]
    a.output.mkdir(exist_ok=False);records=[];controls=[];start_time=time.monotonic();torch.set_num_threads(1)
    with h5py.File(c['fragments'],locking=False) as fr,h5py.File(c['parent']['baseline_predictions'],locking=False) as baseline,h5py.File(run/'predictions.h5',locking=False) as generated,h5py.File(a.output/'predictions.h5','x') as out:
        for row in selected:
            ident=row['id'];g=fr['train/'+ident];q=g['conditions/c20_center'];st=int(q.attrs['start']);fragment=torch.from_numpy(q['fragment'][:]).double()
            inputs=dict(native=g['reference_backbone'][:][None],parent6000=baseline['new/'+ident+'/backbone'][:],retrieved=generated['retrieved/'+ident+'/backbone'][:])
            for arm,array in inputs.items():
                x=torch.from_numpy(array).double();parameters=encode(x)
                rt=decode(parameters,x[:,st:st+20],st);fp=decode(encode(x.float()),x.float()[:,st:st+20],st)
                e64=float((rt-x).abs().max());e32=float((fp.double()-x).abs().max())
                if e64>1e-7 or e32>.005:raise ValueError('Representation roundtrip failed')
                anchors=place_fragment(fragment,x,st);y=decode(parameters,anchors[:,st:st+20],st)
                if not torch.equal(y[:,st:st+20],anchors[:,st:st+20]):raise ValueError('Known motif changed')
                invariants=preserved(parameters,encode(y),st,20)
                if max(invariants.values())>1e-7:raise ValueError('Unknown/cross-boundary internal geometry changed')
                controls.append(dict(target_id=ident,arm=arm,fp64_max_abs=e64,fp32_max_abs=e32,internal_errors=invariants,known_exact=True))
                out[arm+'/'+ident+'/source']=array;out[arm+'/'+ident+'/backbone']=y.numpy()
                for slot,(old,new) in enumerate(zip(array,y.numpy())):
                    def score(bb):
                        r=raw_rows(bb[None],q['fragment'][:],st,arm,ident,row['family'])[0]
                        r['flank_edges_valid']=flank_bonds(bb,st,20,8)['all_edges_valid']
                        r['nonlocal_backbone_overlaps']=steric_audit(bb,list(range(row['length'])))['pairs_below_threshold']
                        return r
                    records.append(dict(target_id=ident,arm=arm,slot=slot,bucket=row['bucket'],source=score(old),constructed=score(new),
                        source_tm=usalign_coordinates(rc['usalign'],new[:,1],old[:,1])))
            print('profiled',row['bucket'],flush=True)
    summaries=[]
    for arm in ('native','parent6000','retrieved'):
        rows=[r for r in records if r['arm']==arm]
        summaries.append(dict(arm=arm,samples=len(rows),mean_source_tm=float(np.mean([r['source_tm'] for r in rows])),
            stages={s:dict(coarse=sum(r[s]['coarse_valid'] for r in rows),raw=sum(r[s]['raw_gate_passed'] for r in rows),
                connected=sum(r[s]['flank_edges_valid'] for r in rows),overlap_free=sum(r[s]['nonlocal_backbone_overlaps']==0 for r in rows),
                joint=sum(r[s]['raw_gate_passed'] and r[s]['flank_edges_valid'] and r[s]['nonlocal_backbone_overlaps']==0 for r in rows)) for s in ('source','constructed')}))
    result=dict(status='complete',representation_roundtrip_qualified=True,designability_tested=False,sources=bound,records=records,controls=controls,
        summary=summaries,predictions_sha256=sha(a.output/'predictions.h5'),seconds=time.monotonic()-start_time)
    (a.output/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    (root/'reports'/('anchor_kinematics_profile_20261009.md')).write_text('# Whole-chain anchored kinematics: CPU diagnostic\n\nRepresentation tests only; no designability or learned-model claim.\n\n```json\n'+json.dumps(summaries,indent=2)+'\n```\n')
    print(json.dumps(summaries))


if __name__=='__main__':main()
