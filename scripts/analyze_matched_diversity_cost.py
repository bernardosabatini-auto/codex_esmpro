"""Descriptive diversity/cost curves on the exact intersection of timed families."""
import argparse
import json
from pathlib import Path
import h5py
import numpy as np
from prepare_overfit import sha
from score_ensemble_states import state_definition
from latentfold.ensemble_metrics import backbone_geometry
from latentfold.metrics import ca_metrics
from latentfold.teacher_states import paired_change

COUNTS = (1,8,32)
BUDGETS = (.5,1.,2.,4.,8.,16.)


def affordable_counts(times, budget):
    """Select sample count from latency alone, never observed coverage."""
    if set(times) != {str(k) for k in COUNTS}: raise ValueError('incomplete measured counts')
    ids = set(times['1'])
    if not ids or any(set(v) != ids for v in times.values()): raise ValueError('unmatched timing targets')
    if any(not np.isfinite(x) or x <= 0 for row in times.values() for x in row.values()): raise ValueError('invalid timing')
    return {i:max([0]+[k for k in COUNTS if times[str(k)][i] <= budget]) for i in ids}


def prefix_coverage(bb, row):
    positions, refs, i, j, reference, labels = state_definition(row)
    if not len(i) or len(set(labels)) < 2 or len(bb) != 32: raise ValueError('not an eligible32-sample state ensemble')
    ca = bb[:,positions,1]
    quality = np.array([[ca_metrics(x,y)['ca_lddt'] for y in refs] for x in ca])
    features = np.linalg.norm(ca[:,i]-ca[:,j],axis=-1)
    errors = np.sqrt(np.mean((features[:,None]-reference[None])**2,axis=-1))
    nearest = errors.argmin(1); best = errors[np.arange(32),nearest]
    good = (best <= 2.) & (quality.max(1) >= .8) & backbone_geometry(bb)['coarse_valid']
    assignments = [labels[k] if ok else None for k,ok in zip(nearest,good)]
    return {str(k):len(set(x for x in assignments[:k] if x is not None))/len(set(labels)) for k in (1,4,8,16,32)}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--latency',type=Path,required=True)
    for name in ('original','candidate','teacher'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    latency=json.loads((a.latency/'manifest.json').read_text());c=latency['config']
    if latency['status']!='complete' or 'RTX PRO 6000 Blackwell' not in latency['device_name']:raise ValueError('incomplete or wrong latency run')
    if sha(c['panel'])!=c['panel_sha256']:raise ValueError('panel changed')
    panel={r['query_id']:r for r in json.loads(Path(c['panel']).read_text())['development']}
    sources={k:getattr(a,k) for k in ('original','candidate','teacher')}
    scores={k:json.loads(v.read_text()) for k,v in sources.items()}
    settings=dict(original='cfg2/latent',candidate='cfg1/latent',teacher='steps50')
    selected={k:{r['target_id']:r for r in s['rows'] if r['setting']==settings[k] and r.get('contact_state_count',0)>1} for k,s in scores.items()}
    if any(s['status']!='complete' for s in scores.values()):raise ValueError('incomplete state scoring')
    ids=sorted(set(c['target_ids']) & set(selected['original']))
    if len(ids)!=4 or any(not set(ids)<=set(rows) for rows in selected.values()):raise ValueError('expected four timed state-eligible families')
    families={i:panel[i]['family'] for i in ids}
    if len(set(families.values()))!=4:raise ValueError('families not independent')
    for name in sources:
        if any(scores[name]['definitions'][i]!=scores['original']['definitions'][i] for i in ids):raise ValueError('state definitions differ')
    result=dict(status='running',families=families,curves={},sources={},budget_estimates={},comparisons={},timing_manifest_sha256=sha(a.latency/'manifest.json'),timing_scope=latency['scope'])
    for name,scorepath in sources.items():
        run=Path(scores[name]['run']);m=json.loads((run/'manifest.json').read_text());mc=m['config']
        if m['status']!='complete' or mc['panel_sha256']!=c['panel_sha256']:raise ValueError('ensemble provenance differs')
        if name=='teacher':
            if mc['steps']!=[50] or mc['sample_batch']!=16 or mc['samples']!=32:raise ValueError('teacher sampler differs')
        else:
            key='student_reference' if name=='original' else 'candidate_reference'
            if (run/'predictions.h5').resolve()!=Path(c[key]).resolve():raise ValueError('student timed-reference lineage differs')
        timing_kind='student' if name=='original' else name
        times={str(k):{} for k in COUNTS};coverage={}
        with h5py.File(run/'predictions.h5') as h:
            for ident in ids:
                coverage[ident]=prefix_coverage(h[ident][settings[name]]['backbone'][:],panel[ident])
                if any(coverage[ident][str(k)]!=selected[name][ident]['coverage']['2.0'][str(k)] for k in (1,4,16,32)):raise ValueError('rescored prefix differs from frozen scores')
                for k in COUNTS:
                    rows=[r for r in latency['rows'] if r['model']==timing_kind and r['target_id']==ident and r['samples']==k]
                    if len(rows)!=3 or {r['repeat'] for r in rows}!={0,1,2}:raise ValueError('incomplete repeats')
                    times[str(k)][ident]=float(np.median([r['seconds'] for r in rows]))
        result['sources'][name]=dict(score=str(scorepath),score_sha256=sha(scorepath),manifest=str(run/'manifest.json'),manifest_sha256=sha(run/'manifest.json'),predictions_sha256=sha(run/'predictions.h5'))
        result['curves'][name]=dict(times=times,coverage=coverage,means={str(k):dict(seconds=float(np.mean(list(times[str(k)].values()))),coverage=float(np.mean([coverage[i][str(k)] for i in ids]))) for k in COUNTS})
        result['budget_estimates'][name]={}
        for budget in BUDGETS:
            counts=affordable_counts(times,budget);values={i:coverage[i][str(k)] if k else 0. for i,k in counts.items()}
            result['budget_estimates'][name][str(budget)]=dict(counts=counts,coverage=values,mean_coverage=float(np.mean(list(values.values()))))
    for budget in BUDGETS:
        result['comparisons'][str(budget)]={other:paired_change(result['budget_estimates']['candidate'][str(budget)]['coverage'],result['budget_estimates'][other][str(budget)]['coverage'],families=families) for other in ('original','teacher')}
    result['status']='complete';a.output.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
    lines=['# Matched development diversity and inference cost','','Descriptive analysis of the four state-eligible families in the fixed eight-sequence RTX timing panel. These are a small selected development subset, not a new validation set. The same frozen contact definitions,2A/0.8/coarse-valid gate and every original sample are retained. K8 is rescored from stored predictions; K1/4/16/32 must exactly reproduce the existing scores.','','| Pipeline | K | Mean seconds | Mean valid state coverage |','|---|---:|---:|---:|']
    for name,d in result['curves'].items():
        for k,v in d['means'].items():lines.append(f"| {name} | {k} | {v['seconds']:.4f} | {v['coverage']:.4f} |")
    lines+=['','Budget estimates choose the largest measured K in{1,8,32} fitting each family’s latency median, using latency alone. No sample means zero coverage. No interpolation, extrapolation, sample selection or restart policy. These combine stored ensemble prefixes with separately measured runtime distributions; teacher timing uses different random seeds. They are estimates, not timed deadline-enforced experiments. Loading/warmup and confidence heads are outside the measured scope.','','| Seconds per family | Original | Compact balanced500 | Teacher |','|---|---:|---:|---:|']
    for budget in BUDGETS:lines.append(f"| {budget:g} | "+' | '.join(f"{result['budget_estimates'][name][str(budget)]['mean_coverage']:.4f}" for name in ('original','candidate','teacher'))+' |')
    lines+=['','The JSON retains every per-family count, coverage, latency and paired-family interval. Four families and fixed random prefixes do not support a broad performance verdict; this analysis does not qualify a model or change any gate. Do not mix these matched curves with the16-family overall coverage means.']
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
