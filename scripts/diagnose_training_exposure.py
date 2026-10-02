"""Audit realized balanced-label exposure versus equal-update corpus comparisons."""
import argparse,collections,json
from pathlib import Path
import numpy as np
from prepare_overfit import sha
from compare_expansion_training import verify_draws
from latentfold.teacher_states import draw_teacher


def exposure(manifest,inventory,step):
    """Validate historical logs before reconstructing every target/state draw.

    Raw draws differ with batch size. Each example's gradient weight is1/B;
    report both quantities rather than mistaking draw counts for loss weights.
    """
    verify_draws(manifest,inventory,step)
    c=manifest['config'];rows={r['id']:r for r in inventory['targets']}
    buckets={b:[r['id'] for r in inventory['targets'] if r['bucket']==b] for b in (128,256,384,512)}
    order=np.random.default_rng(c['seed']);labels=np.random.default_rng(c['seed']+1);queues={b:[] for b in buckets}
    draws=collections.Counter();weight=collections.Counter();states={i:collections.Counter() for i in rows}
    for length in manifest['length_schedule'][:step]:
        count=c['batches'][str(length)]
        while len(queues[length])<count:queues[length].extend(order.permutation(buckets[length]).tolist())
        ids=queues[length][:count];del queues[length][:count]
        for ident in ids:
            state=rows[ident]['state_definition'];indices=state['teacher_indices'];chosen=draw_teacher(indices,state,labels.random(),'balanced')
            cluster=state['clusters'][indices.index(chosen)]
            draws[ident]+=1;weight[ident]+=1/count;states[ident][cluster]+=1
    def describe(values):
        a=np.asarray(values,dtype=float);return dict(min=float(a.min()),median=float(np.median(a)),mean=float(a.mean()),max=float(a.max()))
    per_target={i:dict(bucket=r['bucket'],family=r['family'],draws=draws[i],gradient_mass=weight[i],states=r['state_definition']['states'],states_drawn=len(states[i]),minimum_draws_per_state=min(states[i][s] for s in range(r['state_definition']['states']))) for i,r in rows.items()}
    groups={'all':list(rows),**{str(b):ids for b,ids in buckets.items()}}
    d=dict(seed=c['seed'],step=step,families=len(rows),total_draws=sum(draws.values()),gradient_mass_sum=sum(weight.values()),groups={},per_target=per_target)
    if not np.isclose(d['gradient_mass_sum'],step):raise ValueError('per-step protein weighting lost')
    for group,ids in groups.items():
        if not ids:continue
        d['groups'][group]=dict(families=len(ids),draws=describe([draws[i] for i in ids]),gradient_mass=describe([weight[i] for i in ids]),families_missing_state=sum(per_target[i]['states_drawn']<per_target[i]['states'] for i in ids),minimum_draws_per_state=describe([per_target[i]['minimum_draws_per_state'] for i in ids]))
    return d


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs='+',required=True);p.add_argument('--steps',type=int,nargs='+',default=[500,2000]);p.add_argument('--output',type=Path,required=True);a=p.parse_args();results={}
    for path in a.runs:
        m=json.loads((path/'manifest.json').read_text());c=m['config']
        if c.get('label_distribution')!='balanced' or c.get('corpus_kind') not in (None,'expansion') or m['updates']<max(a.steps):raise ValueError('requires completed declared balanced updates')
        if sha(c['corpus_inventory'])!=c['corpus_inventory_sha256']:raise ValueError('inventory changed')
        inv=json.loads(Path(c['corpus_inventory']).read_text())
        for step in a.steps:results[f'{path.name}_{step}']=exposure(m,inv,step)
    d=dict(scope='Training exposure diagnostic, not a causal training-duration comparison or an authorization for longer runs.',runs=results)
    lines=['# Balanced teacher-label training exposure','',d['scope'],'','Per-update bucket probabilities follow family counts. Batches vary by length; raw draws are therefore not the same as influence in the protein-mean loss. Gradient mass below sums each example weight1/batch-size before learning-rate scaling, clipping and adaptive optimization. Its total equals updates; it does not estimate actual parameter displacement.','','| Run / updates | Families | Total draws | Median draws/family | Median gradient mass | Families missing a state |','|---|---:|---:|---:|---:|---:|']
    for name,r in results.items():
        g=r['groups']['all'];lines.append(f"| {name} | {r['families']} | {r['total_draws']} | {g['draws']['median']:.1f} | {g['gradient_mass']['median']:.3f} | {g['families_missing_state']} |")
    lines+=['','Same update counts do not give the same optimization exposure per family across corpus sizes. More examples per family would require additional training; whether that improves unseen valid diversity remains untested. All reconstructed target/label/LR logs must match their recorded runs.']
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
