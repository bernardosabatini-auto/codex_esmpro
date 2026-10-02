"""Freeze external retry runs from the matched native-qualified heads."""
import argparse,json
from pathlib import Path
from prepare_overfit import sha
from summarize_bounded_retry_native import analyze
from latentfold.teacher_states import audited_families


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1]
    protocol=root/'configs/retry_ensemble_protocol.json';recipe=json.loads(protocol.read_text());path=root/recipe['native_run']/'manifest.json';m=json.loads(path.read_text());native=analyze(m)
    if set(native['summaries'])!=set(recipe['heads']) or not all(r['quality_passed'] for r in native['summaries'].values()):raise ValueError('All declared matched native heads must qualify')
    capacity=root/'reports/expanded_comparison_2000.json';cap=json.loads(capacity.read_text())
    if cap['step']!=2000 or not cap['matched'] or not cap['replicated_capacity_passed'] or cap['seeds']!=[2026100171,2026100181]:raise ValueError('Paired broader capacity missing')
    basepath=root/'runs/ensemble_49618816/manifest.json';base=json.loads(basepath.read_text());panel=Path(base['config']['panel']);rows=json.loads(panel.read_text())['development']
    if base['status']!='complete' or sha(panel)!=base['config']['panel_sha256'] or len(rows)!=48 or len({r['family'] for r in rows})!=48:raise ValueError('Frozen external panel changed')
    fields=dict(protocol=protocol,panel=panel,native_manifest=path,capacity_report=capacity,embedding_cache=basepath.parent/'embeddings.h5',decoder_checkpoint=Path(base['decoder_checkpoint']['path']))
    common={}
    for key,value in fields.items():common[key]=str(value.resolve());common[key+'_sha256']=sha(value)
    if common['decoder_checkpoint_sha256']!=base['decoder_checkpoint']['sha256']:raise ValueError('Decoder changed')
    for name in recipe['heads']:
        head=next(h for h in m['config']['heads'] if h['name']==name)
        c=dict(common,name=name,samples=32,max_attempts=4,noise_arms=['raw','latent'],primary_guidance=head['guidance'],guidance_controls=[],seed=base['config']['seed'],flow_steps=25,flow_solver='euler',flow_time_power=1,compact_condition=name=='compact500',work_cap_seconds=780)
        for key in ('checkpoint','training_manifest'):
            if head.get(key):
                if sha(head[key])!=head[key+'_sha256']:raise ValueError('Changed '+key)
                c[key]=head[key];c[key+'_sha256']=head[key+'_sha256']
        if c.get('training_manifest'):
            train=json.loads(Path(c['training_manifest']).read_text());families=audited_families(train['config'])
            if set(families.values())&{r['family'] for r in rows} or set(families)&{r['query_id'] for r in rows}:raise ValueError('Training/external overlap')
            if name.startswith('seed') and (train['config']['seed'] not in (2026100171,2026100181) or train['config']['label_distribution']!='balanced' or len(families)!=122 or Path(c['checkpoint']).name!='ema_2000.ckpt'):raise ValueError('Wrong broader checkpoint')
        if name in ('original','compact500'):
            jid='49618816' if name=='original' else '49771176';parent=root/f'runs/ensemble_{jid}/manifest.json';pm=json.loads(parent.read_text());scores=root/f'runs/state_scores_{jid}/score.json'
            if pm['status']!='complete' or pm['config']['panel_sha256']!=c['panel_sha256'] or pm['config']['seed']!=c['seed'] or json.loads(scores.read_text())['status']!='complete':raise ValueError('Historical external parent changed')
            for key,value in dict(parent_manifest=parent,parent_predictions=parent.parent/'predictions.h5',parent_scores=scores).items():c[key]=str(value);c[key+'_sha256']=sha(value)
        output=a.output.with_name(a.output.stem+'_'+name+'.json');output.write_text(json.dumps(c,indent=2)+'\n');print(output)

if __name__=='__main__':main()
