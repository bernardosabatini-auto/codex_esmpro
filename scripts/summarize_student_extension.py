"""Score all extended draws and verify every previously published coverage prefix."""
import argparse,json
from pathlib import Path
import h5py,numpy as np
from prepare_overfit import sha
from score_ensemble_states import state_definition
from latentfold.metrics import ca_metrics
from latentfold.ensemble_metrics import backbone_geometry
from latentfold.teacher_states import paired_change

COUNTS=(1,4,16,32,64,128)


def validate_batches(batches, ids):
    expected={(i,k) for i in ids for k in range(0,128,32)}
    if len(batches)!=len(expected) or {(r['target_id'],r['offset']) for r in batches}!=expected:raise ValueError('incomplete generation timing')
    if any(not np.isfinite(r[k]) or r[k]<=0 for r in batches for k in ('seconds','peak_reserved_bytes')):raise ValueError('invalid timing/memory values')


def hit_summary(assignments, labels, counts=COUNTS):
    states=set(labels)
    if not counts or min(counts)<1 or max(counts)>len(assignments):raise ValueError('incomplete assignment prefix')
    if len(states)!=2:raise ValueError('expected two frozen reference states')
    if any(x is not None and x not in states for x in assignments):raise ValueError('unknown assignment')
    coverage={str(k):len(set(x for x in assignments[:k] if x is not None))/len(states) for k in counts}
    first={str(s):next((k+1 for k,v in enumerate(assignments) if v==s),None) for s in sorted(states)}
    return coverage,first


