"""Cache every raw scaffold pair before inspecting designability outcomes."""
import argparse,json
from pathlib import Path
from compare_native_anchor_models import diversity
from retrieved_context_profile import audit
from context_flow_generation import audit_worker
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--generation',type=Path,required=True);p.add_argument('--output-prefix',type=Path,required=True);a=p.parse_args()
    root=Path(__file__).resolve().parents[1];run=a.generation.resolve();mp=run/'manifest.json';m=json.loads(mp.read_text());c=m['config'];audit(c)
    d=json.loads((root/'reports'/(run.name+'.json')).read_text())
    if m['status']!='complete' or not d.get('full_panel') or d['manifest_sha256']!=sha(mp) or d['predictions_sha256']!=sha(run/'predictions.h5'):
        raise ValueError('Changed complete full-panel generation')
    for arm in ('retrieved','random'):
        rc=json.loads((root/f'runs/context_{arm}_refold_20261009_0.json').read_text());audit_worker(rc)
        if rc['generation_manifest']!=str(mp) or sha(rc['usalign'])!=rc['usalign_sha256']:raise ValueError('Wrong generation or scorer')
        result=diversity(dict(generation_manifest=str(mp),config=dict(c,prediction_group=arm)),[],rc['usalign'])
        for r in result['records']:r.pop('both_strong')
        result.update(status='complete',manifest_sha256=sha(mp),predictions_sha256=d['predictions_sha256'],scorer_sha256=rc['usalign_sha256'],prediction_group=arm,
            scope='All192 raw pairs,32 training queries,unfiltered. Both donor identity and flow noise differ across slots; this is not within-code noise diversity. Useful diversity additionally requires strict success in both samples.')
        result['summary']=[r for r in result['summary'] if r['subset']=='all']
        path=Path(str(a.output_prefix)+'_'+arm)
        path.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
        path.with_suffix('.md').write_text('# Retrieved context raw diversity: '+arm+'\n\n'+result['scope']+'\n\n```json\n'+json.dumps(result['summary'],indent=2)+'\n```\n')
        print(arm,result['summary'][0],flush=True)


if __name__=='__main__':main()
