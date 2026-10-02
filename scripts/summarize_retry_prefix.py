"""Report every equivalence failure in the unchanged original-model diagnostic."""
import argparse,json,math
from pathlib import Path
from prepare_overfit import sha


def analyze(m):
    if m['status']!='complete':return dict(status=m['status'],error=m.get('error','Incomplete'))
    c=m['config'];ids=c['target_ids'];wanted={(i,k,n) for i in ids for k in ('cached_vs_reference','online_vs_reference','online_vs_cached') for n in (1,8,32)}|{(i,k,n) for i in ids for k in ('cached_prefix_vs32','online_prefix_vs32') for n in (1,8)}
    for key in ('protocol','failed_manifest','ensemble_manifest','reference','panel','checkpoint','embedding_cache','decoder_checkpoint'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed '+key)
    if len(m['comparisons'])!=len(wanted) or {(r['target_id'],r['kind'],r['count']) for r in m['comparisons']}!=wanted:raise ValueError('Incomplete diagnostic')
    failures=[];summary={}
    for r in m['comparisons']:
        if len(r['checks'])!=r['count'] or {v['slot'] for v in r['checks']}!=set(range(r['count'])):raise ValueError('Missing draw controls')
        key=r['kind']+'_'+str(r['count']);s=summary.setdefault(key,dict(draws=0,failures=0,max_ca_rmsd=0.,min_ca_lddt=1.))
        for v in r['checks']:
            if any(not math.isfinite(v[k]) for k in ('ca_rmsd','ca_lddt')):raise ValueError('Nonfinite control')
            bad=v['ca_rmsd']>.2 or v['ca_lddt']<.99 or not v['validity_identical'] or v['selected_draw']!=v['reference_draw'];s['draws']+=1;s['failures']+=int(bad);s['max_ca_rmsd']=max(s['max_ca_rmsd'],v['ca_rmsd']);s['min_ca_lddt']=min(s['min_ca_lddt'],v['ca_lddt'])
            if bad:failures.append(dict(target_id=r['target_id'],kind=r['kind'],count=r['count'],**v))
    return dict(status='complete',summaries=summary,failures=failures,embeddings=m['embeddings'],all_controls_passed=not failures,manifest_scope='Original head only; no quality-gate or timing promotion',protocol_sha256=c['protocol_sha256'])


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();path=a.runs[0]/'manifest.json';m=json.loads(path.read_text()) if path.exists() else dict(status='failed',error='Missing manifest');d=analyze(m);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');lines=['# Original retry output-equivalence diagnostic','',f"Status:{d['status']}. Unchanged0.2A/0.99 controls, exact selected indices and geometry decisions. All original eight latency families and every K1/8/32 prefix retained."]
    if d['status']=='complete':
        lines+=['','| Comparison | Draws | Failed | Max CA RMSD | Min CA lDDT |','|---|---:|---:|---:|---:|']
        for key,r in d['summaries'].items():lines.append(f"| {key} | {r['draws']} | {r['failures']} | {r['max_ca_rmsd']:.6f} | {r['min_ca_lddt']:.6f} |")
        for r in d['failures']:lines+=['',json.dumps(r)]
        lines+=['','Online versus cached ESM differences:']
        for r in d['embeddings']:lines.append(f"- {r['target_id']}: RMSE{r['rmse']:.8g}, max absolute{r['max_abs']:.8g}.")
        lines+=['','This diagnosis cannot relax the original control or promote a candidate. Batch-prefix and online-embedding effects are separated; failed latency49852006 remains failed. No independent-test scoring.']
    else:lines+=['',d['error']]
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')

if __name__=='__main__':main()
