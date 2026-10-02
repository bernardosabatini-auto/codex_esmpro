"""Bind a quality-qualified ensemble to a fresh matched timing comparison."""
import argparse,json
from pathlib import Path
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--ensemble',type=Path,required=True);p.add_argument('--comparison',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--student-inference-identity',type=Path);p.add_argument('--protocol',type=Path);a=p.parse_args()
    comparison=json.loads(a.comparison.read_text());path=a.ensemble/'manifest.json';m=json.loads(path.read_text());c=m['config']
    if comparison['status']!='complete' or not comparison['sampling_quality_gate_passed'] or m['status']!='complete':raise ValueError('ensemble quality prerequisite failed')
    for side in ('candidate','reference'):
        if sha(comparison[side])!=comparison[side+'_sha256']:raise ValueError('ensemble scores changed')
    job=a.ensemble.name.removeprefix('ensemble_')
    if Path(comparison['candidate']).parent.name!='state_scores_'+job or comparison['candidate_setting']!=f"cfg{c['primary_guidance']}/latent" or comparison['reference_setting']!='cfg2/latent':raise ValueError('comparison does not match this ensemble')
    if sha(c['checkpoint'])!=c['checkpoint_sha256']:raise ValueError('checkpoint changed')
    config=json.loads(Path('runs/ensemble_latency_config.json').read_text())
    if c['panel_sha256']!=config['panel_sha256'] or c['seed']!=config['seed']:raise ValueError('timing/ensemble panel or noise mismatch')
    reference=(a.ensemble/'predictions.h5').resolve()
    config.update(candidate_checkpoint=c['checkpoint'],candidate_checkpoint_sha256=c['checkpoint_sha256'],candidate_reference=str(reference),candidate_reference_sha256=sha(reference),candidate_steps=c['flow_steps'],candidate_guidance=c['primary_guidance'],candidate_solver=c.get('flow_solver','euler'),candidate_time_power=c.get('flow_time_power',1),candidate_compact_condition=c.get('compact_condition',False),include_expanded_candidate=c.get('compact_condition',False),quality_report=str(a.comparison.resolve()),quality_report_sha256=sha(a.comparison),candidate_manifest=str(path.resolve()),candidate_manifest_sha256=sha(path),work_cap_seconds=1680)
    if a.student_inference_identity:
        identity=json.loads(a.student_inference_identity.read_text());baseline=json.loads((Path(config['student_reference']).parent/'manifest.json').read_text())
        if identity['source_sha256']!=baseline['checkpoint']['sha256'] or not identity['tensor_values_verified'] or sha(identity['path'])!=identity['sha256']:raise ValueError('baseline inference weights changed')
        config.update(student_checkpoint=identity['path'],student_checkpoint_sha256=identity['sha256'],student_checkpoint_source_sha256=identity['source_sha256'])
    if a.protocol:config.update(timing_protocol=str(a.protocol.resolve()),timing_protocol_sha256=sha(a.protocol))
    a.output.write_text(json.dumps(config,indent=2)+'\n')


if __name__=='__main__':main()
