"""Fixed sample mixtures and observed support bounds on stored development draws."""
import argparse,json
from pathlib import Path
import h5py,numpy as np
from prepare_overfit import sha
from score_ensemble_states import state_definition
from latentfold.metrics import ca_metrics
from latentfold.ensemble_metrics import backbone_geometry
from latentfold.teacher_states import paired_change


def metrics(assignments,quality,valid):
    hits=set(assignments)-{None}
    return dict(coverage=len(hits)/2,both_states=float(len(hits)==2),ca_lddt=float(np.mean(quality)),valid_fraction=float(np.mean(valid)))


def combine(records,counts):
    if sum(counts.values())!=32 or any(k not in records or not 0<n<=32 for k,n in counts.items()):raise ValueError('Fixed mixture must contain32 existing outputs')
    return metrics([x for k,n in counts.items() for x in records[k]['assignments'][:n]],np.concatenate([records[k]['quality'][:n] for k,n in counts.items()]),np.concatenate([records[k]['valid'][:n] for k,n in counts.items()]))


def main():
    p=argparse.ArgumentParser();p.add_argument('--protocol',type=Path,default=Path('configs/model_mixture_diagnostic_protocol.json'));p.add_argument('--output',type=Path,required=True);a=p.parse_args();protocol=json.loads(a.protocol.read_text());records={};families=None;definitions=None;sources={}
    for name,jid in protocol['sources'].items():
        run=Path('runs/retry_ensemble_'+jid);manifest=run/'manifest.json';scorepath=Path('runs/state_scores_'+jid+'/score.json');m=json.loads(manifest.read_text());s=json.loads(scorepath.read_text());c=m['config'];audit=json.loads(Path('reports/retry_ensemble_'+jid+'.json').read_text())
        if m['status']!='complete' or s['status']!='complete' or audit['status']!='complete' or audit['manifest_sha256']!=sha(manifest) or audit['predictions_sha256']!=sha(run/'predictions.h5') or sha(c['panel'])!=c['panel_sha256']:raise ValueError('Changed/incomplete frozen source')
        selected={r['target_id']:r for r in s['rows'] if r['setting']==f"cfg{c['primary_guidance']}/latent" and r.get('contact_state_count')==2}
        if len(selected)!=16:raise ValueError('All16 two-state families required')
        f={i:r['family'] for i,r in selected.items()}
        if families is None:families=f;definitions=s['definitions']
        if families!=f or definitions!=s['definitions']:raise ValueError('Mismatched families/state definitions')
        panel={r['query_id']:r for r in json.loads(Path(c['panel']).read_text())['development']}
        with h5py.File(run/'predictions.h5') as h:
            for ident in sorted(selected):
                bb=h[ident][f"cfg{c['primary_guidance']}"]['latent']['backbone'][:];pos,refs,i,j,features,labels=state_definition(panel[ident]);valid=backbone_geometry(bb)['coarse_valid'];ca=bb[:,pos,1]
                quality=np.array([[ca_metrics(x,y)['ca_lddt'] for y in refs] for x in ca]).max(1);f=np.linalg.norm(ca[:,i]-ca[:,j],axis=-1);error=np.sqrt(np.mean((f[:,None]-features[None])**2,axis=-1));nearest=error.argmin(1);good=(error[np.arange(32),nearest]<=2)&(quality>=.8)&valid;assign=[labels[n] if ok else None for n,ok in zip(nearest,good)]
                values=metrics(assign,quality,valid);old=selected[ident]
                if values['coverage']!=old['coverage']['2.0']['32'] or values['valid_fraction']!=old['coarse_valid_fraction'] or not np.isclose(values['ca_lddt'],old['oracle_nearest_reference_ca_lddt_mean'],atol=1e-12,rtol=0):raise ValueError('Published selected scores no longer reproduce')
                records.setdefault(ident,{})[name]=dict(assignments=assign,quality=quality.tolist(),valid=valid.tolist(),metrics=values)
        sources[name]=dict(run=str(run),manifest_sha256=sha(manifest),scores_sha256=sha(scorepath),predictions_sha256=audit['predictions_sha256'])
    rows={}
    for ident,heads in records.items():
        mixtures={name:combine(heads,counts) for name,counts in protocol['fixed_mixtures'].items()}
        support=set(x for r in heads.values() for x in r['assignments'] if x is not None)
        rows[ident]=dict(family=families[ident],heads=heads,mixtures=mixtures,observed_union_coverage=len(support)/2,observed_union_both_states=float(len(support)==2))
    baseline={i:r['heads']['original']['metrics'] for i,r in rows.items()};d=dict(status='complete',protocol_sha256=sha(a.protocol),sources=sources,rows=rows,mixtures={})
    for name in protocol['fixed_mixtures']:
        effects={key:paired_change({i:r['mixtures'][name][key] for i,r in rows.items()},{i:baseline[i][key] for i in rows},families=families) for key in ('coverage','both_states','ca_lddt','valid_fraction')}
        d['mixtures'][name]=dict(effects=effects,feasible=bool(effects['coverage']['difference']>=.1 and effects['coverage']['ci95'][0]>0 and effects['ca_lddt']['ci95'][0]>-.005 and effects['valid_fraction']['difference']>=-.01))
    d['observed_union']={key:paired_change({i:r['observed_union_'+key] for i,r in rows.items()},{i:baseline[i][key] for i in rows},families=families) for key in ('coverage','both_states')}
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n')
    lines=['# Model complementarity in saved development samples','','Exploratory CPU-only diagnostic, using every one of the16 two-state families. Three fixed32-output mixtures; no family-specific model choice or reference-informed sample selection. All constituent predictions are from the recorded retry pipelines.','','| Fixed mixture | Coverage | Difference [95% CI] | Both-state families | CA-lDDT | Valid | Feasible |','|---|---:|---|---:|---:|---:|---|']
    for name,r in d['mixtures'].items():
        e=r['effects'];v=e['coverage'];lines.append(f"| {name} | {v['candidate']:.5f} | {v['difference']:+.5f} {v['ci95']} | {round(16*e['both_states']['candidate'])}/16 | {e['ca_lddt']['candidate']:.5f} | {e['valid_fraction']['candidate']:.5f} | {r['feasible']} |")
    u=d['observed_union']['coverage'];lines+=['',f"Observed union of all128 saved outputs/family: coverage{u['candidate']:.5f}, change{u['difference']:+.5f} interval{u['ci95']} versus original32. This is a support bound for these saved draws, not a32-sample pipeline or a bound on future unseen noise draws.",'','A positive mixture feasibility result would still need native, all48-family MD and matched latency testing. Mixing multiple loaded heads adds model memory and inference cost; no efficiency claim from this CPU calculation. No mixing-weight grid. Original34 and reserved17 remain unscored.']
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n');print(json.dumps({name:r['feasible'] for name,r in d['mixtures'].items()}))

if __name__=='__main__':main()
