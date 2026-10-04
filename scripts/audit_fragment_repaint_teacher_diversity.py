"""Cache all oracle scaffold pair scores before learning any refold outcomes."""
import argparse,json
from pathlib import Path
from fragment_repaint_teacher_core import audit
from compare_native_anchor_models import diversity
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--generation',type=Path,required=True);p.add_argument('--refold-config',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    root=Path(__file__).resolve().parents[1];run=a.generation.resolve();mp=run/'manifest.json';m=json.loads(mp.read_text());c=m['config'];audit(c)
    d=json.loads((root/'reports'/(run.name+'.json')).read_text());rc=json.loads(a.refold_config.read_text())
    if (m['status']!='complete' or d['status']!='complete' or d['controls']!=8 or d.get('oracle_teacher') is not True
            or d['manifest_sha256']!=sha(mp) or d['predictions_sha256']!=sha(run/'predictions.h5')
            or rc['generation_manifest']!=str(mp) or sha(rc['usalign'])!=rc['usalign_sha256']):raise ValueError('Changed oracle source or scorer')
    result=diversity(dict(generation_manifest=str(mp),config=dict(c,prediction_group='new')),[],rc['usalign'])
    for row in result['records']:row.pop('both_strong')
    d=dict(status='complete',manifest_sha256=sha(mp),predictions_sha256=sha(run/'predictions.h5'),scorer_sha256=rc['usalign_sha256'],prediction_group='new',records=result['records'],summary=[r for r in result['summary'] if r['subset']=='all'],scope='All192 raw pairs across32 training proteins. Full-context oracle, no outcome filtering. Lower pairTM alone does not establish useful generative diversity or designability.')
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n');a.output.with_suffix('.md').write_text('# Oracle teacher raw scaffold diversity\n\n'+d['scope']+'\n\n```json\n'+json.dumps(d['summary'],indent=2)+'\n```\n');print(json.dumps(d['summary']))


if __name__=='__main__':main()
