"""Cache all unfiltered scaffold pairs while the matched refolds run."""
import argparse
import json
from pathlib import Path
from compare_native_anchor_models import diversity
from pretrained_masked_refolding import qualify_training
from prepare_fragment_preference_refold import audit_inputs
from prepare_overfit import sha


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--generation',type=Path,required=True)
    p.add_argument('--baseline-run',type=Path,required=True)
    p.add_argument('--arm',choices=('generated_cond','generated_untrained'),required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();root=Path(__file__).resolve().parents[1]
    mp=a.generation/'manifest.json';m=json.loads(mp.read_text());c=m['config']
    report=root/'reports'/(a.generation.name+'.json');d=json.loads(report.read_text())
    qualify_training(c,d,'fragment_inpainting')
    if (m['status']!='complete' or d['manifest_sha256']!=sha(mp)
            or d['predictions_sha256']!=sha(a.generation/'predictions.h5')):
        raise ValueError('Unbound complete inpainting predictions')
    parent=json.loads((a.baseline_run/'manifest.json').read_text())['config'];audit_inputs(parent)
    if parent['generation_manifest']!=c['baseline_manifest']:raise ValueError('Different original parent')
    config=dict(c,prediction_group=a.arm)
    scores=diversity(dict(generation_manifest=str(mp),config=config),[],parent['usalign'])
    records=[{k:v for k,v in r.items() if k!='both_strong'} for r in scores['records']]
    result=dict(status='complete',manifest_sha256=sha(mp),predictions_sha256=d['predictions_sha256'],
                scorer_sha256=sha(parent['usalign']),prediction_group=a.arm,records=records,
                summary=[r for r in scores['summary'] if r['subset']=='all'],
                scope='All192 unfiltered training-panel pairs. No success labels used. The final comparison joins strict same-refold outcomes before judging useful diversity.')
    a.output.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
    visible={k:v for k,v in result.items() if k!='records'}
    a.output.with_suffix('.md').write_text('# Coordinate-inpainting scaffold diversity\n\n```json\n'+json.dumps(visible,indent=2)+'\n```\n')
    print(json.dumps(result['summary']))


if __name__=='__main__':main()
