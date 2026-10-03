"""Independent, length-stratified source-family comparison with fixed denominators."""
import argparse
import json
from pathlib import Path

import numpy as np

from prepare_overfit import sha


def summarize(records, seed=2026100381):
    if len(records)!=128 or len({r['target_id'] for r in records})!=128 or len({r['family'] for r in records})!=128:
        raise ValueError('Expected128 distinct source families')
    arrays={};summary=[]
    for arm in ('original512','added7429'):
        for bucket in (128,256,384,512):
            rows=sorted((r for r in records if r['arm']==arm and r['bucket']==bucket),key=lambda r:r['target_id'])
            if len(rows)!=16:
                raise ValueError('Missing source stratum')
            for key in ('scaffold_joint_success','valid_designable'):
                if any(type(r[key]) is not bool for r in rows):
                    raise ValueError('Expected binary source outcomes')
                arrays[arm,bucket,key]=np.array([r[key] for r in rows],float)
            summary.append(dict(arm=arm,bucket=bucket,proteins=16,
                                strong_joint=sum(r['scaffold_joint_success'] for r in rows),
                                designable=sum(r['valid_designable'] for r in rows)))
    contrasts=[]
    for key in ('scaffold_joint_success','valid_designable'):
        rng=np.random.default_rng(seed);draws=np.zeros(10000);estimate=0.
        for bucket in (128,256,384,512):
            a=arrays['original512',bucket,key];b=arrays['added7429',bucket,key]
            estimate+=(b.mean()-a.mean())/4
            draws+=(b[rng.integers(16,size=(10000,16))].mean(1)-a[rng.integers(16,size=(10000,16))].mean(1))/4
        contrasts.append(dict(metric=key,added_minus_original=float(estimate),ci95=np.quantile(draws,[.025,.975]).tolist(),
                              bootstrap='Independent families within length strata, equal bucket weights'))
    return summary,contrasts


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--runs',type=Path,nargs=4,required=True)
    parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();root=Path(__file__).resolve().parents[1]
    records=[];partitions=set();inventories=set();sources=[]
    for run in args.runs:
        run=run.resolve();mp=run/'manifest.json';rp=root/'reports'/(run.name+'.json')
        manifest=json.loads(mp.read_text());report=json.loads(rp.read_text())
        if manifest['status']!='complete' or report['status']!='complete' or report['completed_refolds']!=256:
            raise ValueError('Incomplete source assay')
        if report['manifest_sha256']!=sha(mp) or report['refolded_sha256']!=sha(run/'refolded.h5'):
            raise ValueError('Changed audited source results')
        partitions.add(report['partition']);inventories.add(report['inventory_sha256'])
        records.extend(report['records']);sources.append(dict(path=str(rp),sha256=sha(rp)))
    if partitions!=set(range(4)) or len(inventories)!=1:
        raise ValueError('Mismatched source experiments')
    summary,contrasts=summarize(records)
    report=dict(status='complete',summary=summary,contrasts=contrasts,sources=sources,
                scope='Training-only source calibration. Both cohorts use eight fixed20-motif designs per backbone. No generated/evaluation target labels. Source quality is not generator performance.')
    args.output.with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n')
    lines=['# Training-source designability calibration','',report['scope'],'',
           '|Source corpus|Valid global refold /64|Same valid motif + global + scaffold /64|',
           '|---|---:|---:|']
    for arm in ('original512','added7429'):
        rows=[r for r in summary if r['arm']==arm]
        lines.append(f"|{arm}|{sum(r['designable'] for r in rows)}|{sum(r['strong_joint'] for r in rows)}|")
    for contrast in contrasts:
        lines.extend(['',f"{contrast['metric']}: added minus original {contrast['added_minus_original']:.3f}; 95% interval {contrast['ci95']}."])
    args.output.with_suffix('.md').write_text('\n'.join(lines)+'\n');print(json.dumps(report))


if __name__=='__main__':
    main()
