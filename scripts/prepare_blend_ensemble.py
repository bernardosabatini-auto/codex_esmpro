"""Bind a native-qualified fixed checkpoint blend to external state evaluation."""
import argparse,json
from pathlib import Path
from prepare_overfit import sha
from summarize_expanded_native import analyze
from latentfold.teacher_states import audited_families


def qualified(transfer,head,alpha):
    if alpha!=.5 or head not in ('seed2026100171_blend','seed2026100181_blend') or transfer['step']!=2000 or 'blend_effects' not in transfer:raise ValueError('wrong fixed blend scope')
    setting=head+'_cfg1'
    if not transfer['summaries'][setting]['quality_passed']:raise ValueError('blend native quality failed')
    return setting


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--screen',type=Path,required=True);p.add_argument('--head',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    path=a.screen/'manifest.json';m=json.loads(path.read_text());c=m['config']
    if m['status']!='complete':raise ValueError('native screen incomplete')
    transfer=analyze(m);setting=qualified(transfer,a.head,c['blend_alpha']);head=next(h for h in c['heads'] if h['name']==a.head)
    for key in ('checkpoint','training_manifest','blend_manifest'):
        if sha(head[key])!=head[key+'_sha256']:raise ValueError('changed '+key)
    blend=json.loads(Path(head['blend_manifest']).read_text());training=json.loads(Path(head['training_manifest']).read_text());tc=training['config'];seed=tc['seed']
    source=next(h for h in c['heads'] if h['name']==f'seed{seed}_full')
    if (a.head!=f'seed{seed}_blend' or tc['label_distribution']!='balanced' or training['updates']!=2000 or blend['alpha']!=.5
        or blend['sha256']!=head['checkpoint_sha256'] or not blend['reload_verified'] or blend['trained_checkpoint_sha256']!=source['checkpoint_sha256']
        or blend['protocol_sha256']!=c['protocol_sha256'] or sha(blend['source_screen'])!=blend['source_screen_sha256']):raise ValueError('blend lineage differs')
    if sha(c['capacity_report'])!=c['capacity_report_sha256']:raise ValueError('source capacity evidence changed')
    families=audited_families(tc);basepath=Path('runs/ensemble_49618816/manifest.json');base=json.loads(basepath.read_text())
    if base['status']!='complete':raise ValueError('ensemble baseline incomplete')
    config=base['config'].copy();panel=json.loads(Path(config['panel']).read_text())['development']
    if sha(config['panel'])!=config['panel_sha256'] or len(panel)!=48 or len({r['family'] for r in panel})!=48:raise ValueError('ensemble panel changed')
    if set(families.values())&{r['family'] for r in panel} or set(families)&{r['query_id'] for r in panel}:raise ValueError('training/ensemble overlap')
    cache=(basepath.parent/'embeddings.h5').resolve()
    config.update(checkpoint=head['checkpoint'],checkpoint_sha256=head['checkpoint_sha256'],training_manifest=head['training_manifest'],training_manifest_sha256=head['training_manifest_sha256'],blend_manifest=head['blend_manifest'],blend_manifest_sha256=head['blend_manifest_sha256'],transfer_screen_manifest=str(path.resolve()),transfer_screen_manifest_sha256=sha(path),capacity_report=c['capacity_report'],capacity_report_sha256=c['capacity_report_sha256'],embedding_cache=str(cache),embedding_cache_sha256=sha(cache),checkpoint_selection=dict(setting=setting,step=2000,alpha=.5,rule='Fixed blend native qualification; source full-weight capacity does not certify the blended model',blended_capacity_qualified=False,transfer=transfer['summaries'][setting]),flow_steps=25,flow_solver='euler',flow_time_power=1,primary_guidance=1,guidance_controls=[],work_cap_seconds=780)
    a.output.write_text(json.dumps(config,indent=2)+'\n');print(setting)

if __name__=='__main__':main()
