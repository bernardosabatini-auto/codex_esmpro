"""Freeze both capacity-retaining replay heads for the unchanged native panel."""
import argparse,json
from pathlib import Path
from compare_functional_replay import compare
from prepare_overfit import sha
from latentfold.teacher_states import audited_families


def main():
    p=argparse.ArgumentParser();p.add_argument('--full',type=Path,nargs=2,required=True);p.add_argument('--candidate',type=Path,nargs=2,required=True);p.add_argument('--step',type=int,choices=[500,2000],required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1]
    read=lambda paths:[json.loads((p/'manifest.json').read_text()) for p in paths];full=read(a.full);candidates=read(a.candidate);comparison=compare(full,candidates,a.step)
    if not comparison['replicated_capacity_retained']:raise ValueError('both replay seeds must retain capacity')
    folder=root/'runs/replay_native_snapshots';folder.mkdir(exist_ok=True);report=folder/f'capacity_{a.step}.json'
    if report.exists() and json.loads(report.read_text())!=comparison:raise ValueError('capacity evidence changed')
    if not report.exists():report.write_text(json.dumps(comparison,indent=2)+'\n')
    base=json.loads((root/'runs/euler_schedule_config.json').read_text());selection=json.loads(Path(base['selection']).read_text());tuning={r['id'] for r in selection['tuning']};families={r['family'] for r in selection['tuning']}
    c={k:base[k] for k in ('selection','selection_sha256','embedding_cache','seed','evaluation_seed','baseline_manifest','baseline_manifest_sha256','checkpoint_sha256')};identity=base['inference_checkpoint'];heads=[dict(name='original',checkpoint=identity['path'],checkpoint_sha256=identity['sha256'],source_sha256=identity['source_sha256'])]
    for run,m in sorted(zip(a.candidate,candidates),key=lambda x:x[1]['config']['seed']):
        config=m['config'];teacher=audited_families(config);replay=json.loads(Path(config['replay_selection']).read_text())['targets'];all_families=set(teacher.values())|{r['family'] for r in replay};all_ids=set(teacher)|{r['id'] for r in replay}
        if len(all_families)!=817 or all_families&families or all_ids&tuning:raise ValueError('teacher/replay training overlaps tuning')
        snapshot=folder/f'{run.name}_{a.step}.json'
        if not snapshot.exists():snapshot.write_text(json.dumps(m,indent=2)+'\n')
        old=json.loads(snapshot.read_text())
        if old['config']!=config or [r for r in old['scores'] if r['step'] in (0,a.step)]!=[r for r in m['scores'] if r['step'] in (0,a.step)]:raise ValueError('checkpoint evidence changed')
        checkpoint=(run/f'ema_{a.step}.ckpt').resolve();heads.append(dict(name=f"seed{config['seed']}_replay",checkpoint=str(checkpoint),checkpoint_sha256=sha(checkpoint),training_manifest=str(snapshot),training_manifest_sha256=sha(snapshot)))
    protocol=root/'configs/replay_native_protocol.json';recipe=json.loads(protocol.read_text())
    if [h['name'] for h in heads]!=recipe['heads']:raise ValueError('missing declared replay seed')
    plain=root/f"runs/expansion_native_{'49819892' if a.step==500 else '49831486'}/manifest.json"
    c.update(heads=heads,protocol=str(protocol),protocol_sha256=sha(protocol),capacity_report=str(report),capacity_report_sha256=sha(report),training_family_count=427,replay_family_count=390,training_checkpoint_step=a.step,plain_native_manifest=str(plain),plain_native_manifest_sha256=sha(plain),work_cap_seconds=780)
    a.output.write_text(json.dumps(c,indent=2)+'\n')


if __name__=='__main__':main()
