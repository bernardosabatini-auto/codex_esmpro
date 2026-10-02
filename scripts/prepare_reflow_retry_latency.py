"""Bind four-pipeline timing to qualified external evidence and the existing panel."""
import argparse,json
from pathlib import Path
from prepare_overfit import sha
from compare_reflow_retry_ensemble import analyze


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];protocol=root/'configs/reflow_retry_latency_protocol.json';recipe=json.loads(protocol.read_text());external=root/recipe['external_protocol'];report=root/recipe['quality_report']
    if sha(external)!=recipe['external_protocol_sha256'] or sha(report)!=recipe['quality_report_sha256']:raise ValueError('Changed qualifying evidence')
    actual=analyze(root/'runs/retry_ensemble_49850873',root/'runs/state_scores_49850873/score.json',external)
    if actual!=json.loads(report.read_text()) or not actual['sampling_quality_gate_passed']:raise ValueError('External qualification not reproduced')
    previous=root/'runs/ensemble_latency_49774086/manifest.json';old=json.loads(previous.read_text())
    if old['status']!='complete':raise ValueError('Incomplete prior timing panel')
    c={k:old['config'][k] for k in ('panel','panel_sha256','seed','target_ids')};c.update(retry_heads=[],work_cap_seconds=1680)
    for key,path in dict(protocol=protocol,quality_report=report,previous_timing_manifest=previous).items():c[key]=str(path);c[key+'_sha256']=sha(path)
    for name,jid in [('original','49844758'),('compact500','49844801'),('reflow10','49850873')]:
        run=root/('runs/retry_ensemble_'+jid);manifest=run/'manifest.json';m=json.loads(manifest.read_text());settings=m['config']
        if m['status']!='complete' or settings['name']!=name or settings['seed']!=c['seed'] or settings['panel_sha256']!=c['panel_sha256']:raise ValueError('Wrong timing source')
        head={k:settings[k] for k in ('name','checkpoint','checkpoint_sha256','flow_steps','primary_guidance','compact_condition','seed')}
        for key,path in dict(ensemble_manifest=manifest,reference=run/'predictions.h5').items():head[key]=str(path);head[key+'_sha256']=sha(path)
        c['retry_heads'].append(head)
    a.output.write_text(json.dumps(c,indent=2)+'\n');print([h['name'] for h in c['retry_heads']])

if __name__=='__main__':main()
