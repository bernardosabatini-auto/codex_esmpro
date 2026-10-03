"""New frozen-conditioner assays versus immutable full and6000-update controls."""
import argparse
import json
from pathlib import Path

from compare_extra_fragment_refolds import summarize, designability_summary
from extra_fragment_design_panel import audit_refold_plan, designability_ids
from prepare_overfit import sha


def load_partitions(root, paths):
    reports=[];configs=[];sources=[]
    for path in paths:
        d=json.loads(path.read_text());run=root/'runs'/path.stem;mp=run/'manifest.json'
        if d['status']!='complete' or d['manifest_sha256']!=sha(mp) or d['refolded_sha256']!=sha(run/'refolded.h5'):
            raise ValueError('Unaudited refold partition')
        reports.append(d);configs.append(json.loads(mp.read_text())['config'])
        sources.append(dict(path=str(path),sha256=sha(path)))
    ids=[i for d in reports for i in d['target_ids']]
    if len(reports)!=4 or {d['partition'] for d in reports}!=set(range(4)) or len(ids)!=64 or len(set(ids))!=64 or len({d['generation_inventory_sha256'] for d in reports})!=1:
        raise ValueError('Overlapping or mismatched refold partitions')
    specs=[json.loads(Path(c['protocol']).read_text()) for c in configs]
    if any(s!=specs[0] for s in specs):raise ValueError('Changed generation protocol across partitions')
    return reports,configs,specs[0],sources


def project(reports, arms, *, rename=None, raw_only=False):
    rename=rename or {}
    screen=[dict(r,arm=rename.get(r['arm'],r['arm'])) for d in reports for r in d['screen_rows'] if r['arm'] in arms]
    records=[dict(r,arm=rename.get(r['arm'],r['arm'])) for d in reports for r in d['records']
             if r['arm'] in arms and (not raw_only or r['raw_gate_passed'])]
    return screen,records


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--runs',type=Path,nargs=4,required=True)
    parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();root=Path(__file__).resolve().parents[1]
    protocol=root/'configs/fragment_frozen_comparison_protocol.json';plan=json.loads(protocol.read_text())
    for key in ('generation_protocol','full_comparison','parent_comparison'):
        if sha(plan[key])!=plan[key+'_sha256']:raise ValueError('Changed declared comparison source')
    new,configs,spec,sources=load_partitions(root,[root/'reports'/(p.name+'.json') for p in args.runs])
    if spec!=json.loads(Path(plan['generation_protocol']).read_text()) or set(spec['parents'])!=set(plan['new_arms']):
        raise ValueError('Wrong frozen generation experiment')
    audit_refold_plan(spec)
    previous={key:json.loads(Path(plan[key]).read_text()) for key in ('full_comparison','parent_comparison')}
    reused={};reused_specs={}
    for key,comparison in previous.items():
        for row in comparison['source_reports']:
            if sha(row['path'])!=row['sha256']:raise ValueError('Changed reused refold report')
        ds,cs,oldspec,old_sources=load_partitions(root,[Path(r['path']) for r in comparison['source_reports']])
        for field in ('encoded_cohort','seed','historical_seed','samples','steps','decoder_steps','batch_size','guidance','condition'):
            if oldspec[field]!=spec[field]:raise ValueError('Unmatched historical generation recipe: '+field)
        for c in configs:
            old=next(q for q in cs if q['partition']==c['partition'])
            for field in ('fragments_sha256','target_ids','num_sequences','temperature','mpnn_seed','seed','mpnn','dependencies','teacher_artifacts','precision','usalign_sha256'):
                if old[field]!=c[field]:raise ValueError('Unmatched historical assay inputs: '+field)
        reused[key]=ds;reused_specs[key]=oldspec;sources.extend(old_sources)
    native={i:r for d in new for i,r in d['native_controls'].items()}
    if any({i:r for d in ds for i,r in d['native_controls'].items()}!=native for ds in reused.values()):
        raise ValueError('Native attempts changed or pooled')
    ns,nr=project(new,plan['new_arms']);fs,fr=project(reused['full_comparison'],plan['full_arms'])
    screen=fs+ns;records=fr+nr;arms=plan['full_arms']+plan['new_arms']
    panel=designability_ids(spec,{r['target_id']:dict(length=r['length']) for r in screen})
    if panel!=set(previous['full_comparison']['fixed_panel_designability']['target_ids']):
        raise ValueError('Changed prospective designability panel')
    summaries,contrasts=summarize(screen,records,native,arms=arms,pairs=plan['matched_pairs'],designability_targets=panel)
    designability=designability_summary(screen,records,panel,arms,plan['matched_pairs'])
    ps,pr=project(reused['parent_comparison'],[plan['parent_arm']],rename={plan['parent_arm']:'parent6000'},raw_only=True)
    parent_spec=reused_specs['parent_comparison']
    if parent_spec.get('drop_fragment',{}).get(plan['parent_arm'],False):raise ValueError('Unconditioned frontier is not the declared parent')
    frontier_summaries,frontier_contrasts=summarize(ps+ns,pr+[r for r in nr if r['raw_gate_passed']],native,
                                                 arms=['parent6000']+plan['new_arms'],pairs=plan['frontier_pairs'])
    result=dict(status='complete',protocol_sha256=sha(protocol),source_reports=sources,
                summaries=summaries,paired_family_contrasts=contrasts,fixed_panel_designability=designability,
                frontier_summaries=frontier_summaries,frontier_paired_family_contrasts=frontier_contrasts,
                new_refolds=sum(d['completed_refolds'] for d in new),reused_full_model_refolds=len(fr)*8,
                reused_parent_model_refolds=len(pr)*8,native_controls=native,
                successful_scaffold_diversity=[r for d in new for r in d['successful_scaffold_diversity']],
                scope='Repeated64-family development panel, not independent confirmation. Full256sample denominators. Same-refold motif/global/scaffold gates. Fixed32-panel designability only for new and matched-full arms; parent lacks this panel. Original eight-attempt budgets reused without pooling; teacher RNG is not claimed paired. No evaluation labels train models.')
    args.output.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
    lines=['# Frozen learned-generator result','',result['scope'],'',
           '|Arm|Raw retained /256|Strong same-refold /256|Successful families|Fixed-panel designability /32|',
           '|---|---:|---:|---:|---:|']
    panel_counts={r['arm']:r['valid_designable'] for r in designability['summaries'] if r['cohort']=='all'}
    allrows=[r for r in frontier_summaries if r['cohort']=='all' and r['arm']=='parent6000']+[r for r in summaries if r['cohort']=='all']
    for r in allrows:
        lines.append(f"|{r['arm']}|{r['raw_matches']}|{r['scaffold_successes']}|{r['successful_families']}|{panel_counts.get(r['arm'],'unmeasured')}|")
    for contrast in contrasts+frontier_contrasts:
        if contrast['cohort']=='all':
            metric=contrast['scaffold_joint_success'];lines.extend(['',f"{contrast['candidate_arm']} minus {contrast['baseline_arm']}: {metric['mean']:.4f}, family-bootstrap95% interval {metric['ci95']}."])
    args.output.with_suffix('.md').write_text('\n'.join(lines)+'\n');print(json.dumps(allrows))


if __name__=='__main__':main()
