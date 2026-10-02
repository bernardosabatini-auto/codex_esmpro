"""Report confidence chunking feasibility without a same-hardware speed claim."""
import argparse,json
from pathlib import Path


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();path=a.runs[0]/'manifest.json';m=json.loads(path.read_text()) if path.exists() else dict(status='failed',error='missing manifest');d=dict(status=m['status'],qualified=False)
    if m['status']=='complete':
        if len(m['records'])!=8 or len({r['id'] for r in m['records']})!=8:raise ValueError('incomplete confidence controls')
        d.update(qualified=m['qualified'],records=m['records'],elapsed_seconds=m['elapsed_seconds'],max_reserved_gib=max(r['peak_reserved_bytes'] for r in m['batches'])/1024**3,max_allocated_gib=max(r['peak_allocated_bytes'] for r in m['batches'])/1024**3,measured_seconds=sum(r['seconds'] for r in m['batches']))
    else:d['error']=m.get('error','incomplete profile')
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');lines=['# Teacher confidence chunking','',f"Status: {d['status']}; qualified: {d['qualified']}.",'','Same16 structure draws; only confidence computation chunked by4. Saved full-confidence comparisons cross hardware. No same-hardware latency ratio, full AE-pipeline qualification, changed active data jobs or student-quality claim.']
    if d['status']=='complete':
        lines+=['',f"Peak reserved{d['max_reserved_gib']:.3f}GiB, allocated{d['max_allocated_gib']:.3f}GiB; measured{d['measured_seconds']:.2f}s; worker wall{d['elapsed_seconds']:.2f}s."]
        for r in d['records']:lines+=['',f"{r['id']}: passed{r['passed']}, CA-RMSDmax{r['max_ca_rmsd']:.6g}, pLDDT-RMSE{r['confidence_rmse']:.6g}; geometry/core/eligibility/eligible-state identity {r['validity_exact']}/{r['confident_mask_exact']}/{r['eligibility_exact']}/{r['states_exact']}."]
    else:lines+=['',d['error']]
    a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
