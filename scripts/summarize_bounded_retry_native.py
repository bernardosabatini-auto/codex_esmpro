"""Audit every retry and compare separately defined native pipelines."""
import argparse,json
from pathlib import Path
import numpy as np
from prepare_overfit import sha
from latentfold.teacher_states import paired_change
from antithetic_noise import noise_address,native_scheme,raw_identity_samples
from retry_sampler_settings import native_steps


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


def validate_prior_original(current,prior):
    if prior['status']!='complete':raise ValueError('Incomplete prior retry screen')
    selections={(r['target_id'],r['slot']):r for r in prior['selections'] if r['head']=='original'}
    previous={(r['target_id'],r['draw']):r for r in prior['draws'] if r['head']=='original'}
    if len(selections)!=192 or len(current)!=192 or {(r['target_id'],r['slot']) for r in current}!=set(selections):raise ValueError('Missing shared original controls')
    for r in current:
        chosen=selections[(r['target_id'],r['slot'])]['selected_draw'];old=previous[(r['target_id'],chosen)]
        if r['draw']!=chosen or any(abs(r[k]-old[k])>1e-6 for k in ('ca_lddt','coarse_valid')):raise ValueError('Selected original retry control changed')


def analyze(m):
    if m['status']!='complete' or m['training_updates_executed']!=0:raise ValueError('Incomplete inference')
    c=m['config']
    for key in ('selection','protocol','diagnostic','capacity_report','prior_retry_manifest'):
        if c.get(key) and sha(c[key])!=c[key+'_sha256']:raise ValueError('Changed '+key)
    protocol=json.loads(Path(c['protocol']).read_text());families={r['id']:r['family'] for r in json.loads(Path(c['selection']).read_text())['tuning']};heads=protocol['heads']
    if len(families)!=64 or len(set(families.values()))!=64 or [h['name'] for h in c['heads']]!=heads:raise ValueError('Wrong panel or heads')
    expected={(h,i,k) for h in heads for i in families for k in range(3)}
    key=lambda r:(r['head'],r['target_id'],r['slot'])
    if len(m['selections'])!=len(expected) or {key(r) for r in m['selections']}!=expected or any(key(r) not in expected for r in m['draws']):raise ValueError('Missing/duplicate/extra slots')
    if any(not np.isfinite(r[k]) or not 0<=r[k]<=1 for r in m['draws'] for k in ('ca_lddt','coarse_valid')):raise ValueError('Invalid score')
    controls=m['controls'];control_set={(h,b) for h in heads for b in (128,256,384,512)}
    if len(controls)!=len(control_set) or {(r['head'],r['length']) for r in controls}!=control_set or any(not np.isfinite(r[k]) for r in controls for k in ('ca_rmsd','ca_lddt')) or any(r['ca_rmsd']>.2 or r['ca_lddt']<.99 for r in controls):raise ValueError('Failed batching controls')
    grouped={q:[] for q in expected}
    for r in m['draws']:grouped[key(r)].append(r)
    values={h:dict(raw=[],retry=[]) for h in heads}
    for s in m['selections']:
        raw,retry=validate_slot(grouped[key(s)],s)
        values[s['head']]['raw'].append(raw);values[s['head']]['retry'].append(retry)
    for h in c['heads']:
        scheme=native_scheme(h,protocol);steps=native_steps(h,protocol)
        if h.get('raw_source_manifest') and sha(h['raw_source_manifest'])!=h['raw_source_manifest_sha256']:raise ValueError('Archived raw source changed')
        for record in m['draws']+m['batches']+m['controls']:
            if record['head']==h['name'] and (steps!=25 or 'sampling_steps' in record) and record.get('sampling_steps')!=steps:raise ValueError('Recorded step count changed')
        for r in [r for r in m['draws'] if r['head']==h['name']]:
            if scheme=='antithetic' or 'latent_noise_index' in r:
                if (r.get('latent_noise_index'),r.get('latent_noise_sign'))!=noise_address(r['draw'],scheme):raise ValueError('Recorded latent noise addressing changed')
        if sha(h['raw_manifest'])!=h['raw_manifest_sha256']:raise ValueError('Raw comparator changed')
        old=json.loads(Path(h['raw_manifest']).read_text());baseline={(r['target_id'],r['sample']):r for r in old['scores'] if r['head']==h['raw_head'] and r['guidance']==h['guidance']}
        if len(baseline)!=192:raise ValueError('Incomplete historical controls')
        for r in values[h['name']]['raw']:
            if r['slot'] in raw_identity_samples(h,protocol) and any(abs(r[k]-baseline[(r['target_id'],r['slot'])][k])>1e-6 for k in ('ca_lddt','coarse_valid')):raise ValueError('Historical raw score changed')
    if c.get('prior_retry_manifest'):
        validate_prior_original(values['original']['retry'],json.loads(Path(c['prior_retry_manifest']).read_text()))
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
    if protocol.get('additional_reference_head'):
        reference=protocol['additional_reference_head']
        if reference not in heads:raise ValueError('Missing additional reference head')
        for h in heads:result['summaries'][h]['versus_additional_reference']={k:paired_change(metric(h,'retry',k),metric(reference,'retry',k),families=families) for k in ('ca_lddt','coarse_valid')}
        result['additional_reference_head']=reference
    if protocol.get('antithetic_head'):
        anti=protocol['antithetic_head'];effects={k:paired_change(metric(anti,'retry',k),metric('compact500','retry',k),families=families) for k in ('ca_lddt','coarse_valid')}
        result['antithetic_vs_compact']=effects
        result['antithetic_qualified']=bool(result['summaries'][anti]['quality_passed'] and effects['ca_lddt']['ci95'][0]>-.005 and effects['coarse_valid']['difference']>=-.01)
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
    if d.get('additional_reference_head'):
        for h,r in d['summaries'].items():
            e=r['versus_additional_reference'];lines+=['',f"{h} versus selected{d['additional_reference_head']}: CA difference{e['ca_lddt']['difference']:+.5f},95% interval{e['ca_lddt']['ci95']}; validity difference{e['coarse_valid']['difference']:+.5f}."]
    if 'antithetic_qualified' in d:
        effects=d['antithetic_vs_compact'];lines+=['',f"Antithetic versus selected compact IID: CA difference{effects['ca_lddt']['difference']:+.5f},95% interval{effects['ca_lddt']['ci95']}; validity difference{effects['coarse_valid']['difference']:+.5f}. Both original and compact native criteria pass:{d['antithetic_qualified']}. Antithetic first output matches historical sample0; other first outputs intentionally use paired latent noise and remain fully included."]
    if d.get('error'):lines+=['',d['error']]
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')

if __name__=='__main__':main()
