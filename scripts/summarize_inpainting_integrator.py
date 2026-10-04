"""Independent inventory, geometry, junction and oracle-path scoring."""
import argparse,json
from pathlib import Path
import h5py,numpy as np,torch
from inpainting_integrator_core import audit
from extra_fragment_validation_core import load_conditions
from fragment_validation_core import raw_rows
from latentfold.fragment_inpainting import place_fragment
from latentfold.ensemble_metrics import backbone_geometry
from audit_inpainting_junctions import junctions
from prepare_overfit import sha


def analyze(run):
    mp=run/'manifest.json';m=json.loads(mp.read_text()) if mp.exists() else dict(status='failed',error='Missing manifest')
    if m['status']!='complete':return dict(status=m['status'],error=m.get('error'))
    c=m['config'];spec,gc,source=audit(c);ids=[r['id'] for r in c['selected']]
    pose_ids={next(r['id'] for r in c['selected'] if r['bucket']==b) for b in (128,256,384,512)}
    wanted={(i,k) for i in ids for k in ('original_native','three_generated','three_native')}|{(i,'pose_'+a) for i in pose_ids for a in ('generated','native')}
    controls={(r['target_id'],r['kind']):r for r in m['controls']}
    if (m['training_updates_executed'] or len(m['controls'])!=104 or set(controls)!=wanted or len(m['timing'])!=128
        or m['model_initial']!=m['model_final'] or m['model_initial']!=source['evaluated_model_sha256']
        or m['original_initial']!=m['original_final'] or m['original_initial']!=source['frozen_original']
        or m['predictions_sha256']!=sha(run/'predictions.h5') or m['peak_reserved_GiB']>75):raise ValueError('Incomplete or mutated diagnostic')
    items=load_conditions(c['fragments'],ids,'c20_center',cohort='train');records=[];paths=[]
    with h5py.File(run/'predictions.h5') as f,h5py.File(c['source_predictions']) as prior,h5py.File(c['fragments']) as fr:
        if set(f)!={'noise','anchors','original_native','free','path'} or set(f['free'])!={'generated','native'} or set(f['path'])!={'trained','original_unmasked'}:raise ValueError('Changed diagnostic groups')
        if any(set(f[g])!=set(ids) for g in ('noise','original_native','anchors/generated','anchors/native')):raise ValueError('Missing explicit inputs')
        for kind in ('generated','native'):
            if set(f['free/'+kind])!={'3','10'} or any(set(f[f'free/{kind}/{s}'])!=set(ids) for s in (3,10)):raise ValueError('Changed free-sample inventory')
        for kind in ('trained','original_unmasked'):
            if set(f['path/'+kind])!={str(i) for i in range(4)} or any(set(f[f'path/{kind}/{i}'])!=set(ids) for i in range(4)):raise ValueError('Changed oracle-path inventory')
        for row in c['selected']:
            ident=row['id'];q=items[ident];n=q['length'];keep=q['keep'].numpy();noise=f['noise/'+ident][:]
            if noise.shape!=(4,4*n,3) or not np.isfinite(noise).all():raise ValueError('Invalid explicit noise')
            original=f['original_native/'+ident][:];error=float(np.max(abs(original-prior['native_direct/'+ident+'/backbone'][:])))
            if error>1e-5 or error!=controls[ident,'original_native']['max_abs']:raise ValueError('Original decoder replay changed')
            for kind,group in [('generated','parent'),('native','native_direct')]:
                reference=prior[group+'/'+ident+'/backbone'][:]
                anchors=place_fragment(torch.from_numpy(q['fragment']),torch.from_numpy(reference),q['start']).numpy()
                if not np.allclose(anchors,f['anchors/'+kind+'/'+ident][:],atol=1e-5,rtol=0):raise ValueError('Changed supplied-fragment placement')
                for steps in (3,10):
                    g=f[f'free/{kind}/{steps}/{ident}'];bb=g['backbone'][:]
                    if bb.shape!=(4,n,4,3) or not np.isfinite(bb).all() or np.max(abs(bb[:,keep]-anchors[:,keep]))>1e-4 or np.max(abs(bb.mean((1,2))))>1e-4:raise ValueError('Lost anchors or conditional center')
                    if steps==3:
                        error=float(np.max(abs(bb-prior[kind+'_cond/'+ident+'/backbone'][:])))
                        if error>1e-5 or error!=controls[ident,'three_'+kind]['max_abs']:raise ValueError('Three-step archive changed')
                    elif ident in pose_ids:
                        error=float(np.max(abs(bb-g['pose_backbone'][:])))
                        if error>1e-4 or error!=controls[ident,'pose_'+kind]['max_abs']:raise ValueError('Supplied pose affected prediction')
                    for k,r in enumerate(raw_rows(bb,q['fragment'],q['start'],kind,ident,q['family'])):
                        j=junctions(bb[k],q['start'],20)
                        records.append(dict(r,steps=steps,bucket=row['bucket'],junctions=j,connected_and_coarse=bool(j['valid'] and r['raw_gate_passed'])))
            target=fr['train/'+ident+'/reference_backbone'][:];target=target-target.mean((0,1),keepdims=True)
            for kind in ('trained','original_unmasked'):
                for index,t in enumerate(spec['probe_times']):
                    bb=f[f'path/{kind}/{index}/{ident}'][:]
                    if bb.shape!=(4,n,4,3) or not np.isfinite(bb).all() or np.max(abs(bb[:,keep]-target[None,keep]))>1e-4 or np.max(abs(bb.mean((1,2))))>1e-4:raise ValueError('Invalid oracle-path outputs')
                    geometry=backbone_geometry(bb)['coarse_valid']
                    for k in range(4):
                        j=junctions(bb[k],q['start'],20)
                        paths.append(dict(arm=kind,target_id=ident,slot=k,t=t,coarse_valid=bool(geometry[k]),junctions=j,
                            connected_and_coarse=bool(geometry[k] and j['valid']),
                            unknown_ca_rmsd=float(np.sqrt(np.square(bb[k,~keep,1]-target[~keep,1]).sum(-1).mean()))))
    if len(records)!=512 or len(paths)!=1024:raise ValueError('Changed diagnostic denominators')
    def summary(rows,**labels):
        return dict(**labels,samples=len(rows),valid=sum(r['coarse_valid'] for r in rows),
                    junction_intact=sum(r['junctions']['valid'] for r in rows),connected_and_coarse=sum(r['connected_and_coarse'] for r in rows),
                    mean_junction_cn=float(np.mean([x for r in rows for x in r['junctions']['peptide_distances']])))
    free=[summary([r for r in records if r['arm']==a and r['steps']==s],arm=a,steps=s) for a in ('generated','native') for s in (3,10)]
    probes=[]
    for a in ('trained','original_unmasked'):
        for t in spec['probe_times']:
            rr=[r for r in paths if r['arm']==a and r['t']==t]
            probes.append(dict(summary(rr,arm=a,t=t),mean_unknown_ca_rmsd=float(np.mean([r['unknown_ca_rmsd'] for r in rr]))))
    base,nextrow=[r for r in free if r['arm']=='generated']
    eligible=nextrow['connected_and_coarse']>=9 and nextrow['valid']>=45 and nextrow['connected_and_coarse']>base['connected_and_coarse']
    return dict(status='complete',manifest_sha256=sha(mp),predictions_sha256=m['predictions_sha256'],controls=len(controls),summary=free,path_summary=probes,
                ten_step_followup_eligible=eligible,records=records,path_records=paths,elapsed_seconds=m['elapsed_seconds'],peak_reserved_GiB=m['peak_reserved_GiB'],
                scope='Frozen training-only diagnostic. Motif coordinates are imposed. Oracle paths expose native endpoints and are not generation. No designability claim, refold pooling or parameter update.')


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();torch.set_num_threads(1)
    d=analyze(a.runs[0]);target=a.output.with_suffix('.json');tmp=target.with_suffix('.tmp');tmp.write_text(json.dumps(d,indent=2)+'\n');tmp.replace(target)
    visible={k:v for k,v in d.items() if k not in ('records','path_records')}
    a.output.with_suffix('.md').write_text('# Fixed-fragment integration diagnostic\n\n```json\n'+json.dumps(visible,indent=2)+'\n```\n');print(json.dumps(visible))


if __name__=='__main__':main()
