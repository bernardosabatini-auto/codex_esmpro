"""Build one fixed checkpoint interpolation per seed and bind its tuning test."""
import argparse,json
from pathlib import Path
import torch
from prepare_overfit import sha
from summarize_expanded_native import analyze
from latentfold.checkpoint_blend import architecture,blend_states


def export_blend(initial_path,trained_path,output,alpha,expected):
    identity_path=Path(str(output)+'.identity.json')
    if output.exists():
        d=json.loads(identity_path.read_text())
        if any(d[k]!=v for k,v in expected.items()) or d['alpha']!=alpha or not d['reload_verified'] or sha(output)!=d['sha256']:raise ValueError('existing blend provenance differs')
        return d
    initial=torch.load(initial_path,map_location='cpu',weights_only=True,mmap=True)
    trained=torch.load(trained_path,map_location='cpu',weights_only=True,mmap=True)
    meta=architecture(initial)
    if meta!=architecture(trained):raise ValueError('blend architectures differ')
    weights=blend_states(initial['ema'],trained['ema'],alpha)
    output.parent.mkdir(parents=True,exist_ok=True);temp=output.with_suffix('.tmp')
    torch.save(dict(meta,ema=weights,blend=dict(expected,alpha=alpha)),temp);temp.replace(output)
    loaded=torch.load(output,map_location='cpu',weights_only=True,mmap=True)
    if architecture(loaded)!=meta or set(loaded['ema'])!=set(weights) or any(not torch.equal(v,loaded['ema'][k]) for k,v in weights.items()):raise ValueError('blend reload differs')
    d=dict(expected,alpha=alpha,path=str(output.resolve()),sha256=sha(output),reload_verified=True,tensors=len(weights),bytes=output.stat().st_size)
    identity_path.write_text(json.dumps(d,indent=2)+'\n');return d


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--screen',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();torch.set_num_threads(1)
    root=Path(__file__).resolve().parents[1];protocol=root/'configs/blend_native_protocol.json';recipe=json.loads(protocol.read_text());alpha=recipe['alpha']
    if alpha!=.5 or recipe['seeds']!=[2026100171,2026100181]:raise ValueError('fixed blend protocol changed')
    path=a.screen/'manifest.json';m=json.loads(path.read_text());c=m['config'];screen=analyze(m)
    if m['status']!='complete' or screen['step']!=2000 or c['training_family_count']!=122:raise ValueError('complete broader2000 screen required')
    if sha(c['capacity_report'])!=c['capacity_report_sha256']:raise ValueError('capacity provenance changed')
    capacity=json.loads(Path(c['capacity_report']).read_text())
    if not capacity['matched'] or not capacity['replicated_capacity_passed']:raise ValueError('source capacity prerequisite failed')
    original=next(h for h in c['heads'] if h['name']=='original');initial=Path(original['checkpoint']);identity=json.loads(Path(str(initial)+'.identity.json').read_text())
    if not identity['tensor_values_verified'] or identity['sha256']!=original['checkpoint_sha256'] or sha(initial)!=identity['sha256'] or identity['source_sha256']!=c['checkpoint_sha256']:raise ValueError('original EMA identity changed')
    heads=[original];preparation=[]
    for seed in recipe['seeds']:
        name=f'seed{seed}_balanced';source=next(h for h in c['heads'] if h['name']==name)
        if screen['summaries'][name+'_cfg1']['quality_passed']:raise ValueError('diagnostic protocol expects unqualified full models')
        for field in ('checkpoint','training_manifest'):
            if sha(source[field])!=source[field+'_sha256']:raise ValueError('changed '+field)
        training=json.loads(Path(source['training_manifest']).read_text());tc=training['config']
        if tc['seed']!=seed or tc['label_distribution']!='balanced' or tc['checkpoint_sha256']!=identity['source_sha256'] or training['updates']!=2000 or Path(source['checkpoint']).name!='ema_2000.ckpt':raise ValueError('source training identity differs')
        target=root/'runs/blend_checkpoints'/f'balanced122_2000_seed{seed}_alpha050.ckpt'
        expected=dict(initial_checkpoint=str(initial.resolve()),initial_checkpoint_sha256=identity['sha256'],trained_checkpoint=source['checkpoint'],trained_checkpoint_sha256=source['checkpoint_sha256'],source_screen=str(path.resolve()),source_screen_sha256=sha(path),protocol=str(protocol),protocol_sha256=sha(protocol))
        blend=export_blend(initial,Path(source['checkpoint']),target,alpha,expected);preparation.append(blend)
        heads.append(dict(source,name=f'seed{seed}_full'))
        bp=Path(str(target)+'.identity.json');heads.append(dict(source,name=f'seed{seed}_blend',checkpoint=str(target.resolve()),checkpoint_sha256=blend['sha256'],blend_manifest=str(bp),blend_manifest_sha256=sha(bp)))
        print('prepared blend',seed,flush=True)
    if [h['name'] for h in heads]!=recipe['heads']:raise ValueError('head order differs')
    c=dict(c,heads=heads,protocol=str(protocol),protocol_sha256=sha(protocol),blend_alpha=alpha,source_native_manifest=str(path.resolve()),source_native_manifest_sha256=sha(path),work_cap_seconds=780)
    a.output.write_text(json.dumps(c,indent=2)+'\n')
    (root/'runs/blend_checkpoints/preparation.json').write_text(json.dumps(preparation,indent=2)+'\n')
    print(a.output)

if __name__=='__main__':main()
