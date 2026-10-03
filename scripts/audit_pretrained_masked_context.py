"""Describe conditioning and context effects without changing failed gates."""
import argparse,json
from pathlib import Path
import numpy as np
from compare_extra_fragment_refolds import clustered
from pretrained_masked_refolding import require_quality
from prepare_overfit import sha


def analyze(report):
    d=json.loads(report.read_text())
    if d['status']!='complete' or not d['pretrained_masked'] or d['profile_only'] or d['updates']!=2000 or d['refold_gate']['qualified']:raise ValueError('Expected completed failed full pretrained repair')
    try:require_quality(d)
    except ValueError:pass
    else:raise ValueError('Refold preparation failed to reject the actual failed run')
    arms=('parent','generated_cond','generated_null','native_cond','native_null');rows={a:{(r['target_id'],r['generation_slot']):r for r in d['records'] if r['arm']==a} for a in arms};keys=set(rows['parent']);ids=sorted({i for i,k in keys})
    if len(ids)!=32 or len(keys)!=128 or any(set(rows[a])!=keys for a in arms):raise ValueError('Changed complete paired panel')
    contrasts=[]
    for candidate,reference in [('generated_cond','parent'),('generated_cond','generated_null'),('native_cond','native_null'),('native_cond','generated_cond')]:
        metrics={}
        for metric in ('raw_gate_passed','coarse_valid','motif_ca_rmsd'):
            delta=[np.mean([float(rows[candidate][i,k][metric])-float(rows[reference][i,k][metric]) for k in range(4)]) for i in ids];metrics[metric]=clustered(delta)
        contrasts.append(dict(candidate=candidate,reference=reference,metrics=metrics))
    transitions=dict(retained_raw=sum(rows['parent'][k]['raw_gate_passed'] and rows['generated_cond'][k]['raw_gate_passed'] for k in keys),lost_raw=sum(rows['parent'][k]['raw_gate_passed'] and not rows['generated_cond'][k]['raw_gate_passed'] for k in keys),new_raw=sum(not rows['parent'][k]['raw_gate_passed'] and rows['generated_cond'][k]['raw_gate_passed'] for k in keys),native_raw_but_generated_failed=sum(rows['native_cond'][k]['raw_gate_passed'] and not rows['generated_cond'][k]['raw_gate_passed'] for k in keys))
    return dict(status='complete',source_report_sha256=sha(report),contrasts=contrasts,transitions=transitions,refold_preparation_rejects_failed_run=True,
                scope='Post hoc paired diagnostic on32 repeatedly used training proteins,4fixed noises each. Bootstrap units are protein IDs; no independent generalization or training-seed replication claim. Native context supplies oracle scaffold information. Its advantage mixes context compatibility and model-distribution effects; it does not prove a motif physically impossible in a generated scaffold. Transition counts do not define a deployable selector. All original gates remain failed; no refolds were launched.')


def main():
    p=argparse.ArgumentParser();p.add_argument('--report',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();d=analyze(a.report);a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');lines=['# Pretrained masked-flow context diagnostic','',d['scope'],'','|Candidate minus reference|Raw difference|95% protein-bootstrap interval|','|---|---:|---|']
    for r in d['contrasts']:
        x=r['metrics']['raw_gate_passed'];lines.append(f"|{r['candidate']} minus {r['reference']}|{x['mean']:.4f}|{x['ci95']}|")
    lines.extend(['','Transitions: '+json.dumps(d['transitions']),'','The pretrained repair retains much more valid geometry than the failed small model, but it does not improve raw motif coverage over the parent. A future experiment could test learned global scaffold adjustment; this is a hypothesis, not a rescue of the closed fixed-scaffold recipe.']);a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n');print(json.dumps(dict(contrasts=d['contrasts'],transitions=d['transitions'])))


if __name__=='__main__':main()
