"""Fixed-denominator retrieval versus random-code designability diagnostic."""
import argparse,json
from pathlib import Path
import h5py
import numpy as np
from compare_native_anchor_models import verify_outcome
from compare_extra_fragment_refolds import clustered
from fragment_junction_core import flank_bonds
from latentfold.connected_refold import connected_outcome
from prepare_fragment_preference_refold import TEACHER_KEYS,audit_inputs
from prepare_overfit import sha


def gate(totals):
    a,b,p=(totals[k] for k in ('retrieved','random','parent6000'))
    if (p['strong'],p['strong_families'],p['designable'])!=(8,7,45):raise ValueError('Changed parent comparator')
    return dict(strict=a['strong']>max(p['strong'],b['strong']),families=a['strong_families']>=7,
                designability=a['designable']>=max(45,b['designable']))


def analyze(root,jobs):
    ids=[j for values in jobs.values() for j in values]
    registry={j['id']:j for j in json.loads((root/'runs/jobs.json').read_text())['jobs']}
    if (set(jobs)!={'retrieved','random'} or any(len(v)!=4 for v in jobs.values()) or len(set(ids))!=8
            or any(j not in registry or registry[j]['completion_action']!='summarize_fragment_preference_refold' for j in ids)):
        raise ValueError('Eight distinct registered own refold jobs required')
    bp=root/'reports/fragment_preference_comparison_20261003.json';base=json.loads(bp.read_text())
    if base['status']!='complete' or any(sha(s['report'])!=s['report_sha256'] for s in base['sources']):raise ValueError('Changed original parent')
    paths={'parent6000':[Path(s['report']) for s in base['sources']]}
    paths.update({arm:[root/f'reports/fragment_preference_refold_{j}.json' for j in values] for arm,values in jobs.items()})
    arms={};configs={};sources=[];generation_hash=None;native_sources=None
    for arm,reports in paths.items():
        rows=[];parts=set();cached=None
        for path in reports:
            run=root/'runs'/path.stem;mp=run/'manifest.json';m=json.loads(mp.read_text());d=json.loads(path.read_text());c=m['config']
            gc,spec=audit_inputs(c,audited_generation=cached);cached=(gc,spec)
            if (m['status']!='complete' or d['status']!='complete' or d['manifest_sha256']!=sha(mp)
                    or d['refolded_sha256']!=sha(run/'refolded.h5') or d['completed_refolds']!=256 or len(d['records'])!=32
                    or c['partition'] in parts or d['partition']!=c['partition'] or gc['arm']!=arm
                    or not m['teacher_deterministic_algorithms'] or d['generation_manifest_sha256']!=c['generation_manifest_sha256']
                    or [r['name'] for r in d['records']]!=[r['name'] for r in c['entries']]):raise ValueError('Changed partition, recipe or inventory')
            if arm=='parent6000':native_sources=gc['native_sources']
            else:
                if not d.get('retrieved_context_refold') or not m.get('cpu_preflight_file_identity_unchanged'):raise ValueError('Wrong assay')
                if native_sources!=gc['native_sources']:raise ValueError('Changed native budgets')
                if generation_hash is not None and generation_hash!=c['generation_manifest_sha256']:raise ValueError('Mixed generations')
                generation_hash=c['generation_manifest_sha256']
            parts.add(c['partition']);configs[arm,c['partition']]=c;sources.append(dict(path=str(path),sha256=sha(path)))
            with h5py.File(c['predictions']) as raw,h5py.File(run/'refolded.h5') as folded:
                for r in d['records']:
                    if r['arm']!=arm or len(r['refolds'])!=8:raise ValueError('Changed arm or attempts')
                    verify_outcome(r)
                    edges=flank_bonds(raw[r['dataset']][0],r['motif_start'],len(r['fixed_sequence']),8)
                    for k,row in enumerate(r['refolds']):
                        row['flank_edges_valid']=flank_bonds(folded[r['name']+'/'+str(k)][:],r['motif_start'],len(r['fixed_sequence']),8)['all_edges_valid']
                    expected=connected_outcome(r['raw'],r['refolds'],physical_raw=r['raw']['coarse_valid'] and edges['all_edges_valid'])
                    if arm!='parent6000' and any(r[k]!=v for k,v in expected.items()):raise ValueError('Changed connectivity diagnostic')
                    r.update(expected);rows.append(r)
        wanted={(r['id'],s) for r in gc['selected'] for s in range(4)}
        if parts!=set(range(4)) or len(rows)!=128 or {(r['target_id'],r['generation_slot']) for r in rows}!=wanted:
            raise ValueError('Incomplete128-case denominator')
        arms[arm]=rows
    fields=('target_id','family','length','generation_slot','fixed_start','fixed_sequence','repeatability_control')
    for arm in jobs:
        for part in range(4):
            a,b=configs[arm,part],configs['parent6000',part]
            if any(a[k]!=b[k] for k in TEACHER_KEYS) or any(x[k]!=y[k] for x,y in zip(a['entries'],b['entries']) for k in fields):
                raise ValueError('Unmatched teacher, targets or original fixed sequence')
    summary=[];contrasts=[]
    metrics=('raw_gate_passed','scaffold_joint_success','valid_designable','complete_strict','connected_designable','complete_connected_designable')
    for bucket in (None,128,256,384,512):
        subset={a:[r for r in rows if bucket is None or r['bucket']==bucket] for a,rows in arms.items()}
        for arm,rows in subset.items():
            summary.append(dict(arm=arm,bucket=bucket,samples=len(rows),raw=sum(r['raw_gate_passed'] for r in rows),
                strong=sum(r['scaffold_joint_success'] for r in rows),designable=sum(r['valid_designable'] for r in rows),
                strong_families=len({r['family'] for r in rows if r['scaffold_joint_success']}),
                **{k:sum(r[k] for r in rows) for k in metrics[3:]}))
        families=sorted({r['family'] for r in subset['parent6000']})
        for candidate,ref in [('retrieved','parent6000'),('random','parent6000'),('retrieved','random')]:
            contrasts.append(dict(bucket=bucket,candidate=candidate,reference=ref,metrics={k:clustered([
                np.mean([r[k] for r in subset[candidate] if r['family']==f])-np.mean([r[k] for r in subset[ref] if r['family']==f])
                for f in families]) for k in metrics}))
    passing={a:{(r['target_id'],r['generation_slot']) for r in rows if r['scaffold_joint_success']} for a,rows in arms.items()}
    overlaps=[dict(candidate=a,reference=b,shared=len(passing[a]&passing[b]),candidate_only=len(passing[a]-passing[b]),reference_only=len(passing[b]-passing[a]))
              for a,b in [('retrieved','parent6000'),('random','parent6000'),('retrieved','random')]]
    qualified=gate({r['arm']:r for r in summary if r['bucket'] is None})
    return dict(status='complete',source_reports=sources,baseline_comparison_sha256=sha(bp),summary=summary,contrasts=contrasts,
        overlaps=overlaps,gate=qualified,qualified=all(qualified.values()),records=arms,new_refolds=2048,reused_parent_refolds=1024,
        native=dict(budgets_reused=base['native_budgets_reused'],global_scaffold=base['native_global_scaffold'],controls=base['native']),
        scope='Repeated training-protein diagnostic, not novel-protein generalization. Retrieval excludes all query and validation families. '
              'All128 outputs per arm, eight fixed-original-motif designs each; all failures retained. Strict success requires one valid refold with '
              'motif/global/scaffold agreement. Connectivity is an additional shared diagnostic, not a replacement endpoint. '
              'Parent uses different conditioning; retrieval versus random is the matched contrast. '
              'Donor rank and flow noise both vary across four slots. Qualification licenses a separate replication, not a learned-model claim.')


def main():
    p=argparse.ArgumentParser();p.add_argument('--retrieved',nargs=4,required=True);p.add_argument('--random',nargs=4,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    d=analyze(Path(__file__).resolve().parents[1],dict(retrieved=a.retrieved,random=a.random))
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n')
    lines=['# Retrieved native-code designability','',d['scope'],'','|Arm|Raw|Strict|Designable|Strict families|Connected strict|',
           '|---|---:|---:|---:|---:|---:|']
    for r in d['summary']:
        if r['bucket'] is None:lines.append(f"|{r['arm']}|{r['raw']}|{r['strong']}|{r['designable']}|{r['strong_families']}|{r['complete_strict']}|")
    lines+=['','Gate: '+json.dumps(d['gate'])]
    for r in d['contrasts']:
        if r['bucket'] is None:lines+=['',r['candidate']+' minus '+r['reference']+': '+json.dumps(r['metrics'])]
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n');print(json.dumps(d['gate']))


if __name__=='__main__':main()
