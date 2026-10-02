"""Freeze all matched500-update heads for the separate tuning-panel check."""
import argparse,json
from pathlib import Path
from prepare_overfit import sha
from latentfold.teacher_states import audited_families


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',nargs=4,type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    root=Path(__file__).resolve().parents[1];protocol=root/'configs/overfit_native_protocol.json';gate=root/'reports/overfit_balanced_comparison_500.json';g=json.loads(gate.read_text())
    if g['step']!=500 or not g['matched'] or not all(v['passed'] for v in g['capacity_checks'].values()):raise ValueError('balanced capacity prerequisite failed')
    original=json.loads((root/'runs/euler_schedule_config.json').read_text());selection=json.loads(Path(original['selection']).read_text());tuning={r['id'] for r in selection['tuning']};tf={r['family'] for r in selection['tuning']}
    c={k:original[k] for k in ('selection','selection_sha256','embedding_cache','seed','evaluation_seed','baseline_manifest','baseline_manifest_sha256','checkpoint_sha256')}
    identity=original['inference_checkpoint'];heads=[dict(name='original',checkpoint=identity['path'],checkpoint_sha256=identity['sha256'],source_sha256=identity['source_sha256'])]
    for run in a.runs:
        m=json.loads((run/'manifest.json').read_text());config=m['config'];families=audited_families(config);name=config['arm']+'_'+config.get('label_distribution','empirical')
        if set(families)&tuning or set(families.values())&tf:raise ValueError('training/tuning overlap')
        rows=[r for r in m['scores'] if r['step']==500]
        if m['updates']<500 or len(rows)!=64 or {r['target_id'] for r in rows}!=set(families):raise ValueError('incomplete checkpoint evaluation')
        snapshot=root/'runs/overfit_native_snapshots'/f'{run.name}_500.json';snapshot.parent.mkdir(parents=True,exist_ok=True)
        if not snapshot.exists():snapshot.write_text(json.dumps(m,indent=2)+'\n')
        checkpoint=(run/'ema_500.ckpt').resolve()
        heads.append(dict(name=name,checkpoint=str(checkpoint),checkpoint_sha256=sha(checkpoint),training_manifest=str(snapshot),training_manifest_sha256=sha(snapshot)))
    expected=json.loads(protocol.read_text())['heads']
    if len({h['name'] for h in heads})!=5 or {h['name'] for h in heads}!=set(expected):raise ValueError('all four matched teacher heads required')
    heads.sort(key=lambda h:expected.index(h['name']))
    c.update(heads=heads,protocol=str(protocol),protocol_sha256=sha(protocol),capacity_report=str(gate),capacity_report_sha256=sha(gate),work_cap_seconds=1080)
    a.output.write_text(json.dumps(c,indent=2)+'\n')


if __name__=='__main__':main()
