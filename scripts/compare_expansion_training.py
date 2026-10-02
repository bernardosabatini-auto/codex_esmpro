"""Replicated capacity evidence on the frozen64-family training diagnostic panel."""
import argparse,hashlib,json,math
from pathlib import Path
import numpy as np
from expansion_corpus import metadata
from compare_overfit_balanced import scored
from latentfold.teacher_states import paired_change,draw_teacher
from latentfold.training_schedule import proportional_schedule


def verify_draws(m,inventory,step):
    c=m['config'];buckets={b:[r['id'] for r in inventory['targets'] if r['bucket']==b] for b in (128,256,384,512)}
    targets={r['id']:r for r in inventory['targets']};lengths=proportional_schedule({b:len(v) for b,v in buckets.items()},c['updates'],c['seed']+2)
    if m['length_schedule']!=lengths:raise ValueError('wrong proportional length schedule')
    order=np.random.default_rng(c['seed']);labels=np.random.default_rng(c['seed']+1);queues={b:[] for b in buckets};expected=[]
    for s in range(step):
        length=lengths[s];count=c['batches'][str(length)]
        while len(queues[length])<count:queues[length].extend(order.permutation(buckets[length]).tolist())
        ids=queues[length][:count];del queues[length][:count]
        choices=[draw_teacher(targets[i]['state_definition']['teacher_indices'],targets[i]['state_definition'],labels.random(),'balanced') for i in ids]
        if s%25==0 or s+1 in c['evaluation_steps']:
            lr=c['learning_rate']*min((s+1)/c['warmup_updates'],1)*(.1+.9*.5*(1+math.cos(math.pi*s/max(c['updates']-1,1))))
            expected.append(dict(step=s+1,length=length,batch=count,learning_rate=lr,ids_sha256=hashlib.sha256('\n'.join(ids).encode()).hexdigest(),label_choices_sha256=hashlib.sha256(np.asarray(choices,dtype='int64').tobytes()).hexdigest()))
    logs=[r for r in m['training'] if r['step']<=step]
    if len(logs)!=len(expected):raise ValueError('missing training logs')
    for actual,wanted in zip(logs,expected):
        if any(actual[k]!=v for k,v in wanted.items() if k!='learning_rate') or not np.isclose(actual['learning_rate'],wanted['learning_rate'],rtol=1e-12,atol=1e-16):raise ValueError('target/label/LR draws differ from declared recipe')
        if not np.isfinite(actual['flow_loss']) or not np.isfinite(actual['gradient_norm']) or actual['gradient_norm']<=0:raise ValueError('invalid training diagnostic')


