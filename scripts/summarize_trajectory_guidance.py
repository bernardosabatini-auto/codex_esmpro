import argparse,json
from pathlib import Path
from trajectory_guidance_core import analyze


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,nargs=1,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();
    from prepare_overfit import sha
    target=a.output.with_suffix('.json');run=a.runs[0]
    if target.exists() and a.output.with_suffix('.md').exists():
        old=json.loads(target.read_text())
        if old.get('status')=='complete' and old['manifest_sha256']==sha(run/'manifest.json') and old['predictions_sha256']==sha(run/'predictions.h5'):return
    manifest=json.loads((run/'manifest.json').read_text())
    if manifest['status']!='complete':
        d=dict(status=manifest['status'],error=manifest.get('error'),manifest_sha256=sha(run/'manifest.json'),controls=manifest.get('controls',[]),partial_batches=manifest.get('batches',[]),excluded_from_scientific_comparison=True)
    elif manifest['config']['spec'].get('gradient_branch_diagnostic'):
        from gradient_branch_diagnostic import analyze as analyze_diagnostic
        d=analyze_diagnostic(run)
    elif manifest['config']['spec'].get('joint_sequence_guidance'):
        from sequence_guidance_core import analyze as analyze_joint
        d=analyze_joint(run)
    else:d=analyze(run)
    a.output.with_suffix('.json').write_text(json.dumps(d,indent=2)+'\n')
    short={k:v for k,v in d.items() if k not in ('records','controls','sequence_scores')};a.output.with_suffix('.md').write_text('# Mid-flow decoder guidance pilot\n\nTraining-protein diagnostic. No designability claim. All outputs retained.\n\n```json\n'+json.dumps(short,indent=2)+'\n```\n');print(json.dumps(short))

if __name__=='__main__':main()
