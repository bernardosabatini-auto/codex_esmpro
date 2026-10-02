"""Bind both matched full/geometry pairs to the unchanged tuning screen."""
import argparse,json
from pathlib import Path
from prepare_overfit import sha
from compare_local_geometry import compare
from latentfold.teacher_states import audited_families


def main():
    p=argparse.ArgumentParser();p.add_argument('--full',nargs=2,type=Path,required=True);p.add_argument('--candidate',nargs=2,type=Path,required=True);p.add_argument('--step',type=int,choices=(500,2000),required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1]
    runs=a.full+a.candidate;manifests=[json.loads((run/'manifest.json').read_text()) for run in runs];comparison=compare(manifests[:2],manifests[2:],a.step)
    # The training protocol mandates accuracy checks at both endpoints, regardless of capacity pass/fail.
    report=root/'runs/local_geometry_native_snapshots'/f'capacity_{a.step}.json';report.parent.mkdir(parents=True,exist_ok=True)
    if report.exists() and json.loads(report.read_text())!=comparison:raise ValueError('frozen capacity evidence differs')
    if not report.exists():report.write_text(json.dumps(comparison,indent=2)+'\n')
    original=json.loads((root/'runs/euler_schedule_config.json').read_text());selection=json.loads(Path(original['selection']).read_text());tuning={r['id'] for r in selection['tuning']};tf={r['family'] for r in selection['tuning']}
    c={k:original[k] for k in ('selection','selection_sha256','embedding_cache','seed','evaluation_seed','baseline_manifest','baseline_manifest_sha256','checkpoint_sha256')}
    identity=original['inference_checkpoint'];heads=[dict(name='original',checkpoint=identity['path'],checkpoint_sha256=identity['sha256'],source_sha256=identity['source_sha256'])]
    for run,m in zip(runs,manifests):
        config=m['config'];families=audited_families(config)
        if set(families)&tuning or set(families.values())&tf:raise ValueError('training/tuning overlap')
        name=f"seed{config['seed']}_{'geometry' if config.get('local_geometry') else 'full'}";snapshot=report.parent/f'{run.name}_{a.step}.json'
        if not snapshot.exists():snapshot.write_text(json.dumps(m,indent=2)+'\n')
        frozen=json.loads(snapshot.read_text())
        if frozen['config']!=config or [r for r in frozen['scores'] if r['step'] in (0,a.step)]!=[r for r in m['scores'] if r['step'] in (0,a.step)]:raise ValueError('checkpoint provenance changed')
        checkpoint=(run/f'ema_{a.step}.ckpt').resolve()
        heads.append(dict(name=name,checkpoint=str(checkpoint),checkpoint_sha256=sha(checkpoint),training_manifest=str(snapshot),training_manifest_sha256=sha(snapshot)))
    protocol=root/'configs/local_geometry_native_protocol.json';expected=json.loads(protocol.read_text())['heads']
    if len(heads)!=len(expected) or {h['name'] for h in heads}!=set(expected):raise ValueError('both priors and seeds required')
    heads.sort(key=lambda h:expected.index(h['name']))
    c.update(heads=heads,protocol=str(protocol),protocol_sha256=sha(protocol),capacity_report=str(report),capacity_report_sha256=sha(report),training_family_count=122,training_checkpoint_step=a.step,work_cap_seconds=780)
    a.output.write_text(json.dumps(c,indent=2)+'\n');print(json.dumps(dict(step=a.step,matched=comparison['matched'],heads=expected)))


if __name__=='__main__':main()