def compare(manifests,step):
    if len(manifests)!=2 or step not in (500,2000):raise ValueError('two declared seed endpoints required')
    configs=[m['config'] for m in manifests];normalized=[{k:v for k,v in c.items() if k!='seed'} for c in configs]
    if normalized[0]!=normalized[1]:raise ValueError('different data-breadth configurations')
    c=configs[0];inventory=metadata(c);protocol=json.loads(Path(c['protocol']).read_text());seeds=protocol['seeds']
    for key in ('updates','evaluation_steps','evaluation_guidance','evaluation_seed','learning_rate','ema_decay','warmup_updates','batches'):
        if c[key]!=protocol[key]:raise ValueError('training configuration differs from frozen protocol: '+key)
    if len(seeds)!=2 or {x['seed'] for x in configs}!=set(seeds) or c['corpus_kind']!='expansion' or c['profile_only'] or c['evaluation_guidance']!=[1]:raise ValueError('wrong experiment scope')
    all_targets={r['id']:r for r in inventory['targets']};targets={i:all_targets[i] for i in c['evaluation_ids']};families={i:r['family'] for i,r in targets.items()}
    old={i for i,r in targets.items() if r['cohort']=='original122'};new=set(targets)-old
    if len(old)!=32 or len(new)!=32:raise ValueError('wrong original/new capacity-panel membership')
    metrics=('coverage32','strict_coverage32','valid_fraction','teacher_ca_lddt','reference_ca_lddt','balanced_state_tv')
    initial=scored(manifests[0],0,1,targets)
    for m in manifests:
        if m['status'] not in ('running','complete') or m['updates']<step or m['initial_checkpoint_sha256']!=c['checkpoint_sha256']:raise ValueError('checkpoint incomplete or wrong initialization')
        verify_draws(m,inventory,step)
        other=scored(m,0,1,targets)
        for ident,r in other.items():
            if r['assignments']!=initial[ident]['assignments'] or any(not np.isclose(r[k],initial[ident][k],atol=1e-5,rtol=0) for k in metrics):raise ValueError('different initialization predictions')
    d=dict(step=step,matched=True,seeds=seeds,training_targets=len(all_targets),evaluation_ids=c['evaluation_ids'],summaries={},comparisons={},capacity_checks={})
    for m in manifests:
        seed=m['config']['seed'];rows=scored(m,step,1,targets)
        for cohort,ids in dict(all64=set(targets),original32=old,new32=new).items():
            name=f'{seed}_{cohort}'
            d['summaries'][name]={key:float(np.mean([rows[i][key] for i in ids])) for key in metrics}
            d['comparisons'][name+'_vs_initial']={key:paired_change({i:rows[i][key] for i in sorted(ids)},{i:initial[i][key] for i in sorted(ids)},families={i:families[i] for i in ids}) for key in metrics}
        checks={}
        for cohort in ('all64','new32'):
            values=d['comparisons'][f'{seed}_{cohort}_vs_initial'];checks[cohort+'_recall']=values['coverage32']['ci95'][0]>0;checks[cohort+'_validity']=values['valid_fraction']['difference']>=-.01
        d['capacity_checks'][str(seed)]=dict(checks=checks,passed=all(checks.values()))
    d['replicated_capacity_passed']=all(x['passed'] for x in d['capacity_checks'].values());return d


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--runs',type=Path,nargs=2,required=True);p.add_argument('--step',type=int,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    manifests=[json.loads((p/'manifest.json').read_text()) for p in a.runs];d=compare(manifests,a.step)
    root=Path(__file__).resolve().parents[1];inventory=metadata(manifests[0]['config']);targets={r['id']:r for r in inventory['targets']};original={i:targets[i] for i in d['evaluation_ids'] if targets[i]['cohort']=='original122'}
    d['historical_full122']={}
    for m,jid in zip(sorted(manifests,key=lambda m:m['config']['seed']),('49753133','49753251')):
        historical=json.loads((root/f'runs/overfit_{jid}/manifest.json').read_text());hc=historical['config'];oldinv=json.loads(Path(hc['corpus_inventory']).read_text());oldtargets={r['id']:r for r in oldinv['targets']}
        if historical['status']!='complete' or hc['seed']!=m['config']['seed'] or hc['label_distribution']!='balanced' or hc['corpus_inventory_sha256']!=inventory['old_inventory_sha256'] or historical['initial_checkpoint_sha256']!=m['initial_checkpoint_sha256']:raise ValueError('historical comparator identity changed')
        for i in original:
            if any(original[i][key]!=oldtargets[i][key] for key in ('state_definition','source_labels_sha256','sequence_sha256')):raise ValueError('historical original32 labels changed')
        oldscores=scored(historical,a.step,1,oldtargets);panel={i:targets[i] for i in d['evaluation_ids']};newscore=scored(m,a.step,1,panel)
        families={i:original[i]['family'] for i in original};d['historical_full122'][str(hc['seed'])]={k:paired_change({i:newscore[i][k] for i in original},{i:oldscores[i][k] for i in original},families=families) for k in ('coverage32','valid_fraction','teacher_ca_lddt')}
    lines=['# Larger-corpus training capacity','',f"Checkpoint{a.step}; {d['training_targets']} training families, fixed64-family diagnostic panel. Both seeds retained; exact target/label/LR schedules and initialization checked.",'','Every evaluated family is training data. Family intervals are unadjusted. This cannot establish external diversity or promote a model.','','| Seed / training cohort | Recall2A | Recall1A | Valid | Teacher CA-lDDT | Balanced TV |','|---|---:|---:|---:|---:|---:|']
    for name,r in d['summaries'].items():lines.append(f"| {name} | {r['coverage32']:.5f} | {r['strict_coverage32']:.5f} | {r['valid_fraction']:.5f} | {r['teacher_ca_lddt']:.5f} | {r['balanced_state_tv']:.5f} |")
    for name,r in d['comparisons'].items():lines+=['',f"{name}: recall delta{r['coverage32']['difference']:+.5f},95% interval{r['coverage32']['ci95']}; validity delta{r['valid_fraction']['difference']:+.5f}."]
    for seed,r in d['historical_full122'].items():lines+=['',f"Original32, seed{seed}, larger minus historical full122: recall{r['coverage32']['difference']:+.5f},95% interval{r['coverage32']['ci95']}; validity{r['valid_fraction']['difference']:+.5f}. Target draws differ across corpus sizes; this is a paired family diagnostic, not identical optimization streams."]
    lines+=['',f"Replicated declared capacity gate: {d['replicated_capacity_passed']}. Both checkpoints still require the separate unchanged native quality screen."]
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
