"""Prepare archived10-step external sampling only after native retry qualification."""
import argparse,json
from pathlib import Path
from prepare_overfit import sha
from summarize_bounded_retry_native import analyze
from compare_retry_ensembles import validate_source


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1];protocol=root/'configs/reflow_retry_ensemble_protocol.json';recipe=json.loads(protocol.read_text());path=root/recipe['native_run']/'manifest.json';m=json.loads(path.read_text());result=analyze(m)
    if set(result['summaries'])!=set(recipe['heads']) or not all(r['quality_passed'] for r in result['summaries'].values()):raise ValueError('Missing native qualification')
    for name,reused in recipe['reused_controls'].items():
        run=root/reused['run'];old=json.loads((run/'manifest.json').read_text());validate_source(run,old['config'],protocol,recipe,m)
        if old['status']!='complete' or sha(root/reused['scores'])!=reused['scores_sha256']:raise ValueError('Changed reused external evidence')
    head=next(h for h in m['config']['heads'] if h['name']=='reflow10');c={k:v for k,v in old['config'].items() if not k.startswith(('parent_','capacity_report'))}
    selection=json.loads(Path(m['config']['selection']).read_text());rows=json.loads(Path(c['panel']).read_text())['development']
    if {r['family'] for r in selection['train']}&{r['family'] for r in rows} or {r['id'] for r in selection['train']}&{r['query_id'] for r in rows}:raise ValueError('Training/external family overlap')
    c.update(name='reflow10',primary_guidance=1,flow_steps=10,compact_condition=False,native_manifest=str(path),native_manifest_sha256=sha(path),protocol=str(protocol),protocol_sha256=sha(protocol))
    for key in ('checkpoint','training_manifest'):
        if sha(head[key])!=head[key+'_sha256']:raise ValueError('Changed '+key)
        c[key]=head[key];c[key+'_sha256']=head[key+'_sha256']
    a.output.write_text(json.dumps(c,indent=2)+'\n');print(c['name'])

if __name__=='__main__':main()
