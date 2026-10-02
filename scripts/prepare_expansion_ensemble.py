"""Advance quality-qualified larger-data settings with both training seeds retained."""
import argparse,json
from pathlib import Path
from prepare_overfit import sha
from summarize_expansion_native import analyze
from latentfold.teacher_states import audited_families


def qualified(capacity, transfer, head, guidance, *, step=500):
    if guidance!=1 or step not in (500,2000):raise ValueError('invalid sampling or endpoint')
    allowed={f'seed{seed}_expansion':str(seed) for seed in (2026100171,2026100181)}
    if head not in allowed:raise ValueError('only declared larger-data seed settings qualify')
    if capacity['step']!=step or not capacity['matched'] or capacity['seeds']!=[2026100171,2026100181]:raise ValueError('paired capacity evidence incomplete')
    if transfer.get('training_targets',0)<=122 or transfer['training_targets']!=capacity['training_targets']:raise ValueError('wrong larger-data tuning comparison')
    setting=head+'_cfg1'
    if transfer['step']!=step or not transfer['summaries'][setting]['quality_passed']:raise ValueError('transfer prerequisite failed')
    return setting


def training_identity(config, head):
    if head!=f"seed{config['seed']}_expansion" or config['label_distribution']!='balanced' or config.get('corpus_kind')!='expansion' or config.get('local_geometry') or config.get('trainable_tail_blocks') is not None:
        raise ValueError('head and training identity differ')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--screen',type=Path,required=True);p.add_argument('--head',required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    path=a.screen/'manifest.json';m=json.loads(path.read_text());c=m['config']
    if m['status']!='complete':raise ValueError('transfer evaluation incomplete')
    if sha(c['capacity_report'])!=c['capacity_report_sha256']:raise ValueError('capacity evidence changed')
    capacity=json.loads(Path(c['capacity_report']).read_text());transfer=analyze(m)
    step=c.get('training_checkpoint_step',500)
    setting=qualified(capacity,transfer,a.head,1,step=step)
    head=next(h for h in c['heads'] if h['name']==a.head)
    for field in ('checkpoint','training_manifest'):
        if sha(head[field])!=head[field+'_sha256']:raise ValueError(f'changed {field}')
    training=json.loads(Path(head['training_manifest']).read_text())
    if Path(head['checkpoint']).name!=f'ema_{step}.ckpt' or training['updates']<step:
        raise ValueError('checkpoint endpoint differs from evidence')
    training_identity(training['config'],a.head)
    families=audited_families(training['config'])
    basepath=Path('runs/ensemble_49618816/manifest.json');base=json.loads(basepath.read_text())
    if base['status']!='complete':raise ValueError('ensemble baseline incomplete')
    config=base['config'].copy();panel=json.loads(Path(config['panel']).read_text())['development']
    if sha(config['panel'])!=config['panel_sha256'] or len(panel)!=48 or len({r['family'] for r in panel})!=48:
        raise ValueError('ensemble panel changed')
    if set(families.values())&{r['family'] for r in panel} or set(families)&{r['query_id'] for r in panel}:
        raise ValueError('training/ensemble overlap')
    cache=(basepath.parent/'embeddings.h5').resolve()
    config.update(checkpoint=head['checkpoint'],checkpoint_sha256=head['checkpoint_sha256'],
        training_manifest=head['training_manifest'],training_manifest_sha256=head['training_manifest_sha256'],
        transfer_screen_manifest=str(path.resolve()),transfer_screen_manifest_sha256=sha(path),
        capacity_report=c['capacity_report'],capacity_report_sha256=c['capacity_report_sha256'],
        embedding_cache=str(cache),embedding_cache_sha256=sha(cache),
        checkpoint_selection=dict(setting=setting,step=step,rule='Complete two-seed larger-data capacity evidence plus this declared seed passing unchanged tuning quality; capacity success reported separately under frozen expansion protocol; no retrospective gate or best-seed substitution',
                                  capacity=capacity['comparisons'][f"{training['config']['seed']}_all64_vs_initial"],transfer=transfer['summaries'][setting]),
        flow_steps=25,flow_solver='euler',flow_time_power=1,primary_guidance=1,guidance_controls=[],work_cap_seconds=780)
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(config,indent=2)+'\n')
    print(json.dumps(config['checkpoint_selection']))


if __name__=='__main__':main()
