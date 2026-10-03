import argparse,json
from pathlib import Path
import h5py,numpy as np
from broad_fragment_full_core import audit,crops,gates,verify_original
from latentfold.ensemble_metrics import backbone_geometry
from latentfold.metrics import ca_metrics
from latentfold.fragment_designability import motif_fit
from prepare_overfit import sha


def analyze(run):
    path=run/'manifest.json';m=json.loads(path.read_text()) if path.exists() else dict(status='failed',error='Missing manifest')
    if m['status']!='complete':return dict(status=m['status'],error=m.get('error'),data_gate_passed=False)
    c=m['config'];new,base,history=audit(c);rows=[dict(r,base=False) for r in new]+[dict(r,base=True) for r in base];controls=[];records=[];control_ids={next(r['id'] for r in new if r['bucket']==b) for b in (128,256,384,512)}
    if m['training_updates_executed'] or sha(run/'fragments.h5')!=m['fragments_sha256'] or len(m['records'])!=2048 or len(m['controls'])!=16 or max(r['peak_reserved_GiB'] for r in m['batches'])>75:raise ValueError('Changed full-data output')
    archived={r['target_id']:r for r in m['records']}
    with h5py.File(run/'fragments.h5') as out,h5py.File(c['base_fragments']) as old,h5py.File(c['cache']) as cache,h5py.File(c['source_backbones']) as source:
        if set(out)!={'train','rejected','historical'} or set(out['train'])&set(out['rejected']) or set(out['train'])|set(out['rejected'])!={r['id'] for r in rows} or set(out['historical'])!=set(history):raise ValueError('Changed source inventory')
        for ident in history:
            error=float(np.max(abs(out['historical/'+ident][:]-old['development/'+ident+'/conditions/f30_center/latent'][:])));controls.append(dict(kind='historical',target_id=ident,latent_max_abs=error))
            if not np.isfinite(error) or error>1e-5:raise ValueError('Historical code failed')
        for row in rows:
            ident=row['id'];retained=ident in out['train'];g=out[('train/' if retained else 'rejected/')+ident];bb=g['reference_backbone'][:];record=dict(target_id=ident,base=row['base'],length=row['length'],bucket=row['bucket'],source_ca_error=None,source_valid=bool(backbone_geometry(bb[None])['coarse_valid'][0]),conditions=[])
            if row['base']:
                if not retained:raise ValueError('Original protein dropped')
                verify_original(old['train/'+ident],g);record['qualified']=True
            else:
                z=cache['train/'+ident+'/z'][:];ca=cache['train/'+ident+'/ca_coords'][:];error=float(np.sqrt(np.mean(np.sum((bb[:,1]-ca)**2,-1))));parity=float(np.sqrt(np.mean((g['encoded_z'][:]-z)**2)));decoded=g['roundtrip'][:];valid=bool(backbone_geometry(decoded[None])['coarse_valid'][0]);rmsd=ca_metrics(decoded[:,1],bb[:,1])['ca_rmsd'];qualified=record['source_valid'] and valid and rmsd<=1
                if error>.02 or parity>.05 or not np.isfinite([error,parity,rmsd]).all() or not np.array_equal(g['reference_z'][:],z) or ca_metrics(bb[:,1],source[ident+'/backbone'][:,1])['ca_rmsd']>.001 or retained!=qualified:raise ValueError('Changed source/target qualification')
                record.update(source_ca_error=error,full_encoding_rmse=parity,decoded_valid=valid,decoded_ca_rmsd=rmsd,qualified=qualified)
                if ident in control_ids:
                    check=g['singleton_backbone'][:];metric=ca_metrics(check[:,1],decoded[:,1]);delta=float(np.max(abs(g['singleton_encoded'][:]-g['encoded_z'][:])));same=bool(record['source_valid'] and backbone_geometry(check[None])['coarse_valid'][0] and ca_metrics(check[:,1],bb[:,1])['ca_rmsd']<=1)==qualified;controls.append(dict(kind='singleton',target_id=ident,latent_max_abs=delta,same_qualification=same,**metric))
                    if delta>1e-4 or metric['ca_rmsd']>.01 or metric['ca_lddt']<.999 or not same:raise ValueError('Singleton control failed')
            qs=crops(bb,row['sequence'],short_only=row['base'])
            if not row['base'] and set(g['conditions'])!={q['name'] for q in qs}:raise ValueError('Changed twelve-condition inventory')
            for q in qs:
                v=g['conditions/'+q['name']]
                if v.attrs['start']!=q['start'] or v.attrs['sequence']!=q['sequence'] or not np.array_equal(v['fragment'][:],q['fragment']) or v['latent'].shape!=(len(q['fragment']),8) or not np.isfinite(v['latent'][:]).all():raise ValueError('Changed isolated condition')
                record['conditions'].append(dict(name=q['name'],**motif_fit(v['roundtrip'][:],q['fragment'],0)))
                if ident in control_ids and q['name'] in ('f30_center','c20_center'):
                    coordinate=float(np.max(abs(v['pose_fragment'][:]-q['fragment'])));delta=float(np.max(abs(v['pose_latent'][:]-v['latent'][:])));controls.append(dict(kind='pose',target_id=ident,condition=q['name'],coordinate_max_abs=coordinate,latent_max_abs=delta))
                    if coordinate>1e-4 or delta>1e-4:raise ValueError('Pose control failed')
            previous=archived[ident]
            if record['conditions']!=previous['conditions'] or record['qualified']!=previous['qualified'] or any(abs(record[k]-previous[k])>1e-5 for k in ('source_ca_error','full_encoding_rmse','decoded_ca_rmsd') if record.get(k) is not None):raise ValueError('Changed stored data evidence')
            records.append(record)
    if len(controls)!=16:raise ValueError('Missing audited controls')
    result=gates(records)
    if any(m[k]!=v for k,v in result.items()):raise ValueError('Changed data gate')
    return dict(status='complete',manifest_sha256=sha(path),fragments_sha256=m['fragments_sha256'],partition=c['partition'],**result,controls=16,preserved_base_proteins=128,peak_reserved_GiB=max(r['peak_reserved_GiB'] for r in m['batches']),elapsed_seconds=m['elapsed_seconds'],records=records,scope='Every frozen candidate retained in the ledger. Only qualified new full endpoints enter training; all original inputs retained unchanged with three additive short crops. Fragment failures remain visible. No teacher labels or model training.')


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();d=analyze(a.runs[0]);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('# Broader isolated-fragment data\n\n```json\n'+json.dumps({k:v for k,v in d.items() if k!='records'},indent=2)+'\n```\n')

if __name__=='__main__':main()
