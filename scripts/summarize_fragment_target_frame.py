"""Audit new supervision and exact preservation of all original input arrays."""
import argparse,json
from pathlib import Path
import h5py,numpy as np
from latentfold.metrics import ca_metrics
from latentfold.ensemble_metrics import backbone_geometry
from prepare_overfit import sha


def analyze(run):
    path=run/'manifest.json';m=json.loads(path.read_text()) if path.exists() else dict(status='failed',error='Missing manifest')
    if m['status']!='complete':return dict(status=m['status'],error=m.get('error'),training_gate_passed=False)
    c=m['config']
    for key in ('protocol','probe_report','probe_manifest','parent_manifest','base_fragments','decoder_checkpoint'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed target source')
    if sha(run/'fragments.h5')!=m['fragments_sha256']:raise ValueError('Changed target data')
    for key,tolerance in [('controls',1e-4),('encoding_controls',.05)]:
        if len(m[key])!=32 or len({r['target_id'] for r in m[key]})!=32 or any(not np.isfinite(r['latent_rmse']) or r['latent_rmse']>tolerance or r.get('coordinate_max_abs',0)>1e-4 for r in m[key]):raise ValueError('Failed target controls')
    index={(r['target_id'],r['condition']):r for r in m['records']};copied=0;qualified=0
    with h5py.File(c['base_fragments']) as old,h5py.File(run/'fragments.h5') as new:
        def check(name,obj):
            nonlocal copied
            other=new[name]
            if dict(obj.attrs)!=dict(other.attrs):raise ValueError('Changed original attributes')
            if isinstance(obj,h5py.Dataset):
                if not np.array_equal(obj[:],other[:]):raise ValueError('Changed original input array')
                copied+=1
        old.visititems(check)
        if set(new)!=set(old) or set(new['train'])!=set(old['train']) or set(new['development'])!=set(old['development']):raise ValueError('Changed corpus')
        wanted={(i,k) for i in old['train'] for k in old['train/'+i+'/conditions']}
        if len(m['records'])!=288 or set(index)!=wanted:raise ValueError('Incomplete conditional target inventory')
        for ident,condition in sorted(wanted):
            q=new['train/'+ident+'/conditions/'+condition];original=old['train/'+ident];z=q['target_latent'][:];bb=q['target_roundtrip'][:];raw=original['reference_backbone'][:]
            if z.shape!=original['reference_z'].shape or bb.shape!=raw.shape or not np.isfinite(z).all() or not np.isfinite(bb).all():raise ValueError('Invalid added target')
            actual=dict(coarse_valid=bool(backbone_geometry(bb[None])['coarse_valid'][0]),**ca_metrics(bb[:,1],raw[:,1]));row=index[ident,condition]
            if any(abs(row[key]-value)>1e-6 for key,value in actual.items()):raise ValueError('Target score mismatch')
            qualified+=int(actual['coarse_valid'] and actual['ca_rmsd']<=.5)
    return dict(status='complete',manifest_sha256=sha(path),fragments_sha256=m['fragments_sha256'],copied_arrays_bitwise_identical=copied,training_proteins=32,conditional_targets=288,valid_reconstruction_under_half_A=qualified,training_gate_passed=qualified/288>=.95,elapsed_seconds=m['elapsed_seconds'],peak_reserved_GiB=m['peak_reserved_GiB'])


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();d=analyze(a.runs[0]);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('# Fragment-anchored training targets\n\nAll original inputs and cached null targets preserved; new full-context codes are supervision only.\n\n```json\n'+json.dumps(d,indent=2)+'\n```\n')

if __name__=='__main__':main()
