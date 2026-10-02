"""Audit every isolated conditioning fragment and unchanged cached target."""
import argparse,json
from pathlib import Path
import h5py,numpy as np,torch
from prepare_overfit import sha
from generate_isolated_motif import canonical_fragment
from generate_generative_pilot import motif_error
from latentfold.fragment_conditioning import fragment_features


def analyze(run):
    path=run/'manifest.json';m=json.loads(path.read_text()) if path.exists() else dict(status='failed',error='Missing manifest')
    if m['status']!='complete':return dict(status=m['status'],error=m.get('error','Incomplete'))
    c=m['config']
    for key in ('protocol','training_manifest','training_labels','development_manifest','development_predictions','selection','decoder_checkpoint'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed '+key)
    if sha(run/'fragments.h5')!=m['fragments_sha256'] or len(m['records'])!=288 or len(m['controls'])!=32 or len(m['development'])!=16:raise ValueError('Incomplete data audit')
    expected_controls={r['id'] for r in c['training_targets']}
    if {r['target_id'] for r in m['controls']}!=expected_controls or any(r['coordinate_max_abs']>1e-4 or r['latent_rmse']>1e-4 for r in m['controls']):raise ValueError('Failed pose controls')
    records=[]
    with h5py.File(run/'fragments.h5') as f,h5py.File(c['training_labels']) as src,h5py.File(c['development_predictions']) as dev:
        if set(f)!= {'train','development'} or set(f['train'])!=expected_controls or set(f['development'])!={r['target_id'] for r in c['development_rows']}:raise ValueError('Unexpected corpus coverage')
        for row in c['training_targets']:
            ident=row['id'];g=f['train/'+ident];bb=src[ident+'/reference_backbone'][:];n=len(bb)
            if not np.array_equal(g['reference_backbone'][:],bb) or not np.array_equal(g['reference_z'][:],src[ident+'/reference_z'][:]):raise ValueError('Cached full targets changed')
            expected=set()
            for fraction in (.2,.3,.4):
                k=max(8,int(fraction*n))
                for pos,st in [('left',0),('center',(n-k)//2),('right',n-k)]:
                    name=f'f{round(fraction*100)}_{pos}';expected.add(name);q=g['conditions/'+name];fragment,_=canonical_fragment(bb[st:st+k].copy());z=q['latent'][:];seq=row['sequence'][st:st+k]
                    if q.attrs['start']!=st or q.attrs['sequence']!=seq or not np.array_equal(q['fragment'][:],fragment) or z.shape!=(k,8) or not np.isfinite(z).all():raise ValueError('Fragment conditioning changed')
                    features,keep=fragment_features(torch.from_numpy(z),seq,length=n,start=st)
                    if (features[~keep]!=0).any():raise ValueError('Scaffold leakage')
                    error=float(motif_error(q['roundtrip'][:][None],fragment,np.ones(k,bool))[0]);old=next(r for r in m['records'] if (r['target_id'],r['condition'])==(ident,name))
                    if not np.isfinite(error) or abs(error-old['roundtrip_drms'])>1e-7:raise ValueError('Fragment roundtrip audit failed')
                    records.append(error)
            if set(g['conditions'])!=expected:raise ValueError('Wrong fragment inventory')
        for row in c['development_rows']:
            ident=row['target_id'];n=row['length'];k=max(8,int(.3*n));st=(n-k)//2;q=f['development/'+ident+'/conditions/f30_center']
            if q.attrs['start']!=st or q.attrs['sequence']!=row['sequence'][st:st+k]:raise ValueError('Development fragment sequence/position changed')
            for key,old in [('fragment','fragment'),('latent','fragment_latent'),('roundtrip','fragment_roundtrip')]:
                if not np.array_equal(q[key][:],dev[ident+'/'+old][:]):raise ValueError('Existing isolated-fragment arrays changed')
    fraction=float(np.mean(np.asarray(records)<=.5))
    if m['training_gate_passed']!=(fraction>=.9):raise ValueError('Data gate mismatch')
    return dict(status='complete',training_gate_passed=fraction>=.9,training_proteins=32,training_fragments=288,development_fragments=16,mean_fragment_roundtrip_drms=float(np.mean(records)),maximum_fragment_roundtrip_drms=float(np.max(records)),fraction_under_half_A=fraction,pose_controls=32,elapsed_seconds=m['elapsed_seconds'],peak_reserved_GiB=m['peak_reserved_GiB'],manifest_sha256=sha(path),fragments_sha256=m['fragments_sha256'])


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();d=analyze(a.runs[0]);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n')
    lines=['# Isolated-fragment conditioning data','',f"Status: {d['status']}.",'','Full-chain training targets and standalone fragment inputs are separate. No scaffold sequence or full-context motif codes enter the conditioner. No training, model-quality or designability claim.','',json.dumps(d,indent=2)];a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