def analyze(m, predictions):
    c=m['config']
    for field in ('panel','protocol','base_scores','teacher_scores'):
        if sha(c[field])!=c[field+'_sha256']:raise ValueError('changed '+field)
    if c['samples']!=128 or c['sample_batch']!=32 or len(c['target_ids'])!=16:raise ValueError('wrong extension scope')
    if set(m['targets'])!=set(c['target_ids']) or len(m['targets'])!=16 or len(m['controls'])!=16 or {r['target_id'] for r in m['controls']}!=set(c['target_ids']):raise ValueError('incomplete targets/prefix controls')
    if any(not np.isfinite(r[k]) for r in m['controls'] for k in ('max_ca_rmsd','min_ca_lddt')) or any(r['max_ca_rmsd']>.2 or r['min_ca_lddt']<.99 or not r['validity_identical'] for r in m['controls']):raise ValueError('prefix controls failed')
    validate_batches(m['batches'],c['target_ids'])
    parent=json.loads(Path(c['base_scores']).read_text());teacher=json.loads(Path(c['teacher_scores']).read_text())
    parents={r['target_id']:r for r in parent['rows'] if r['setting']==c['setting'] and 'coverage' in r}
    teachers={r['target_id']:r for r in teacher['rows'] if r['setting']=='steps50' and 'coverage' in r}
    if parent['status']!='complete' or teacher['status']!='complete' or set(parents)!=set(c['target_ids']) or set(teachers)!=set(parents):raise ValueError('incomplete frozen comparisons')
    panel={r['query_id']:r for r in json.loads(Path(c['panel']).read_text())['development']}
    d=dict(status='complete',name=c['name'],rows=[],definitions={},prefix_scores_identical=True)
    with h5py.File(predictions) as h:
        if set(h)!=set(parents):raise ValueError('prediction target mismatch')
        for ident in sorted(h):
            row=panel[ident];bb=h[ident]['backbone'][:]
            if bb.shape!=(128,row['length'],4,3) or not np.isfinite(bb).all():raise ValueError('missing or invalid draws')
            expected=np.stack((np.arange(128),np.zeros(128,dtype=int)),axis=1)
            if not np.array_equal(h[ident]['seed_indices'][:],expected):raise ValueError('noise indices changed')
            positions,refs,i,j,features,labels=state_definition(row)
            definition=dict(variable_contacts=len(i),reference_states=len(set(labels)) if len(i) else 0,reference_cluster_labels=labels)
            if definition!=parent['definitions'][ident] or definition!=teacher['definitions'][ident]:raise ValueError('reference state definition changed')
            valid=np.concatenate([backbone_geometry(bb[k:k+32])['coarse_valid'] for k in range(0,128,32)])
            ca=bb[:,positions,1];quality=np.array([[ca_metrics(x,y)['ca_lddt'] for y in refs] for x in ca]).max(1)
            f=np.linalg.norm(ca[:,i]-ca[:,j],axis=-1);error=np.sqrt(np.mean((f[:,None]-features[None])**2,axis=-1));nearest=error.argmin(1);best=error[np.arange(128),nearest]
            r=dict(target_id=ident,family=row['family'],coverage={},first_state_hit={},valid_fraction={str(k):float(valid[:k].mean()) for k in COUNTS},oracle_ca_lddt={str(k):float(quality[:k].mean()) for k in COUNTS})
            for threshold in (1.,2.,3.):
                good=(best<=threshold)&(quality>=.8)&valid;assignments=[labels[n] if ok else None for n,ok in zip(nearest,good)]
                coverage,first=hit_summary(assignments,labels)
                if any(coverage[str(k)]!=parents[ident]['coverage'][str(threshold)][str(k)] for k in (1,4,16,32)):raise ValueError('frozen coverage prefix changed')
                r['coverage'][str(threshold)]=coverage;r['first_state_hit'][str(threshold)]=first
            d['rows'].append(r);d['definitions'][ident]=definition
    families={r['target_id']:r['family'] for r in d['rows']}
    if len(set(families.values()))!=16:raise ValueError('not16 separate families')
    values=lambda key,k:{r['target_id']:(r['coverage']['2.0'][str(k)] if key=='coverage' else float(r['coverage']['2.0'][str(k)]==1.) if key=='both_states' else r[key][str(k)]) for r in d['rows']}
    d['curves']={str(k):{key:float(np.mean(list(values(key,k).values()))) for key in ('coverage','both_states','valid_fraction','oracle_ca_lddt')} for k in COUNTS}
    d['extension_effects']={key:paired_change(values(key,128),values(key,32),families=families) for key in ('coverage','both_states','valid_fraction','oracle_ca_lddt')}
    d['versus_teacher128']={key:paired_change(values(key,128),{i:r['coverage']['2.0']['128'] if key=='coverage' else float(r['coverage']['2.0']['128']==1.) for i,r in teachers.items()},families=families) for key in ('coverage','both_states')}
    d['generation_seconds']=sum(r['seconds'] for r in m['batches']);d['max_reserved_gib']=max(r['peak_reserved_bytes'] for r in m['batches'])/1024**3
    return d


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--runs',type=Path,nargs='+',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();run=a.runs[0];path=run/'manifest.json'
    m=json.loads(path.read_text()) if path.exists() else dict(status='failed',error='Missing manifest')
    d=analyze(m,run/'predictions.h5') if m['status']=='complete' else dict(status=m['status'],error=m.get('error','Incomplete extension'))
    d['manifest_sha256']=sha(path) if path.exists() else None
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n')
    lines=['# Student128-sample extension','',f"Status: {d['status']}; pipeline: {d.get('name')}.",'','All16 frozen two-state development families. Original first32 coverage prefixes must match at1/2/3A. All samples retained; fixed decoder noise and varied latent noise. This diagnoses observed state reachability, not thermodynamic populations or model promotion.','','| K | Mean coverage | Families hitting both states | Valid fraction | Oracle CA-lDDT |','|---|---:|---:|---:|---:|']
    for k,r in d.get('curves',{}).items():lines.append(f"| {k} | {r['coverage']:.5f} | {round(16*r['both_states'])}/16 | {r['valid_fraction']:.5f} | {r['oracle_ca_lddt']:.5f} |")
    for key,r in d.get('extension_effects',{}).items():lines+=['',f"128 minus32 {key}: {r['difference']:+.5f},95% paired-family interval{r['ci95']}."]
    for key,r in d.get('versus_teacher128',{}).items():lines+=['',f"Student128 minus teacher128 {key}: {r['difference']:+.5f},95% paired-family interval{r['ci95']}."]
    if 'generation_seconds' in d:lines+=['',f"Cached-conditioner generation{d['generation_seconds']:.2f}s for16×128 samples; peak reserved{d['max_reserved_gib']:.2f}GiB. Excludes ESMC, loading, prefix controls and disk I/O; no end-to-end speed claim."]
    if 'error' in d:lines+=['',d['error']]
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
