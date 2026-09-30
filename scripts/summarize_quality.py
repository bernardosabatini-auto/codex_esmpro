"""Matched confidence-weighting pilot, reusing the three identical flow controls."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from latentfold.metrics import paired_comparison
from summarize_comparison import validate_scores, means_by_target, hardware
from summarize_pilot import geometry_by_target, METRICS


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--runs',nargs='+',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();result=dict(status='incomplete',failures=[],seeds={},hardware={});aggregate={arm:{m:{} for m in METRICS} for arm in ('flow','confidence')}
    for run in a.runs:
        try:
            train=json.loads((run/'training.json').read_text());config=train['config'];seed=train['task']['seed']
            if train['status']!='complete' or train['steps']!=500 or not all(r['passed'] for r in train['weighted_gradient_controls']):
                raise ValueError('incomplete training or failed controls')
            control_path=Path(config['matched_control_runs'][str(seed)])
            ct=json.loads((control_path/'training.json').read_text())
            if ct['status']!='complete' or ct['task']!={'seed':seed,'arm':'flow'}:raise ValueError('invalid matched control')
            removed={'tasks','confidence_weights','confidence_weights_sha256','matched_control_runs','reference_job'}
            if {k:v for k,v in config.items() if k not in removed}!= {k:v for k,v in ct['config'].items() if k not in removed}:
                raise ValueError('control training settings differ beyond weighting')
            signature=lambda d:[(r['step'],r['input_ids_sha256'],r['flow_rng_sha256']) for r in d['rows']]
            if signature(train)!=signature(ct):raise ValueError('paired input or RNG streams differ')
            cp=Path(config['development_clusters'])
            if hashlib.sha256(cp.read_bytes()).hexdigest()!=config['development_clusters_sha256']:raise ValueError('clusters changed')
            clusters=json.loads(cp.read_text())['clusters'];rows={}
            for arm,path in [('flow',control_path),('confidence',run)]:
                m=json.loads((path/'evaluation/manifest.json').read_text());s=json.loads((path/'evaluation/scores.json').read_text());validate_scores(m,s);rows[arm]=s['records']
            paired={}
            for metric in METRICS:
                means={arm:means_by_target(r,'steps25_cfg2',metric) for arm,r in rows.items()}
                paired[metric]=paired_comparison(means['flow'],means['confidence'],clusters=clusters)
                for arm in means:
                    for name,value in means[arm].items():aggregate[arm][metric].setdefault(name,[]).append(value)
            paired['geometry']={field:paired_comparison(geometry_by_target(rows['flow'],field),geometry_by_target(rows['confidence'],field),clusters=clusters) for field in ('predicted_ca_gaps_on_reference_short','peptide_length_outliers_on_reference_short')}
            if str(seed) in result['seeds']:raise ValueError('duplicate training seed')
            result['seeds'][str(seed)]=paired
            result['hardware'][run.name]=dict(training_seconds=train['training_seconds'],peak_reserved_gib=train['peak_reserved_bytes']/2**30,training=hardware(Path(str(run)+'_nsight.sqlite'),train['batches'],prefix='train::'))
        except Exception as error:result['failures'].append(dict(run=str(run),error=f'{type(error).__name__}: {error}'))
    lines=['# Confidence-weighted training pilot','', 'One change to the three matched control runs: fixed source-pLDDT residue weights. Same 1,024 proteins, input order, random draws, 500 updates, learning rate and inference settings. No examples dropped.']
    if not result['failures'] and len(result['seeds'])==3:
        result['status']='complete'
        result['mean_across_training_seeds']={m:paired_comparison({k:float(np.mean(v)) for k,v in aggregate['flow'][m].items()},{k:float(np.mean(v)) for k,v in aggregate['confidence'][m].items()},clusters=clusters) for m in METRICS}
        tm=result['mean_across_training_seeds']['tm_fixed_reference'];lddt=result['mean_across_training_seeds']['ca_lddt']
        result['development_gate_passed']=(tm['theirs_minus_ours']>=.01 and tm['ci95'][0]>0 and all(v['tm_fixed_reference']['theirs_minus_ours']>0 for v in result['seeds'].values()) and lddt['ci95'][0]>=-.005 and all(m['ci95'][1]<=.001 for v in result['seeds'].values() for m in v['geometry'].values()))
        lines+=['',f"Mean TM change {tm['theirs_minus_ours']:+.5f}, 95% sequence-cluster CI {tm['ci95']}. Development gate passed: {result['development_gate_passed']}.",
            'Cluster intervals condition on these three training seeds. Development data are reused; independent final-test confirmation remains required. Geometry diagnostics use the inherited reference-short CA proxy.']
    else:lines+=['','Incomplete; no accuracy promotion.']
    lines+=['','```json',json.dumps(result,indent=2),'```']
    a.output.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n');a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
