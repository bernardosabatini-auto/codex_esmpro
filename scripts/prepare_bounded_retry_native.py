"""Freeze historical raw controls and four heads for a separate retry pipeline."""
import argparse,json
from pathlib import Path
from prepare_overfit import sha
from latentfold.teacher_states import audited_families


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    root=Path(__file__).resolve().parents[1]
    protocol=root/'configs/bounded_retry_native_protocol.json'
    diagnostic=root/'reports/bounded_retry_20261002.json'
    if not json.loads(diagnostic.read_text())['feasibility_passed']:raise ValueError('CPU feasibility failed')
    broad_path=root/'runs/expanded_native_49782951/manifest.json'
    small_path=root/'runs/overfit_native_49736749/manifest.json'
    broad=json.loads(broad_path.read_text());small=json.loads(small_path.read_text())
    if broad['status']!='complete' or small['status']!='complete':raise ValueError('Incomplete historical native runs')
    base=broad['config'];c={k:base[k] for k in ('selection','selection_sha256','embedding_cache','seed','evaluation_seed')}
    if any(small['config'][k]!=v for k,v in c.items()):raise ValueError('Historical native panels differ')
    rows=json.loads(Path(c['selection']).read_text())['tuning'];tuning={r['family'] for r in rows}
    heads=[]
    for name,old_name,m,path,guidance in [('original','original',broad,broad_path,2),('compact500','aligned_teacher_balanced',small,small_path,1)]+[(f'seed{s}_balanced',f'seed{s}_balanced',broad,broad_path,1) for s in (2026100171,2026100181)]:
        h=dict(next(x for x in m['config']['heads'] if x['name']==old_name))
        for key in ('checkpoint','training_manifest'):
            if h.get(key) and sha(h[key])!=h[key+'_sha256']:raise ValueError('Changed historical '+key)
        if h.get('training_manifest'):
            families=audited_families(json.loads(Path(h['training_manifest']).read_text())['config'])
            if set(families.values())&tuning:raise ValueError('Training/tuning overlap')
        raw=[r for r in m['scores'] if r['head']==old_name and r['guidance']==guidance]
        if len(raw)!=192:raise ValueError('Incomplete raw controls')
        h.update(name=name,guidance=guidance,raw_head=old_name,raw_manifest=str(path),raw_manifest_sha256=sha(path))
        heads.append(h)
    if [h['name'] for h in heads]!=json.loads(protocol.read_text())['heads']:raise ValueError('Wrong heads')
    c.update(heads=heads,protocol=str(protocol),protocol_sha256=sha(protocol),diagnostic=str(diagnostic),diagnostic_sha256=sha(diagnostic),work_cap_seconds=780)
    a.output.write_text(json.dumps(c,indent=2)+'\n')
    print(json.dumps(dict(heads=[h['name'] for h in heads],families=len(rows))))

if __name__=='__main__':main()
