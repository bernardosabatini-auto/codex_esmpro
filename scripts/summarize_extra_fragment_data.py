import argparse,json
from pathlib import Path
import h5py,numpy as np
from extra_fragment_data import audit_config,crop_condition
from latentfold.fragment_designability import motif_fit
from prepare_overfit import sha


def analyze(run):
    path=run/'manifest.json';m=json.loads(path.read_text()) if path.exists() else dict(status='failed',error='Missing manifest')
    if m['status']!='complete':return dict(status=m['status'],error=m.get('error'),generation_gate_passed=False)
    c=m['config'];selection=audit_config(c);rows={r['target_id']:r for r in selection['selected']};scores=[]
    if m['training_updates_executed'] or m['peak_reserved_GiB']>75 or sha(run/'fragments.h5')!=m['fragments_sha256']:raise ValueError('Changed encoding output')
    wanted={('historical',i) for i in c['control_ids']}|{('pose',i) for i in c['target_ids']}
    if len(m['controls'])!=68 or {(r['kind'],r['target_id']) for r in m['controls']}!=wanted or len(m['records'])!=64:raise ValueError('Missing encoding controls')
    with h5py.File(c['backbones']) as src,h5py.File(run/'fragments.h5') as out,h5py.File(c['historical_fragments']) as old:
        if set(out)!=set(('train','development','references','historical')) or len(out['train']) or set(out['development'])!=set(c['target_ids']) or set(out['references'])!=set(c['target_ids']) or set(out['historical'])!=set(c['control_ids']):raise ValueError('Changed cohort inventory')
        for ident in c['control_ids']:
            if np.max(abs(out['historical/'+ident+'/latent'][:]-old['development/'+ident+'/conditions/f30_center/latent'][:]))>1e-5:raise ValueError('Historical latent control failed')
        for ident in c['target_ids']:
            bb=src[ident+'/backbone'][:];st,seq,fragment,_=crop_condition(bb,rows[ident]['sequence']);g=out['development/'+ident];q=g['conditions/f30_center']
            if g.attrs['length']!=len(bb) or g.attrs['family']!=rows[ident]['family'] or set(g['conditions'])!={'f30_center'} or q.attrs['start']!=st or q.attrs['sequence']!=seq or not np.array_equal(q['fragment'][:],fragment) or not np.array_equal(out['references/'+ident+'/backbone'][:],bb):raise ValueError('Changed crop or source backbone')
            z=q['latent'][:]
            if z.shape!=(len(fragment),8) or not np.isfinite(z).all() or np.max(abs(q['pose_fragment'][:]-fragment))>1e-4 or np.max(abs(q['pose_latent'][:]-z))>1e-4:raise ValueError('Invalid fragment representation or pose control')
            fit=motif_fit(q['roundtrip'][:],fragment,0);record=next(r for r in m['records'] if r['target_id']==ident)
            if any(abs(fit[k]-record[k])>1e-5 for k in fit):raise ValueError('Changed roundtrip evidence')
            scores.append(dict(target_id=ident,**fit,qualified=fit['motif_ca_rmsd']<=.5 and fit['motif_drms']<=.5))
    qualified=sum(r['qualified'] for r in scores)
    return dict(status='complete',manifest_sha256=sha(path),fragments_sha256=m['fragments_sha256'],generation_gate_passed=qualified/64>=.9,fragments=64,controls=68,qualified_fragment_roundtrips=qualified,peak_reserved_GiB=m['peak_reserved_GiB'],elapsed_seconds=m['elapsed_seconds'],records=scores,scope=c['spec']['scope']+' Every selected family is retained, including any poor roundtrip.')


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();d=analyze(a.runs[0]);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('# Additional experimental isolated fragments\n\n```json\n'+json.dumps({k:v for k,v in d.items() if k!='records'},indent=2)+'\n```\n')

if __name__=='__main__':main()
