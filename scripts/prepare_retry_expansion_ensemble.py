"""Freeze both larger-data retry ensembles and prove original-control reuse."""
import argparse,json
from pathlib import Path
from prepare_overfit import sha
from summarize_bounded_retry_native import analyze
from latentfold.teacher_states import audited_families


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];protocol=root/'configs/retry_expansion_ensemble_protocol.json';recipe=json.loads(protocol.read_text());path=root/recipe['native_run']/'manifest.json';m=json.loads(path.read_text());result=analyze(m)
    if set(result['summaries'])!=set(recipe['heads']) or not all(r['quality_passed'] for r in result['summaries'].values()):raise ValueError('All declared larger-data heads must qualify')
    control=recipe['reused_controls']['original'];oldpath=root/control['run']/'manifest.json';old=json.loads(oldpath.read_text());base=old['config']
    if sha(oldpath)!=control['manifest_sha256'] or old['status']!='complete' or sha(root/recipe['reuse_protocol'])!=recipe['reuse_protocol_sha256'] or base['protocol_sha256']!=recipe['reuse_protocol_sha256'] or base['native_manifest_sha256']!=m['config']['prior_retry_manifest_sha256']:raise ValueError('Original control reuse is not supported')
    capacity=Path(m['config']['capacity_report']);cap=json.loads(capacity.read_text())
    if sha(capacity)!=m['config']['capacity_report_sha256'] or not cap['replicated_capacity_passed'] or cap['training_targets']!=427 or cap['step']!=2000:raise ValueError('Larger capacity evidence changed')
    rows=json.loads(Path(base['panel']).read_text())['development']
    if sha(base['panel'])!=base['panel_sha256'] or len(rows)!=48 or len({r['family'] for r in rows})!=48:raise ValueError('External panel changed')
    for head in m['config']['heads']:
        if head['name']=='original':continue
        train=json.loads(Path(head['training_manifest']).read_text());families=audited_families(train['config'])
        if len(families)!=427 or set(families.values())&{r['family'] for r in rows} or set(families)&{r['query_id'] for r in rows} or train['config'].get('functional_replay') or train['config']['label_distribution']!='balanced' or head['name']!=f"seed{train['config']['seed']}_expansion" or Path(head['checkpoint']).name!='ema_2000.ckpt':raise ValueError('Wrong larger checkpoint or training overlap')
        c={k:v for k,v in base.items() if not k.startswith('parent_')};c.update(name=head['name'],primary_guidance=1,compact_condition=False,native_manifest=str(path),native_manifest_sha256=sha(path),protocol=str(protocol),protocol_sha256=sha(protocol),capacity_report=str(capacity),capacity_report_sha256=sha(capacity))
        for key in ('checkpoint','training_manifest'):
            if sha(head[key])!=head[key+'_sha256']:raise ValueError('Changed '+key)
            c[key]=head[key];c[key+'_sha256']=head[key+'_sha256']
        output=a.output.with_name(a.output.stem+'_'+head['name']+'.json');output.write_text(json.dumps(c,indent=2)+'\n');print(output)

if __name__=='__main__':main()
