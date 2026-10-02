"""Freeze the compact balanced pipeline after full-panel qualification."""
import argparse,json
from pathlib import Path
from prepare_overfit import sha
from summarize_compact_native import analyze


def validate_reference(config,head):
    if config.get('checkpoint_sha256')!=head['checkpoint_sha256'] or config.get('primary_guidance')!=1 or config.get('flow_steps',25)!=25 or config.get('flow_solver','euler')!='euler' or config.get('flow_time_power',1)!=1 or config.get('compact_condition',False):raise ValueError('incompatible expanded ensemble reference')
    if config.get('checkpoint_selection',{}).get('step')!=500:raise ValueError('expected qualified balanced500 ensemble')


def main():
    p=argparse.ArgumentParser();p.add_argument('--screen',type=Path,required=True);p.add_argument('--reference',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    path=a.screen/'manifest.json';m=json.loads(path.read_text())
    if m['status']!='complete':raise ValueError('compact native screen incomplete')
    result=analyze(m);name='aligned_teacher_balanced'
    if name not in result['qualified_heads']:raise ValueError('balanced compact pipeline did not qualify')
    head=next(h for h in m['config']['heads'] if h['name']==name);reference=a.reference/'manifest.json';base=json.loads(reference.read_text())
    if base['status']!='complete':raise ValueError('reference ensemble incomplete')
    c=base['config'].copy();validate_reference(c,head)
    for key in ('checkpoint','training_manifest','capacity_report','panel'):
        if sha(c[key])!=c[key+'_sha256']:raise ValueError('changed '+key)
    cache=(a.reference/'embeddings.h5').resolve()
    c.update(compact_condition=True,compact_screen_manifest=str(path.resolve()),compact_screen_manifest_sha256=sha(path),compact_reference_manifest=str(reference.resolve()),compact_reference_manifest_sha256=sha(reference),embedding_cache=str(cache),embedding_cache_sha256=sha(cache),guidance_controls=[],work_cap_seconds=780)
    a.output.write_text(json.dumps(c,indent=2)+'\n');print('Qualified balanced500 compact CFG1, fixed48-family panel')


if __name__=='__main__':main()
