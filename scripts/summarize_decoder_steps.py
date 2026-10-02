"""Geometry/accuracy tradeoffs of longer decoding at fixed latent samples."""
import argparse,itertools,json
from pathlib import Path
import numpy as np
from prepare_overfit import sha
from latentfold.teacher_states import paired_change

METRICS=('ca_lddt','coarse_valid','peptide_outlier_fraction','ca_clashing_residue_fraction','ca_gap_fraction')


def analyze(m):
    c=m['config']
    for key in ('selection','protocol','source_native_manifest'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('changed '+key)
    protocol=json.loads(Path(c['protocol']).read_text());selection=json.loads(Path(c['selection']).read_text());families={r['id']:r['family'] for r in selection['tuning']};heads=protocol['heads'];steps=protocol['decoder_steps'];rows=m['scores']
    if len(families)!=64 or len(set(families.values()))!=64 or len(heads)!=5 or [h['name'] for h in c['heads']]!=heads or steps!=[3,5,10] or m['training_updates_executed']!=0:raise ValueError('wrong decoder screen scope')
    def complete(values,keys,expected):
        observed=[tuple(r[k] for k in keys) for r in values]
        if len(observed)!=len(expected) or set(observed)!=expected:raise ValueError('missing or duplicate records')
    complete(rows,('head','decoder_steps','target_id','sample'),set(itertools.product(heads,steps,families,range(3))))
    if any(r['guidance']!=protocol['guidance_by_head'][r['head']][0] or any(not np.isfinite(r[k]) or not 0<=r[k]<=1 for k in METRICS) for r in rows):raise ValueError('invalid score or guidance')
    complete(m['controls'],('head','decoder_steps','length'),set(itertools.product(heads,steps,(128,256,384,512))))
    complete(m['reproduction_controls'],('head','target_id','sample'),set(itertools.product(heads,families,range(3))))
    if any(not np.isfinite(r[k]) for r in m['controls']+m['reproduction_controls'] for k in ('ca_rmsd','ca_lddt')) or any(r['ca_rmsd']>.2 or r['ca_lddt']<.99 for r in m['controls']+m['reproduction_controls']):raise ValueError('failed structural control')
    prior=json.loads(Path(c['source_native_manifest']).read_text());original={(r['head'],r['target_id'],r['sample']):r for r in prior['scores']};current={(r['head'],r['target_id'],r['sample']):r for r in rows if r['decoder_steps']==3}
    if prior['status']!='complete' or len(original)!=960 or set(original)!=set(current) or any(abs(current[i][k]-original[i][k])>1e-6 for i in current for k in METRICS):raise ValueError('decoder3 reproduction failed')
    values={(h,s):{key:{i:float(np.mean([r[key] for r in rows if (r['head'],r['decoder_steps'],r['target_id'])==(h,s,i)])) for i in families} for key in METRICS} for h,s in itertools.product(heads,steps)}
    def compare(a,b):return {k:paired_change(values[a][k],values[b][k],families=families) for k in METRICS}
    expected=[]
    for h in heads:
        for length in (128,256,384,512):
            for offset in range(0,sum(r['bucket']==length for r in selection['tuning']),8):
                expected.append((h,'flow',0,length,offset));expected.extend((h,'decoder',s,length,offset) for s in steps)
    times=[dict(r,decoder_steps=r.get('decoder_steps',0)) for r in m['batches']]
    complete(times,('head','stage','decoder_steps','length','offset'),set(expected))
    if any(not np.isfinite(r['seconds']) or r['seconds']<=0 for r in times):raise ValueError('invalid component timing')
    d=dict(summaries={},prior_effects={},replicated_quality_by_decoder={},checkpoint_step=c['training_checkpoint_step'])
    for h,s in itertools.product(heads,steps):
        metrics=compare((h,s),('original',3));within=compare((h,s),(h,3));flow_seconds=sum(r['seconds'] for r in times if r['head']==h and r['stage']=='flow');decoder_seconds=sum(r['seconds'] for r in times if r['head']==h and r['stage']=='decoder' and r['decoder_steps']==s)
        d['summaries'][f'{h}_decoder{s}']=dict(head=h,decoder_steps=s,versus_original_decoder3=metrics,versus_same_head_decoder3=within,quality_passed=bool(metrics['ca_lddt']['ci95'][0]>-.005 and metrics['coarse_valid']['difference']>=-.01),flow_seconds=flow_seconds,decoder_seconds=decoder_seconds)
    for s in steps:
        d['replicated_quality_by_decoder'][str(s)]=all(d['summaries'][f'seed{seed}_balanced_decoder{s}']['quality_passed'] for seed in protocol['seeds'])
        for seed in protocol['seeds']:d['prior_effects'][f'{seed}_decoder{s}']=compare((f'seed{seed}_balanced',s),(f'seed{seed}_empirical',s))
    return d


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',nargs='+',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();run=a.runs[0];path=run/'manifest.json';m=json.loads(path.read_text()) if path.exists() else dict(status='failed',error='Missing manifest');d=dict(status=m['status'])
    if m['status']=='complete':
        d.update(analyze(m));d['manifest_sha256']=sha(path)
        try:
            from summarize_comparison import hardware
            d['hardware']=hardware(Path(str(run)+'_nsight.sqlite'),m['batches'])
        except Exception as error:d['hardware']=dict(status='unavailable',error=str(error))
    else:d['error']=m.get('error','Incomplete decoder diagnostic')
    lines=['# Fixed-latent decoder integration comparison','',f"Status: {d['status']}.",'','Five pipelines,64 tuning families,three paired samples. Latents and decoder noise held fixed across3/5/10 steps. All source3-step scores and backbones must reproduce. Strict FP32, all samples retained; no locked-test scoring. Unadjusted family intervals. Component costs exclude ESMC, loading and untimed warmups and are not end-to-end benchmarks.','','| Head / decoder | CA-lDDT | CA delta vs original3 |95% interval | Valid | Validity delta | Qualified | Flow s | Decoder s |','|---|---:|---:|---|---:|---:|---|---:|---:|']
    for name,r in d.get('summaries',{}).items():
        ca=r['versus_original_decoder3']['ca_lddt'];v=r['versus_original_decoder3']['coarse_valid'];lines.append(f"| {name} | {ca['candidate']:.5f} | {ca['difference']:+.5f} | {ca['ci95']} | {v['candidate']:.5f} | {v['difference']:+.5f} | {r['quality_passed']} | {r['flow_seconds']:.2f} | {r['decoder_seconds']:.2f} |")
    lines+=['','| Within-head change from decoder3 | CA-lDDT difference | Validity difference | Clash-fraction difference | Peptide-outlier difference |','|---|---:|---:|---:|---:|']
    for name,r in d.get('summaries',{}).items():
        x=r['versus_same_head_decoder3'];lines.append(f"| {name} | {x['ca_lddt']['difference']:+.5f} | {x['coarse_valid']['difference']:+.5f} | {x['ca_clashing_residue_fraction']['difference']:+.5f} | {x['peptide_outlier_fraction']['difference']:+.5f} |")
    if 'error' in d:lines+=['',d['error']]
    else:lines+=['',f"Both balanced seeds qualify by decoder length: {d['replicated_quality_by_decoder']}.",'Geometry recovery is not proof of improved biological diversity. Separate ensembles and matched sequence timing remain necessary.']
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
