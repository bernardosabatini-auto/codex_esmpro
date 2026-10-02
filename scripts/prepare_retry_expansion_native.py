"""Evaluate larger training breadth under the already fixed retry algorithm."""
import argparse,json
from pathlib import Path
from prepare_overfit import sha
from latentfold.teacher_states import audited_families


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1]
    path=root/'runs/expansion_native_49831486/manifest.json';m=json.loads(path.read_text());base=m['config'];capacity=Path(base['capacity_report']);d=json.loads(capacity.read_text())
    if m['status']!='complete' or sha(capacity)!=base['capacity_report_sha256'] or not d['matched'] or not d['replicated_capacity_passed'] or d['step']!=2000 or d['training_targets']!=427 or d['seeds']!=[2026100171,2026100181]:raise ValueError('Unqualified larger capacity')
    prior=root/'runs/bounded_retry_native_49843256/manifest.json';old=json.loads(prior.read_text());c={k:base[k] for k in ('selection','selection_sha256','embedding_cache','seed','evaluation_seed','capacity_report','capacity_report_sha256')}
    if any(c[k]!=old['config'][k] for k in ('selection_sha256','embedding_cache','seed','evaluation_seed')):raise ValueError('Retry panel changed')
    rows=json.loads(Path(c['selection']).read_text())['tuning'];tuning={r['family'] for r in rows};heads=[]
    for head in base['heads']:
        h=dict(head)
        for key in ('checkpoint','training_manifest'):
            if h.get(key) and sha(h[key])!=h[key+'_sha256']:raise ValueError('Changed '+key)
        if h.get('training_manifest'):
            train=json.loads(Path(h['training_manifest']).read_text());families=audited_families(train['config'])
            if len(families)!=427 or set(families.values())&tuning or train['config']['label_distribution']!='balanced' or train['config'].get('functional_replay') or Path(h['checkpoint']).name!='ema_2000.ckpt':raise ValueError('Wrong training identity or leakage')
        h.update(guidance=2 if h['name']=='original' else 1,raw_head=h['name'],raw_manifest=str(path),raw_manifest_sha256=sha(path));heads.append(h)
    protocol=root/'configs/retry_expansion_native_protocol.json'
    if [h['name'] for h in heads]!=json.loads(protocol.read_text())['heads']:raise ValueError('Missing declared heads')
    c.update(heads=heads,protocol=str(protocol),protocol_sha256=sha(protocol),diagnostic=old['config']['diagnostic'],diagnostic_sha256=old['config']['diagnostic_sha256'],prior_retry_manifest=str(prior),prior_retry_manifest_sha256=sha(prior),work_cap_seconds=780)
    a.output.write_text(json.dumps(c,indent=2)+'\n');print(json.dumps(dict(heads=[h['name'] for h in heads],families=len(rows))))

if __name__=='__main__':main()
