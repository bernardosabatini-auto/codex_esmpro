"""Report data-generation controls, useful throughput, memory and label audit."""
import argparse,json
from collections import Counter
from pathlib import Path
from expansion_data import reconstruction_summary


def summarize(m):
    rows=m.get('records',[]);new=[r for r in rows if not r['control']]
    complete=m.get('status')=='complete' and len(new)==len(m['config']['targets']) and len(rows)==len(new)+4
    control_counts={key:len(m.get(key,[])) for key in ('controls','embedding_controls','rotation_controls','metric_controls')}
    control_ok=all(v==4 for v in control_counts.values())
    if complete and not control_ok:raise ValueError('incomplete control certificate')
    audit=reconstruction_summary(new) if complete else None
    phases={}
    for phase in ('embedding','teacher','encode_audit'):
        batches=[b for b in m.get('batches',[]) if b['phase']==phase]
        phases[phase]=dict(seconds=sum(b['seconds'] for b in batches),peak_gib=max((b['peak_reserved_bytes']/1024**3 for b in batches),default=0))
    return dict(status='complete' if complete else 'failed',error=m.get('error'),new_targets=len(new),eligible=sum(r.get('eligible',False) for r in new),exclusion_reasons=dict(Counter(r['exclusion_reason'] for r in new if r.get('exclusion_reason'))),control_counts=control_counts,phases=phases,elapsed_seconds=m.get('elapsed_seconds'),reconstruction=audit,generation_qualified=bool(complete and control_ok and m.get('resource_gate_passed')),scope='Data generation controls and fixed-noise reconstruction only; full eligible-corpus reconstruction gate is required before student training.')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();path=a.runs[0]/'manifest.json'
    if path.exists():d=summarize(json.loads(path.read_text()))
    else:d=dict(status='failed',error='missing worker manifest',generation_qualified=False)
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n')
    lines=['# Expansion data generation','',f"Status: {d['status']}; generation qualified: {d['generation_qualified']}."]
    if 'new_targets' in d:
        lines+=['',d['scope'],'',f"New families: {d['new_targets']}; metadata eligible: {d['eligible']}; wall seconds: {d['elapsed_seconds']}.",f"Exclusion counts: {d['exclusion_reasons']}.",'','| Phase | Measured seconds | Peak reserved GiB |','|---|---:|---:|']
        for name,v in d['phases'].items():lines.append(f"| {name} | {v['seconds']:.2f} | {v['peak_gib']:.2f} |")
        lines+=['',f"Control counts: {d['control_counts']}.",f"Reconstruction: {d['reconstruction']}.",'','Phase times include controls and exclude model loading, disk work and CPU bookkeeping; use wall time for allocation planning. Confidence/contact-state criteria exclude labels without using student outcomes. All draws are retained.']
    if d.get('error'):lines+=['',d['error']]
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
