"""Descriptive native outcomes in the four pre-existing length strata."""
import argparse,json
from pathlib import Path
import numpy as np
from diagnose_native_failures import analyze,LIMITS


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',nargs='+',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();results={}
    for path in a.runs:
        checked=analyze(path/'manifest.json');m=json.loads((path/'manifest.json').read_text());c=m['config']
        targets={r['id']:r for r in json.loads(Path(c['selection']).read_text())['tuning']}
        rows=[];baseline={b:[r for r in m['scores'] if r['head']=='original' and r['guidance']==2 and targets[r['target_id']]['bucket']==b] for b in (128,256,384,512)}
        for head,guidance in sorted({(r['head'],r['guidance']) for r in m['scores']}):
            for bucket in baseline:
                group=[r for r in m['scores'] if (r['head'],r['guidance'])==(head,guidance) and targets[r['target_id']]['bucket']==bucket]
                if len(group)!=48 or len({r['target_id'] for r in group})!=16:raise ValueError('length stratum coverage differs')
                ca=float(np.mean([r['ca_lddt'] for r in group]));base=float(np.mean([r['ca_lddt'] for r in baseline[bucket]]))
                rows.append(dict(head=head,guidance=guidance,bucket=bucket,families=16,samples=48,ca_lddt=ca,ca_difference=ca-base,invalid=sum(not r['coarse_valid'] for r in group),original_invalid=sum(not r['coarse_valid'] for r in baseline[bucket]),ca_clashes=sum(r['ca_clashing_residue_fraction']>LIMITS['ca_clashing_residue_fraction'] for r in group)))
        results[path.name]=dict(manifest_sha256=checked['manifest_sha256'],step=checked['step'],rows=rows)
    d=dict(scope='Descriptive length-stratum diagnostics only; unchanged pooled native gate. All64 tuning families and all3 samples retained. No locked-test outcomes.',runs=results)
    lines=['# Native accuracy and geometry by existing length stratum','',d['scope'],'']
    for name,data in results.items():
        lines += [name+'; checkpoint'+str(data['step']), '', '| Head / CFG | Bucket | CA-lDDT | CA difference | Invalid /48 | Original invalid /48 | CA clashes |','|---|---:|---:|---:|---:|---:|---:|']
        for r in data['rows']:lines.append(f"| {r['head']} /{r['guidance']} | {r['bucket']} | {r['ca_lddt']:.5f} | {r['ca_difference']:+.5f} | {r['invalid']} | {r['original_invalid']} | {r['ca_clashes']} |")
        lines.append('')
    lines+=['Three samples per family and16 families per stratum do not establish the cause of a regression. Length-dependent patterns are exploratory; no stratum is omitted or given a revised qualification threshold.']
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('\n'.join(lines)+'\n')


if __name__=='__main__':main()
