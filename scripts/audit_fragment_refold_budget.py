"""Retrospective fixed-prefix and first-valid teacher-call costs; no new selection."""
import argparse
import json
from pathlib import Path
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--comparison',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    comparison=json.loads(a.comparison.read_text())
    if comparison['status']!='complete':raise ValueError('Incomplete source comparison')
    sources={str(a.comparison):sha(a.comparison)};screen={};records={}
    for source in comparison['source_reports']:
        path=Path(source['path'])
        if sha(path)!=source['sha256']:raise ValueError('Changed refold report')
        d=json.loads(path.read_text());sources[str(path)]=sha(path)
        if d['status']!='complete':raise ValueError('Incomplete partition')
        for key,rows,inventory in [('screen_rows',d['screen_rows'],screen),('records',d['records'],records)]:
            for r in rows:
                if r['arm']=='native':continue
                k=(r['arm'],r['target_id'],r['generation_slot'])
                if k in inventory and inventory[k]!=r:raise ValueError('Inconsistent reused sample')
                inventory[k]=r
    summary=[]
    for arm in sorted({k[0] for k in screen}):
        rows=[r for k,r in screen.items() if k[0]==arm]
        raw=[k for k,r in screen.items() if k[0]==arm and r['raw_gate_passed']]
        if any(k not in records or not records[k]['raw_gate_passed'] for k in raw):raise ValueError('Missing raw-match assay')
        earliest=[]
        for k in raw:
            r=records[k];indices=r['scaffold_successful_refold_indices']
            if len(r['refolds'])!=8 or any(i not in range(8) for i in indices):raise ValueError('Changed eight-design budget')
            earliest.append(min(indices)+1 if indices else 9)
        for budget in (1,2,4,8):
            successes=sum(i<=budget for i in earliest)
            summary.append(dict(arm=arm,generations=len(rows),raw_matches=len(raw),sequence_budget=budget,
                                strong_successes=successes,teacher_calls_fixed_prefix=budget*len(raw),
                                teacher_calls_first_valid=sum(min(i,budget) for i in earliest),
                                teacher_calls_per_success=(sum(min(i,budget) for i in earliest)/successes if successes else None)))
    result=dict(status='complete',sources=sources,summary=summary,
                scope='Retrospective development diagnostic using original ordered sequences only. Every generation remains in the denominator; raw failures are rejected before sequence design for this hypothetical deployment cost. First-valid stops only after one same-valid-refold passes motif/global/scaffold gates. Excludes generation,MPNN,startup and numerical-control costs; teacher-call counts are not wall-clock performance. No attempts pooled, candidates reranked, assay budgets changed or optimal budget selected from these outcomes.')
    a.output.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
    lines=['# Fixed-prefix refolding cost audit','',result['scope'],'',
           '|Arm|Design budget|Strong /256|Raw matches|Fixed-prefix calls|First-valid calls|Calls/success|',
           '|---|---:|---:|---:|---:|---:|---:|']
    for r in summary:
        if r['generations']!=256:raise ValueError('Unexpected generation denominator')
        cost='undefined' if r['teacher_calls_per_success'] is None else f"{r['teacher_calls_per_success']:.1f}"
        lines.append(f"|{r['arm']}|{r['sequence_budget']}|{r['strong_successes']}|{r['raw_matches']}|{r['teacher_calls_fixed_prefix']}|{r['teacher_calls_first_valid']}|{cost}|")
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n');print(json.dumps(summary))


if __name__=='__main__':main()
