"""Advance quality-qualified restricted settings with both training seeds retained."""
import argparse,json
from pathlib import Path
from prepare_overfit import sha
from summarize_expanded_native import analyze
from latentfold.teacher_states import audited_families


def qualified(capacity, transfer, head, guidance, *, step=500):
    if guidance!=1 or step not in (500,2000):raise ValueError('invalid sampling or endpoint')
    allowed={f'seed{seed}_tail':str(seed) for seed in (2026100171,2026100181)}
    if head not in allowed:raise ValueError('only declared restricted seed settings qualify')
    if capacity['step']!=step or not capacity['matched'] or capacity['seeds']!=[2026100171,2026100181]:raise ValueError('paired capacity evidence incomplete')
    if 'adaptation_effects' not in transfer:raise ValueError('wrong tuning comparison')
    setting=head+'_cfg1'
    if transfer['step']!=step or not transfer['summaries'][setting]['quality_passed']:raise ValueError('transfer prerequisite failed')
    return setting


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
    if a.head!=f"seed{training['config']['seed']}_tail" or training['config']['label_distribution']!='balanced' or training['config'].get('trainable_tail_blocks')!=4:raise ValueError('head and training identity differ')
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
        checkpoint_selection=dict(setting=setting,step=step,rule='Complete matched two-seed capacity evidence plus this declared tail setting passing tuning quality, as specified by tail122 protocol; no retrospective capacity threshold or best-seed substitution',
                                  capacity=capacity['comparisons'][f"{training['config']['seed']}_tail_all122_vs_initial"],transfer=transfer['summaries'][setting]),
        flow_steps=25,flow_solver='euler',flow_time_power=1,primary_guidance=1,guidance_controls=[],work_cap_seconds=780)
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(config,indent=2)+'\n')
    print(json.dumps(config['checkpoint_selection']))


if __name__=='__main__':main()
