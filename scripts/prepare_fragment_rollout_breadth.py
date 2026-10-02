"""Profile the same rollout objective on a designability-qualified broader corpus."""
import argparse,json
from pathlib import Path
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--designability-report',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];baseline=root/'runs/fragment_training_49951202/manifest.json';report=root/'reports/fragment_training_49951202.json';d=json.loads(report.read_text());m=json.loads(baseline.read_text());assay=json.loads(a.designability_report.read_text());assay_manifest=root/'runs'/a.designability_report.stem/'manifest.json';am=json.loads(assay_manifest.read_text())
    if d['status']!='complete' or d['manifest_sha256']!=sha(baseline) or not m['config'].get('expanded_fragment_data'):raise ValueError('Unqualified broader corpus control')
    if assay['status']!='complete' or not assay['positive_controls_passed'] or assay['manifest_sha256']!=sha(assay_manifest) or am['config']['generation_manifest_sha256']!=sha(baseline) or am['config'].get('training_step',2000)!=2000:raise ValueError('Unqualified designability evidence')
    if next(r for r in assay['summaries'] if r['mode']=='conditioned')['valid_designable']['count']<4:raise ValueError('Broader-data designability screen failed')
    c=m['config'].copy()
    for key in ('profile_report','profile_report_sha256','allocation_minutes'):c.pop(key,None)
    protocol=root/'configs/fragment_rollout_protocol.json';c.update(profile_only=True,updates=40,evaluation_steps=[40],work_cap_seconds=780,rollout_motif=json.loads(protocol.read_text())['auxiliary'])
    for key,path in [('rollout_protocol',protocol),('rollout_breadth_protocol',root/'configs/fragment_rollout_breadth_protocol.json'),('rollout_breadth_gate_report',a.designability_report),('rollout_breadth_gate_manifest',assay_manifest),('rollout_control_manifest',baseline)]:c[key]=str(path.resolve());c[key+'_sha256']=sha(path)
    a.output.write_text(json.dumps(c,indent=2)+'\n')

if __name__=='__main__':main()
