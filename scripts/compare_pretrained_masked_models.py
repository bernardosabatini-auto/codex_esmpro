"""Fixed same-refold comparison for the pretrained masked-flow experiment."""
import argparse
import fcntl
import json
from pathlib import Path


def ready_command(root):
    path=root/'runs/pretrained_masked_model_comparison.json';output=root/'reports/pretrained_masked_model_comparison_20261003'
    if not path.exists() or output.with_suffix('.json').exists():return None
    plan=json.loads(path.read_text());jobs=plan['jobs']
    if not plan.get('pretrained_masked_comparison') or set(jobs)!={'generated_null','generated_cond'} or any(len(v)!=4 for v in jobs.values()):raise ValueError('Incomplete masked-flow comparison')
    ids=[i for v in jobs.values() for i in v]
    if any(i is None for i in ids):return None
    registry={r['id']:r for r in json.loads((root/'runs/jobs.json').read_text())['jobs']}
    if len(set(ids))!=8 or any(i not in registry or registry[i]['completion_action']!='summarize_fragment_preference_refold' for i in ids):raise ValueError('Unregistered or duplicated masked-flow refolds')
    if not all((root/f'reports/fragment_preference_refold_{i}.json').exists() and json.loads((root/f'reports/fragment_preference_refold_{i}.json').read_text())['status']=='complete' for i in ids):return None
    if plan.get('diversity_pending'):
        import hashlib
        if not all(Path(p).exists() and json.loads(Path(p).read_text())['status']=='complete' for p in plan['diversity_pending'].values()):return None
        for arm,p in plan.pop('diversity_pending').items():
            with Path(p).open('rb') as f:checksum=hashlib.file_digest(f,'sha256').hexdigest()
            plan.setdefault('diversity',{})[arm]=dict(path=p,sha256=checksum)
        temporary=path.with_suffix('.tmp');temporary.write_text(json.dumps(plan,indent=2)+'\n');temporary.replace(path)
    return [str(root/'scripts/compare_pretrained_masked_models.py'),'--plan',str(path),'--output',str(output)]


def main():
    from compare_native_anchor_models import write_comparison
    p=argparse.ArgumentParser();p.add_argument('--plan',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    with a.output.with_suffix('.lock').open('w') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX);write_comparison(a)


if __name__=='__main__':main()
