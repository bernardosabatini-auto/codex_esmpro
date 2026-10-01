"""Replay recorded teacher-label RNG and quantify sparse late-time exposure."""
import argparse,hashlib,json,math
from pathlib import Path
from statistics import NormalDist
import numpy as np
from latentfold.teacher_states import audited_families,draw_teacher


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run',type=Path,required=True);p.add_argument('--step',type=int,choices=(500,2000),required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();m=json.loads((a.run/'manifest.json').read_text());c=m['config'];audited_families(c)
    if c['arm'] not in ('aligned_teacher','pca_teacher') or a.step<1 or a.step>m['updates']:raise ValueError('completed teacher-training prefix required')
    if c.get('flow_time_mean',0)!=0 or c.get('flow_time_std',1)!=1:raise ValueError('diagnostic currently assumes the default time distribution')
    rows=json.loads(Path(c['label_manifest']).read_text())['config']['targets'];records={r['id']:r for r in rows}
    scored={}
    for checkpoint in (0,a.step):
        values=[r for r in m['scores'] if r['step']==checkpoint and r['guidance']==1]
        if len(values)!=len(rows) or {r['target_id'] for r in values}!=set(records):raise ValueError('complete CFG1 scoring required')
        scored[checkpoint]={r['target_id']:r for r in values}
    buckets={k:[r['id'] for r in rows if r['bucket']==k] for k in (128,256,384,512)};queues={k:[] for k in buckets}
    counts={r['id']:np.zeros(len(r['state_definition']['teacher_indices']),dtype=int) for r in rows}
    order=np.random.default_rng(c['seed']);labels=np.random.default_rng(c['seed']+1);verified=[]
    logs={r['step']:r for r in m['training'] if r['step']<=a.step}
    for step in range(a.step):
        length=sorted(buckets)[step%4];batch=c['batches'][str(length)]
        while len(queues[length])<batch:queues[length].extend(order.permutation(buckets[length]).tolist())
        ids=queues[length][:batch];del queues[length][:batch];choices=[]
        for ident in ids:
            state=records[ident]['state_definition'];indices=state['teacher_indices']
            choice=draw_teacher(indices,state,labels.random(),c.get('label_distribution','empirical'));choices.append(choice)
            counts[ident][indices.index(choice)]+=1
        if step+1 in logs:
            log=logs[step+1]
            if log['ids_sha256']!=hashlib.sha256('\n'.join(ids).encode()).hexdigest() or log['label_choices_sha256']!=hashlib.sha256(np.asarray(choices,dtype='int64').tobytes()).hexdigest():raise ValueError('replayed sampling does not match recorded batch')
            verified.append(step+1)
    if len(verified)!=len(logs) or not verified:raise ValueError('unverified replay')
    # Default FlowConfig has logistic-normal time with mean0/std1 and dropout0.1.
    # These are expectations conditional on reconstructed labels, not observed
    # CUDA time/conditioning draws, and not counts of "useful" training examples.
    late_probability=1-NormalDist().cdf(math.log(3))
    d=dict(step=a.step,run=str(a.run),distribution=c.get('label_distribution','empirical'),verified_logged_batches=verified,
           time_above_075_probability=late_probability,conditional_late_probability=.9*late_probability,
           alternative_time_mean1_probability=1-NormalDist().cdf(math.log(3)-1),buckets={},targets=[])
    for r in rows:
        state=r['state_definition'];labels=np.asarray(state['clusters']);sizes=np.bincount(labels);singleton=sizes[labels]==1;draws=counts[r['id']]
        hits={checkpoint:sum(i in scored[checkpoint][r['id']]['assignments'] for i in np.flatnonzero(sizes==1)) for checkpoint in (0,a.step)}
        d['targets'].append(dict(id=r['id'],bucket=r['bucket'],total_draws=int(draws.sum()),singleton_label_draws=draws[singleton].tolist(),initial_singleton_hits=int(hits[0]),current_singleton_hits=int(hits[a.step])))
    lines=['# Teacher-label exposure diagnostic','',f"Replayed training prefix: {a.step} updates; {len(verified)} logged batch hashes match exactly.",'',
           'The complete target/label sequence is reconstructed from the training algorithm and seeds, checked against every saved batch hash. Time/conditioning counts below are analytic expectations; CUDA draws were not replayed. All noise times contribute to training. Time>0.75 is a diagnostic region where the finite-teacher oracle strongly resolves states, not a cutoff for useful learning.','',
           '| Padded length | Proteins | Mean examples/protein | Singleton states | Mean draws/singleton | Mean expected conditioned examples at t>0.75 | Initial singleton hits | Current singleton hits |',
           '|---|---:|---:|---:|---:|---:|---:|---:|']
    for length in buckets:
        selected=[r for r in d['targets'] if r['bucket']==length];singletons=[n for r in selected for n in r['singleton_label_draws']]
        v=dict(proteins=len(selected),mean_examples=float(np.mean([r['total_draws'] for r in selected])),singleton_states=len(singletons),mean_singleton_draws=float(np.mean(singletons)),mean_expected_conditional_late=float(np.mean(singletons))*.9*late_probability)
        v.update(initial_singleton_hits=sum(r['initial_singleton_hits'] for r in selected),current_singleton_hits=sum(r['current_singleton_hits'] for r in selected));d['buckets'][str(length)]=v
        lines.append(f"| {length} | {v['proteins']} | {v['mean_examples']:.2f} | {v['singleton_states']} | {v['mean_singleton_draws']:.2f} | {v['mean_expected_conditional_late']:.2f} | {v['initial_singleton_hits']} | {v['current_singleton_hits']} |")
    lines+=['',f"Default P(t>0.75)={late_probability:.5f}; shifting logistic-normal mean to1 would make it {d['alternative_time_mean1_probability']:.5f}. This arithmetic is not evidence that changing the time distribution improves the model. Prior-preserving time weighting remains a possible targeted follow-up if final capacity results warrant it."]
    lines+=['','The observed length pattern must be considered alongside exposure. More exposure alone is not a sufficient diagnosis of why an individual teacher state is missed; do not infer that late-time resampling will fix the failure from these counts.']
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
