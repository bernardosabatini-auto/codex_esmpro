"""Normalize archived short-sampler controls without changing any outcomes."""
import argparse,json,math
from pathlib import Path
from prepare_overfit import sha
from summarize_bounded_retry_native import analyze


def normalized_scores(m,ids):
    if m['status']!='complete' or m['updates']!=2000 or m['config']['arm']!='reflow_paired':raise ValueError('Wrong archived training endpoint')
    rows=[dict(r,head='reflow10',guidance=1) for r in m['scores'] if r['step']==2000 and r['sampling_steps']==10]
    if len(ids)!=64 or len(set(ids))!=64 or len(rows)!=192 or {(r['target_id'],r['sample']) for r in rows}!={(i,k) for i in ids for k in range(3)}:raise ValueError('Incomplete archived controls')
    if any(not math.isfinite(r[k]) or not 0<=r[k]<=1 for r in rows for k in ('ca_lddt','coarse_valid')):raise ValueError('Invalid archived metric')
    return rows


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];protocol=root/'configs/reflow_retry_native_protocol.json';recipe=json.loads(protocol.read_text());prior_path=root/'runs/bounded_retry_native_49843256/manifest.json';prior=json.loads(prior_path.read_text());analyze(prior);c=dict(prior['config'])
    source=root/recipe['source_run']/'manifest.json';old=json.loads(source.read_text());selection=json.loads(Path(c['selection']).read_text());ids=[r['id'] for r in selection['tuning']];scores=normalized_scores(old,ids)
    if any(old['config'][k]!=c[k] for k in ('selection','selection_sha256','embedding_cache','seed','evaluation_seed')):raise ValueError('Archived panel/seed differs')
    train=selection['train'];tuning=selection['tuning']
    if len(train)!=512 or len({r['family'] for r in train})!=512 or {r['family'] for r in train}&{r['family'] for r in tuning}:raise ValueError('Wrong training scope/leakage')
    adapter=dict(status='complete',source_manifest=str(source),source_manifest_sha256=sha(source),normalization='Add head=reflow10/guidance=1; retain all2000-update10-step archived metrics and all64x3 outcomes unchanged',scores=scores)
    destination=root/'runs/reflow_retry_raw_controls.json'
    if destination.exists() and json.loads(destination.read_text())!=adapter:raise ValueError('Archived control adapter changed')
    if not destination.exists():destination.write_text(json.dumps(adapter,indent=2)+'\n')
    heads=[dict(h,sampling_steps=25) for h in c['heads'] if h['name'] in ('original','compact500')];checkpoint=source.parent/'ema_2000.ckpt'
    heads.append(dict(name='reflow10',sampling_steps=10,guidance=1,checkpoint=str(checkpoint),checkpoint_sha256=sha(checkpoint),training_manifest=str(source),training_manifest_sha256=sha(source),raw_manifest=str(destination),raw_manifest_sha256=sha(destination),raw_source_manifest=str(source),raw_source_manifest_sha256=sha(source),raw_head='reflow10'))
    if [h['name'] for h in heads]!=recipe['heads']:raise ValueError('Wrong declared heads')
    c.update(heads=heads,protocol=str(protocol),protocol_sha256=sha(protocol),prior_retry_manifest=str(prior_path),prior_retry_manifest_sha256=sha(prior_path),work_cap_seconds=780)
    a.output.write_text(json.dumps(c,indent=2)+'\n');print(json.dumps(dict(heads=recipe['heads'],archive_rows=len(scores),training_families=len(train))))

if __name__=='__main__':main()
