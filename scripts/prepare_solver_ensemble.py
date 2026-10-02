"""Choose the predeclared cheapest quality-qualified solver for ensemble testing."""
import argparse,json,subprocess,sys,tempfile
from pathlib import Path
from prepare_overfit import sha


def choose(summaries):
    eligible=[(name,r) for name,r in summaries.items() if name!='euler_25_cfg2' and r['passed'] and r['network_forwards']<50]
    if not eligible:raise ValueError('no cheaper solver passed the reference quality screen')
    # Python sorting preserves protocol order for any remaining ties.
    return min(eligible,key=lambda item:(item[1]['network_forwards'],item[1]['solver']!='euler',item[1].get('time_power',1)!=1))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--screen',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    path=a.screen/'manifest.json';m=json.loads(path.read_text());c=m['config']
    if m['status']!='complete' or sha(c['baseline_manifest'])!=c['baseline_manifest_sha256']:raise ValueError('screen or baseline incomplete/changed')
    # Regenerate into temporary files rather than trusting or overwriting a report
    # that may already be hash-bound by another experiment.
    with tempfile.TemporaryDirectory() as tmp:
        output=Path(tmp)/'quality'
        subprocess.run([sys.executable,str(Path(__file__).with_name('summarize_midpoint.py')),'--runs',str(a.screen),'--output',str(output)],check=True)
        result=json.loads(output.with_suffix('.json').read_text())
    if result['status']!='complete':raise ValueError('incomplete quality analysis')
    name,setting=choose(result['summaries']);prior=json.loads(Path(c['baseline_manifest']).read_text())
    checkpoint=Path(prior['checkpoint']['path'])
    if prior['checkpoint']['sha256']!=m['checkpoint_sha256'] or sha(checkpoint)!=m['checkpoint_sha256']:raise ValueError('screen checkpoint changed')
    baseline=Path('runs/ensemble_49618816/manifest.json');base=json.loads(baseline.read_text())
    if base['status']!='complete' or base['checkpoint']['sha256']!=m['checkpoint_sha256']:raise ValueError('incompatible ensemble baseline')
    checkpoint_hash=m['checkpoint_sha256']
    if c.get('inference_checkpoint'):
        identity=c['inference_checkpoint'];checkpoint=Path(identity['path']);checkpoint_hash=identity['sha256']
        if identity['source_sha256']!=m['checkpoint_sha256'] or not identity['tensor_values_verified'] or sha(checkpoint)!=checkpoint_hash:raise ValueError('inference checkpoint changed')
    config=base['config'].copy();cache=(baseline.parent/'embeddings.h5').resolve()
    config.update(checkpoint=str(checkpoint.resolve()),checkpoint_sha256=checkpoint_hash,solver_origin_checkpoint_sha256=m['checkpoint_sha256'],embedding_cache=str(cache),embedding_cache_sha256=sha(cache),solver_screen_manifest=str(path.resolve()),solver_screen_manifest_sha256=sha(path),solver_selection=dict(setting=name,rule='Fewest network forwards among quality-qualified cheaper settings; ties prefer Euler and uniform grid, then protocol order',quality_screen=setting),flow_solver=setting['solver'],flow_time_power=setting.get('time_power',1),flow_steps=setting['steps'],primary_guidance=setting['guidance'],guidance_controls=[],work_cap_seconds=1080)
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(config,indent=2)+'\n');print(json.dumps(config['solver_selection']))


if __name__=='__main__':main()
