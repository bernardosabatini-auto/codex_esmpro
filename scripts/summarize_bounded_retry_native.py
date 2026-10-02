"""Audit every retry and compare separately defined native pipelines."""
import argparse,json
from pathlib import Path
import numpy as np
from prepare_overfit import sha
from latentfold.teacher_states import paired_change


def validate_slot(draws, selection):
    attempts=selection['attempts'];slot=selection['slot']
    if not 1<=attempts<=4 or not 0<=slot<3 or len(draws)!=attempts:
        raise ValueError('Incomplete retry sequence')
    draws=sorted(draws,key=lambda r:r['attempt'])
    if [r['attempt'] for r in draws]!=list(range(attempts)) or any(r['draw']!=slot+3*r['attempt'] for r in draws):
        raise ValueError('Retry ordering changed')
    if any(r['coarse_valid'] not in (0,1) for r in draws):raise ValueError('Nonboolean validity')
    valid=[r for r in draws if r['coarse_valid']]
    if valid:
        if len(valid)!=1 or valid[0]!=draws[-1] or selection['exhausted'] or selection['selected_draw']!=valid[0]['draw']:
            raise ValueError('Selection is not first valid draw')
    elif attempts!=4 or not selection['exhausted'] or selection['selected_draw']!=slot:
        raise ValueError('Exhausted fallback changed')
    return draws[0],next(r for r in draws if r['draw']==selection['selected_draw'])


def analyze(m):
    if m['status']!='complete' or m['training_updates_executed']!=0:raise ValueError('Incomplete inference')
    c=m['config']
    for key in ('selection','protocol','diagnostic'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed '+key)
    protocol=json.loads(Path(c['protocol']).read_text());families={r['id']:r['family'] for r in json.loads(Path(c['selection']).read_text())['tuning']};heads=protocol['heads']
    if len(families)!=64 or len(set(families.values()))!=64 or [h['name'] for h in c['heads']]!=heads:raise ValueError('Wrong panel or heads')
    expected={(h,i,k) for h in heads for i in families for k in range(3)}
    key=lambda r:(r['head'],r['target_id'],r['slot'])
    if len(m['selections'])!=len(expected) or {key(r) for r in m['selections']}!=expected or any(key(r) not in expected for r in m['draws']):raise ValueError('Missing/duplicate/extra slots')
    if any(not np.isfinite(r[k]) or not 0<=r[k]<=1 for r in m['draws'] for k in ('ca_lddt','coarse_valid')):raise ValueError('Invalid score')
    controls=m['controls'];control_set={(h,b) for h in heads for b in (128,256,384,512)}
    if len(controls)!=16 or {(r['head'],r['length']) for r in controls}!=control_set or any(not np.isfinite(r[k]) for r in controls for k in ('ca_rmsd','ca_lddt')) or any(r['ca_rmsd']>.2 or r['ca_lddt']<.99 for r in controls):raise ValueError('Failed batching controls')
    grouped={q:[] for q in expected}
    for r in m['draws']:grouped[key(r)].append(r)
    values={h:dict(raw=[],retry=[]) for h in heads}
    for s in m['selections']:
        raw,retry=validate_slot(grouped[key(s)],s)
        values[s['head']]['raw'].append(raw);values[s['head']]['retry'].append(retry)
    for h in c['heads']:
        if sha(h['raw_manifest'])!=h['raw_manifest_sha256']:raise ValueError('Raw comparator changed')
        old=json.loads(Path(h['raw_manifest']).read_text());baseline={(r['target_id'],r['sample']):r for r in old['scores'] if r['head']==h['raw_head'] and r['guidance']==h['guidance']}
        if len(baseline)!=192:raise ValueError('Incomplete historical controls')
        for r in values[h['name']]['raw']:
            if any(abs(r[k]-baseline[(r['target_id'],r['slot'])][k])>1e-6 for k in ('ca_lddt','coarse_valid')):raise ValueError('Historical raw score changed')
    batches=m['batches'];initial={(h,b,o) for h in heads for b in (128,256,384,512) for o in (0,8)}
    if len([r for r in batches if r['attempt']==0])!=len(initial) or {(r['head'],r['length'],r['offset']) for r in batches if r['attempt']==0}!=initial:raise ValueError('Missing initial batch timings')
    if sum(r['batch'] for r in batches)!=len(m['draws']) or any(not np.isfinite(r[k]) or r[k]<=0 for r in batches for k in ('seconds','peak_reserved_bytes')):raise ValueError('Invalid draw/timing accounting')
    def metric(head,mode,key):return {i:float(np.mean([r[key] for r in values[head][mode] if r['target_id']==i])) for i in families}
    result=dict(status='complete',summaries={})
    for h in heads:
        comparisons={mode:{k:paired_change(metric(h,mode,k),metric('original',mode,k),families=families) for k in ('ca_lddt','coarse_valid')} for mode in ('raw','retry')}
        effect={k:paired_change(metric(h,'retry',k),metric(h,'raw',k),families=families) for k in ('ca_lddt','coarse_valid')}
        selected=[r for r in m['selections'] if r['head']==h];bs=[r for r in batches if r['head']==h]
        quality=comparisons['retry']['ca_lddt']['ci95'][0]>-.005 and comparisons['retry']['coarse_valid']['difference']>=-.01
        result['summaries'][h]=dict(comparisons=comparisons,retry_effect=effect,quality_passed=bool(quality),attempts=sum(r['attempts'] for r in selected),exhausted=sum(r['exhausted'] for r in selected),initial_seconds=sum(r['seconds'] for r in bs if r['attempt']==0),retry_seconds=sum(r['seconds'] for r in bs if r['attempt']>0),peak_reserved_gib=max(r['peak_reserved_bytes'] for r in bs)/1024**3)
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();path=a.runs[0]/'manifest.json';m=json.loads(path.read_text()) if path.exists() else dict(status='failed',error='Missing manifest')
    d=analyze(m) if m['status']=='complete' else dict(status=m['status'],error=m.get('error','Incomplete'))
    d['manifest_sha256']=sha(path) if path.exists() else None
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n')
    lines=['# Bounded retry native pipeline','','Separate64-family matched retry evaluation; all raw and attempted samples retained. Native qualification compares selected adapted outputs with selected original outputs. Historical raw failures remain unchanged.','','| Head | Raw CA / valid | Retry CA / valid | Retry CA difference [95% CI] | Validity difference | Qualified |','|---|---|---|---|---:|---|']
    for h,r in d.get('summaries',{}).items():
        raw=r['comparisons']['raw'];retry=r['comparisons']['retry'];ca=retry['ca_lddt'];v=retry['coarse_valid']
        lines.append(f"| {h} | {raw['ca_lddt']['candidate']:.5f} / {raw['coarse_valid']['candidate']:.5f} | {ca['candidate']:.5f} / {v['candidate']:.5f} | {ca['difference']:+.5f} {ca['ci95']} | {v['difference']:+.5f} | {r['quality_passed']} |")
    for h,r in d.get('summaries',{}).items():lines+=['',f"{h}: {r['attempts']} attempted draws for192 outputs; {r['exhausted']} exhausted slots. Initial generation {r['initial_seconds']:.2f}s plus retries {r['retry_seconds']:.2f}s; peak {r['peak_reserved_gib']:.2f}GiB."]
    lines+=['','Single-pass generation times exclude ESM, loading and disk I/O; not an end-to-end latency benchmark. Native qualification still requires matched external diversity and efficiency evidence. Original34 and reserved17 unscored.']
    if d.get('error'):lines+=['',d['error']]
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')

if __name__=='__main__':main()
