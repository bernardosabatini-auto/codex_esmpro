"""Audit reconstruction scores before testing their measured-designability signal."""
import argparse,json
from pathlib import Path
import h5py,numpy as np
from latentfold.metrics import ca_metrics
from generate_generative_pilot import motif_error
from prepare_roundtrip_designability import audit_sources
from prepare_overfit import sha


def auc(labels,scores):
    y=np.asarray(labels,bool);s=np.asarray(scores,float)
    if y.shape!=s.shape or y.ndim!=1 or not np.isfinite(s).all():raise ValueError('Finite matched labels/scores required')
    positive,negative=s[y],s[~y]
    if not len(positive) or not len(negative):return None
    d=positive[:,None]-negative[None,:]
    return float(np.mean((d>0)+.5*(d==0)))


def discriminate(rows):
    if not rows:return dict(backbones=0,families=0,designable=0,pooled_auc=None,family_bootstrap_ci95=None,bootstrap_defined_draws=0,mixed_label_families=0,within_family_auc=None)
    families=sorted({r['family'] for r in rows});groups=[[r for r in rows if r['family']==f] for f in families];score=lambda rr:auc([r['designable'] for r in rr],[-r['mean_ca_rmsd'] for r in rr]);value=score(rows);within=[score(g) for g in groups];mixed=[v for v in within if v is not None];rng=np.random.default_rng(2026100244);samples=[]
    for indices in rng.integers(0,len(groups),(2000,len(groups))):
        x=score([r for i in indices for r in groups[i]])
        if x is not None:samples.append(x)
    return dict(backbones=len(rows),families=len(families),designable=sum(r['designable'] for r in rows),pooled_auc=value,family_bootstrap_ci95=np.quantile(samples,[.025,.975]).tolist() if samples else None,bootstrap_defined_draws=len(samples),mixed_label_families=len(mixed),within_family_auc=float(np.mean(mixed)) if mixed else None)


def analyze(run):
    path=run/'manifest.json';m=json.loads(path.read_text()) if path.exists() else dict(status='failed',error='Missing manifest')
    if m['status']!='complete':return dict(status=m['status'],error=m.get('error'),exploratory_followup_qualified=False)
    c=m['config'];audit_sources(c);index={(r['name'],r['sample_index']):r for r in m['records']};expected={(r['name'],k) for r in c['entries'] for k in range(2)}
    if len(m['records'])!=152 or set(index)!=expected or len(m['controls'])!=4 or {r['name'] for r in m['controls']}!=set(c['control_names']) or any(r['coordinate_max_abs']>1e-4 or r['latent_rmse']>1e-4 for r in m['controls']):raise ValueError('Missing samples or failed controls')
    rows=[]
    with h5py.File(c['inputs']) as inp,h5py.File(run/'roundtrips.h5') as out:
        if set(out)!={r['name'] for r in c['entries']}:raise ValueError('Changed reconstruction inventory')
        for r in c['entries']:
            raw=inp[r['name']][:];values=[]
            if set(out[r['name']])!={'0','1'}:raise ValueError('Incomplete decoder seeds')
            for k in range(2):
                bb=out[r['name']+'/'+str(k)][:]
                if bb.shape!=raw.shape or not np.isfinite(bb).all():raise ValueError('Invalid reconstruction')
                metrics=ca_metrics(bb[:,1],raw[:,1]);metrics['distance_rms']=float(motif_error(bb[None],raw,np.ones(len(raw),bool))[0]);old=index[r['name'],k]
                if any(abs(old[key]-value)>1e-6 for key,value in metrics.items()):raise ValueError('Reconstruction score mismatch')
                values.append(metrics)
            rows.append(dict(**r,mean_ca_rmsd=float(np.mean([v['ca_rmsd'] for v in values])),mean_distance_rms=float(np.mean([v['distance_rms'] for v in values]))))
    native=[r for r in rows if r['cohort'].endswith('_native')];native_ok=sum(r['mean_ca_rmsd']<=1 for r in native);summaries={cohort:discriminate([r for r in rows if r['cohort']==cohort and r['raw_valid']]) for cohort in ['training','development']};qualified=native_ok>=10 and all(s['pooled_auc'] is not None and s['pooled_auc']>=.7 and s['within_family_auc'] is not None and s['within_family_auc']>=.7 and s['mixed_label_families']>=3 for s in summaries.values())
    return dict(status='complete',manifest_sha256=sha(path),roundtrips_sha256=sha(run/'roundtrips.h5'),reconstructions=152,native_controls=len(native),native_controls_under_1A=native_ok,summaries=summaries,exploratory_followup_qualified=bool(qualified),interpretation='Existing-label exploratory diagnostic. Native controls excluded; predictive analyses use generated coarse-valid backbones. A pass would require fresh training-family refold validation before proxy optimization. No motif success inferred.',records=rows,elapsed_seconds=m['elapsed_seconds'],measurement_seconds=sum(r['seconds'] for r in m['timings']),peak_reserved_GiB=m['peak_reserved_GiB'])


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();d=analyze(a.runs[0]);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('# Reconstruction consistency versus measured designability\n\n```json\n'+json.dumps({k:v for k,v in d.items() if k!='records'},indent=2)+'\n```\n')

if __name__=='__main__':main()
