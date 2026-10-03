import argparse,json
from pathlib import Path
import h5py,numpy as np
from broad_fragment_pilot import audit,qualify
from generate_isolated_motif import canonical_fragment
from latentfold.metrics import ca_metrics
from latentfold.ensemble_metrics import backbone_geometry
from latentfold.fragment_designability import motif_fit
from prepare_overfit import sha


def analyze(run):
    path=run/'manifest.json';m=json.loads(path.read_text()) if path.exists() else dict(status='failed',error='Missing manifest')
    if m['status']!='complete':return dict(status=m['status'],error=m.get('error'),data_gate_passed=False)
    c=m['config'];rows=audit(c);spec=c['spec'];records=[];controls=[];seen=set()
    if m['training_updates_executed'] or m['peak_reserved_GiB']>spec['max_reserved_GiB'] or sha(run/'fragments.h5')!=m['fragments_sha256']:raise ValueError('Changed pilot output')
    with h5py.File(run/'fragments.h5') as out,h5py.File(c['cache']) as cache,h5py.File(c['historical_fragments']) as old,h5py.File(c['backbones']) as source:
        if set(out)!={'train','historical'} or set(out['train'])!={r['id'] for r in rows} or set(out['historical'])!=set(c['control_ids']):raise ValueError('Changed pilot inventory')
        for ident in c['control_ids']:controls.append(dict(kind='historical',target_id=ident,latent_max_abs=float(np.max(abs(out['historical/'+ident][:]-old['development/'+ident+'/conditions/f30_center/latent'][:])))))
        for row in rows:
            ident=row['id'];g=out['train/'+ident];bb=g['reference_backbone'][:];decoded=g['roundtrip'][:];z=cache['train/'+ident+'/z'][:]
            if not np.array_equal(g['reference_z'][:],z) or ca_metrics(bb[:,1],source[ident+'/backbone'][:,1])['ca_rmsd']>.001:raise ValueError('Changed full source or target')
            record=dict(target_id=ident,length=row['length'],bucket=row['bucket'],source_ca_error=float(np.sqrt(np.mean(np.sum((bb[:,1]-cache['train/'+ident+'/ca_coords'][:])**2,-1)))),full_encoding_rmse=float(np.sqrt(np.mean((g['encoded_z'][:]-z)**2))),source_valid=bool(backbone_geometry(bb[None])['coarse_valid'][0]),decoded_valid=bool(backbone_geometry(decoded[None])['coarse_valid'][0]),decoded_ca_rmsd=ca_metrics(decoded[:,1],bb[:,1])['ca_rmsd'],fragments=[])
            if row['bucket'] not in seen:controls.append(dict(kind='repeat',target_id=ident,**ca_metrics(g['repeat'][:,1],decoded[:,1])));seen.add(row['bucket'])
            names={f'f{round(f*100)}_{p}' for f in spec['fractions'] for p in spec['positions']}
            if set(g['conditions'])!=names:raise ValueError('Changed nine-condition inventory')
            for fraction in spec['fractions']:
                k=max(8,int(fraction*len(bb)))
                for position,start in [('left',0),('center',(len(bb)-k)//2),('right',len(bb)-k)]:
                    name=f'f{round(fraction*100)}_{position}';q=g['conditions/'+name];fragment,_=canonical_fragment(bb[start:start+k].astype(np.float64))
                    if not np.array_equal(q['fragment'][:],fragment) or q.attrs['start']!=start or q.attrs['sequence']!=row['sequence'][start:start+k]:raise ValueError('Crop isolation failed')
                    record['fragments'].append(dict(condition=name,**motif_fit(q['roundtrip'][:],fragment,0)))
                    if name=='f30_center':controls.append(dict(kind='pose',target_id=ident,coordinate_max_abs=float(np.max(abs(q['pose_fragment'][:]-fragment))),latent_max_abs=float(np.max(abs(q['pose_latent'][:]-q['latent'][:])))))
            archived=next(r for r in m['records'] if r['target_id']==ident)
            if any(abs(record[k]-archived[k])>1e-5 for k in ('source_ca_error','full_encoding_rmse','decoded_ca_rmsd')) or record['fragments']!=archived['fragments']:raise ValueError('Changed recorded evidence')
            records.append(record)
    result=qualify(records,controls,spec)
    if any(m[k]!=v for k,v in result.items()):raise ValueError('Changed pilot qualification')
    return dict(status='complete',manifest_sha256=sha(path),fragments_sha256=m['fragments_sha256'],**result,proteins=64,fragments=576,controls=72,peak_reserved_GiB=m['peak_reserved_GiB'],elapsed_seconds=m['elapsed_seconds'],records=records,scope=spec['scope'])


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();d=analyze(a.runs[0]);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('# Broader fragment-data feasibility\n\n```json\n'+json.dumps({k:v for k,v in d.items() if k!='records'},indent=2)+'\n```\n')

if __name__=='__main__':main()
