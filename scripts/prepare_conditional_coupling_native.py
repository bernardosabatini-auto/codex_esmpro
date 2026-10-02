"""Freeze a qualified coupling pair for the existing separate tuning evaluator."""
import argparse,json
from pathlib import Path
from prepare_overfit import sha
from latentfold.teacher_states import audited_families


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=2,required=True);p.add_argument('--comparison',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    root=Path(__file__).resolve().parents[1];gate=json.loads(a.comparison.read_text())
    if gate['status']!='complete' or not gate['qualified_for_replication_and_native'] or gate['archived_predictions_audited']!=4096 or gate['matched_updates']!=500:raise ValueError('Coupling capacity not qualified')
    if {str(Path(k).resolve()):v for k,v in gate['sources'].items()}!={str((r/'manifest.json').resolve()):sha(r/'manifest.json') for r in a.runs}:raise ValueError('Changed capacity evidence')
    base=json.loads((root/'runs/euler_schedule_config.json').read_text());selection=json.loads(Path(base['selection']).read_text());tuning={r['id'] for r in selection['tuning']};families={r['family'] for r in selection['tuning']}
    c={k:base[k] for k in ('selection','selection_sha256','embedding_cache','seed','evaluation_seed','baseline_manifest','baseline_manifest_sha256','checkpoint_sha256')};identity=base['inference_checkpoint'];heads=[dict(name='original',checkpoint=identity['path'],checkpoint_sha256=identity['sha256'],source_sha256=identity['source_sha256'])]
    for run in a.runs:
        path=run/'manifest.json';m=json.loads(path.read_text());train=audited_families(m['config']);arm=m['config']['conditional_coupling']['arm']
        if len(train)!=32 or set(train)&tuning or set(train.values())&families or m['status']!='complete' or m['updates']!=500:raise ValueError('Invalid training scope or tuning overlap')
        ckpt=(run/'ema_500.ckpt').resolve();heads.append(dict(name=arm,checkpoint=str(ckpt),checkpoint_sha256=sha(ckpt),training_manifest=str(path.resolve()),training_manifest_sha256=sha(path)))
    protocol=root/'configs/conditional_coupling_native_protocol.json';recipe=json.loads(protocol.read_text());heads.sort(key=lambda h:recipe['heads'].index(h['name']))
    if [h['name'] for h in heads]!=recipe['heads']:raise ValueError('Missing or duplicate arm')
    c.update(heads=heads,protocol=str(protocol),protocol_sha256=sha(protocol),capacity_report=str(a.comparison.resolve()),capacity_report_sha256=sha(a.comparison),training_family_count=32,training_checkpoint_step=500,work_cap_seconds=600)
    a.output.write_text(json.dumps(c,indent=2)+'\n')


if __name__=='__main__':main()
