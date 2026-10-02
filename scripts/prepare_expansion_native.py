"""Freeze both larger-data seed checkpoints for the unchanged tuning screen."""
import argparse,json
from pathlib import Path
from compare_expansion_training import compare
from prepare_overfit import sha
from latentfold.teacher_states import audited_families


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--runs',type=Path,nargs=2,required=True);p.add_argument('--step',type=int,choices=(500,2000),required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1]
    ms=[json.loads((r/'manifest.json').read_text()) for r in a.runs];comparison=compare(ms,a.step)
    folder=root/'runs/expansion_native_snapshots';folder.mkdir(exist_ok=True);report=folder/f'capacity_{a.step}.json'
    if report.exists() and json.loads(report.read_text())!=comparison:raise ValueError('capacity evidence changed')
    if not report.exists():report.write_text(json.dumps(comparison,indent=2)+'\n')
    base=json.loads((root/'runs/euler_schedule_config.json').read_text());selection=json.loads(Path(base['selection']).read_text());tuning={r['id'] for r in selection['tuning']};tf={r['family'] for r in selection['tuning']}
    c={k:base[k] for k in ('selection','selection_sha256','embedding_cache','seed','evaluation_seed','baseline_manifest','baseline_manifest_sha256','checkpoint_sha256')};identity=base['inference_checkpoint'];heads=[dict(name='original',checkpoint=identity['path'],checkpoint_sha256=identity['sha256'],source_sha256=identity['source_sha256'])]
    for run,m in sorted(zip(a.runs,ms),key=lambda pair:pair[1]['config']['seed']):
        config=m['config'];families=audited_families(config)
        if set(families)&tuning or set(families.values())&tf:raise ValueError('training/tuning overlap')
        snapshot=folder/f'{run.name}_{a.step}.json'
        if not snapshot.exists():snapshot.write_text(json.dumps(m,indent=2)+'\n')
        old=json.loads(snapshot.read_text())
        if old['config']!=config or [r for r in old['scores'] if r['step'] in (0,a.step)]!=[r for r in m['scores'] if r['step'] in (0,a.step)]:raise ValueError('checkpoint evidence changed')
        checkpoint=(run/f'ema_{a.step}.ckpt').resolve();heads.append(dict(name=f"seed{config['seed']}_expansion",checkpoint=str(checkpoint),checkpoint_sha256=sha(checkpoint),training_manifest=str(snapshot),training_manifest_sha256=sha(snapshot)))
    protocol=root/'configs/expansion_native_protocol.json';recipe=json.loads(protocol.read_text())
    if [h['name'] for h in heads]!=recipe['heads']:raise ValueError('missing declared seed')
    c.update(heads=heads,protocol=str(protocol),protocol_sha256=sha(protocol),capacity_report=str(report),capacity_report_sha256=sha(report),training_family_count=comparison['training_targets'],training_checkpoint_step=a.step,work_cap_seconds=780)
    a.output.write_text(json.dumps(c,indent=2)+'\n');print(json.dumps(dict(heads=recipe['heads'],step=a.step,capacity_passed=comparison['replicated_capacity_passed'])))


if __name__=='__main__':main()
